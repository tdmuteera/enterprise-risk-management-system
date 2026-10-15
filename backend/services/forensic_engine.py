"""
Forensic anomaly detection engine.

Detects suspicious patterns in risk management:
  - Chronic unresolved risks (possible negligence)
  - Score suppression near reporting deadlines
  - Sudden risk closure without mitigation
  - Repeated identical risks (padding)
  - Emerging risk chains requiring escalation
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, Float
from sqlalchemy.orm import selectinload

from models.risk import (
    Risk,
    RiskHistory,
    RiskLink,
    MitigationAction,
    Alert,
    RiskStatus,
    MitigationStatus,
)
from models.alert import AlertType, AlertSeverity, AlertRole
from utils.risk_scorer import normalise_score


# ============================================================================
# DETECTOR 1: CHRONIC UNRESOLVED RISKS
# ============================================================================


async def detect_chronic_unresolved_risks(
    db: AsyncSession,
    days_threshold: int = 90,
) -> List[Dict[str, Any]]:
    """
    Detect risks that are unresolved for 90+ days.

    Rule:
      - Status is Open or In-Progress
      - No completed MitigationAction
      - Score >= 40 (High or Critical)
      - Unchanged for >= 90 days

    Flags: "Chronic Unresolved Risk — possible negligence or avoidance"

    Args:
        db: SQLAlchemy async session
        days_threshold: Days of no change (default 90)

    Returns:
        List of findings with keys: risk_id, title, score, days_unresolved, flag
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)

    # Subquery: Get latest change date for each risk
    latest_change = (
        select(
            RiskHistory.risk_id,
            func.max(RiskHistory.changed_at).label("latest_change_at"),
        )
        .group_by(RiskHistory.risk_id)
        .subquery()
    )

    # Find risks
    stmt = (
        select(
            Risk,
            func.coalesce(
                latest_change.c.latest_change_at,
                Risk.updated_at,
                Risk.created_at,
            ).label("last_change_at"),
        )
        .outerjoin(latest_change, Risk.id == latest_change.c.risk_id)
        .where(
            and_(
                Risk.status.in_([RiskStatus.OPEN, RiskStatus.IN_PROGRESS]),
                func.coalesce(
                    latest_change.c.latest_change_at,
                    Risk.updated_at,
                    Risk.created_at,
                )
                <= cutoff_date,
                Risk.risk_score >= 250.0,  # 250/6.25 = 40.0 normalised
                # No completed mitigation actions
                ~Risk.id.in_(
                    select(MitigationAction.risk_id)
                    .where(MitigationAction.status == MitigationStatus.COMPLETED)
                    .distinct()
                ),
            )
        )
        .options(selectinload(Risk.department))
    )

    result = await db.execute(stmt)
    rows = result.unique().all()

    findings: List[Dict[str, Any]] = []
    now = datetime.utcnow()

    for risk, last_change_at in rows:
        days_since_change = (now - last_change_at).days if last_change_at else None

        findings.append(
            {
                "risk_id": str(risk.id),
                "title": risk.title,
                "department": risk.department.name if risk.department else "Unknown",
                "score": normalise_score(risk.risk_score),
                "status": str(risk.status),
                "days_unresolved": days_since_change,
                "flag": "Chronic Unresolved Risk — possible negligence or avoidance",
            }
        )

    return findings


# ============================================================================
# DETECTOR 2: SCORE SUPPRESSION
# ============================================================================


async def detect_score_suppression(db: AsyncSession) -> List[Dict[str, Any]]:
    """Detect score drops of >=30% near month-end / quarter-end without mitigation.

    Rule:
      - Score dropped by >= 30%
      - Drop event occurs within 7 days of a month-end or quarter-end deadline
      - No MitigationAction marked Completed in the same window

    Flags: "Possible Risk Score Suppression — score reduced near reporting deadline without mitigation"
    """

    def _month_end(d: datetime) -> datetime:
        if d.month == 12:
            first_next = datetime(d.year + 1, 1, 1)
        else:
            first_next = datetime(d.year, d.month + 1, 1)
        return first_next - timedelta(days=1)

    def _quarter_end(d: datetime) -> datetime:
        q = ((d.month - 1) // 3) + 1
        end_month = q * 3
        if end_month == 12:
            first_next = datetime(d.year + 1, 1, 1)
        else:
            first_next = datetime(d.year, end_month + 1, 1)
        return first_next - timedelta(days=1)

    def _near_reporting_deadline(d: datetime, window_days: int = 7) -> bool:
        month_end = _month_end(d)
        quarter_end = _quarter_end(d)
        return (
            abs((d.date() - month_end.date()).days) <= window_days
            or abs((d.date() - quarter_end.date()).days) <= window_days
        )

    findings: List[Dict[str, Any]] = []

    risks_result = await db.execute(select(Risk))
    risks = risks_result.scalars().all()

    for risk in risks:
        history_result = await db.execute(
            select(RiskHistory)
            .where(RiskHistory.risk_id == risk.id)
            .where(RiskHistory.action == "score_changed")
            .order_by(RiskHistory.changed_at)
        )
        history = history_result.scalars().all()
        if len(history) < 2:
            continue

        for i in range(len(history) - 1):
            old_entry = history[i]
            new_entry = history[i + 1]

            old_score = (old_entry.new_values or {}).get("risk_score")
            if old_score is None:
                old_score = (old_entry.previous_values or {}).get("risk_score")

            new_score = (new_entry.new_values or {}).get("risk_score")
            if new_score is None:
                new_score = (new_entry.previous_values or {}).get("risk_score")

            if not isinstance(old_score, (int, float)) or not isinstance(new_score, (int, float)):
                continue
            if old_score <= 0:
                continue

            drop_percent = ((old_score - new_score) / old_score) * 100
            if drop_percent < 30:
                continue

            if not _near_reporting_deadline(new_entry.changed_at, window_days=7):
                continue

            window_start = max(old_entry.changed_at, new_entry.changed_at - timedelta(days=7))
            window_end = new_entry.changed_at

            mitigation_result = await db.execute(
                select(MitigationAction.id)
                .where(MitigationAction.risk_id == risk.id)
                .where(MitigationAction.status == MitigationStatus.COMPLETED)
                .where(MitigationAction.completion_date >= window_start)
                .where(MitigationAction.completion_date <= window_end)
                .limit(1)
            )
            if mitigation_result.scalar_one_or_none() is not None:
                continue

            findings.append(
                {
                    "risk_id": str(risk.id),
                    "title": risk.title,
                    "old_score": normalise_score(float(old_score)),
                    "new_score": normalise_score(float(new_score)),
                    "drop_percent": round(drop_percent, 1),
                    "change_date": new_entry.changed_at.isoformat(),
                    "flag": "Possible Risk Score Suppression — score reduced near reporting deadline without mitigation",
                }
            )

    return findings


# ============================================================================
# DETECTOR 3: SUDDEN RISK DISAPPEARANCE
# ============================================================================


async def detect_sudden_risk_disappearance(db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Detect Critical risks deleted or closed within 72 hours without mitigation.

    Rule:
      - Risk was Critical (score >= 65 normalised = 406.25 raw)
      - Status changed to Closed or deleted within 72 hours
      - No completed MitigationAction

    Flags: "Suspicious Risk Closure — Critical risk closed without documented mitigation"

    Returns:
        List of findings with keys: risk_id, title, old_status, new_status, flag
    """
    cutoff_date = datetime.utcnow() - timedelta(hours=72)

    findings = []

    # Look for closure/deletion events in the last 72 hours
    events_stmt = (
        select(RiskHistory)
        .where(RiskHistory.changed_at >= cutoff_date)
        .where(RiskHistory.action.in_(["deleted", "status_changed"]))
        .order_by(desc(RiskHistory.changed_at))
    )
    events_result = await db.execute(events_stmt)
    events = events_result.scalars().all()

    for ev in events:
        # status_changed must explicitly move to Closed; deleted is always suspicious candidate
        new_status = (ev.new_values or {}).get("status")
        if ev.action == "status_changed" and new_status != "Closed":
            continue

        # Cross-check: no completed mitigation exists
        mitigation_stmt = (
            select(MitigationAction.id)
            .where(MitigationAction.risk_id == ev.risk_id)
            .where(MitigationAction.status == MitigationStatus.COMPLETED)
            .limit(1)
        )
        mitigation_result = await db.execute(mitigation_stmt)
        if mitigation_result.scalar_one_or_none() is not None:
            continue

        # Was the risk Critical (>= 65 normalised) within 72h before the event?
        score_cutoff = ev.changed_at - timedelta(hours=72)
        critical_score_stmt = (
            select(func.max(func.json_extract(RiskHistory.new_values, "$.risk_score").cast(Float)))
            .where(RiskHistory.risk_id == ev.risk_id)
            .where(RiskHistory.action == "score_changed")
            .where(RiskHistory.changed_at >= score_cutoff)
            .where(RiskHistory.changed_at <= ev.changed_at)
        )
        score_result = await db.execute(critical_score_stmt)
        max_score = score_result.scalar_one_or_none() or 0.0

        if max_score >= 406.25:
            # Fetch risk title if still present
            risk_stmt = select(Risk).where(Risk.id == ev.risk_id)
            risk_result = await db.execute(risk_stmt)
            risk = risk_result.scalar_one_or_none()

            findings.append(
                {
                    "risk_id": str(ev.risk_id),
                    "title": risk.title if risk else "(deleted risk)",
                    "old_score": normalise_score(max_score),
                    "event": ev.action,
                    "event_time": ev.changed_at.isoformat(),
                    "flag": "Suspicious Risk Closure — Critical risk closed without documented mitigation",
                }
            )

    return findings


# ============================================================================
# DETECTOR 4: REPEATED SAME RISK
# ============================================================================


async def detect_repeated_same_risk(
    db: AsyncSession,
    similarity_threshold: float = 0.8,
) -> List[Dict[str, Any]]:
    """
    Detect 3+ similar risks in same department (possible register padding).

    Rule:
      - Same department, same category
      - Similar titles (token overlap >= threshold)
      - Never resolved

    Flags: "Risk Register Padding — repeated risks without mitigation progress"

    Args:
        db: SQLAlchemy async session
        similarity_threshold: Token overlap ratio (0-1)

    Returns:
        List of findings with keys: department, risks, flag
    """
    findings = []

    # Group by department
    dept_stmt = select(Risk.department_id).distinct()
    dept_result = await db.execute(dept_stmt)
    departments = dept_result.scalars().all()

    def token_overlap(title1: str, title2: str) -> float:
        """Compute simple token overlap similarity."""
        tokens1 = set(title1.lower().split())
        tokens2 = set(title2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    for dept_id in departments:
        # Get all unresolved risks in this department
        risks_stmt = (
            select(Risk)
            .where(Risk.department_id == dept_id)
            .where(Risk.status.in_([RiskStatus.OPEN, RiskStatus.IN_PROGRESS]))
        )
        risks_result = await db.execute(risks_stmt)
        risks = risks_result.scalars().all()

        # Group by category and find similar titles
        by_category: Dict[str, List[Risk]] = {}
        for risk in risks:
            if risk.category not in by_category:
                by_category[risk.category] = []
            by_category[risk.category].append(risk)

        # Find groups of 3+ similar risks
        for category, cat_risks in by_category.items():
            if len(cat_risks) < 3:
                continue

            # Cluster similar titles
            clusters: List[List[Risk]] = []
            used: Set[UUID] = set()

            for i, risk1 in enumerate(cat_risks):
                if risk1.id in used:
                    continue

                cluster = [risk1]
                used.add(risk1.id)

                for risk2 in cat_risks[i + 1 :]:
                    if risk2.id in used:
                        continue

                    if token_overlap(risk1.title, risk2.title) >= similarity_threshold:
                        cluster.append(risk2)
                        used.add(risk2.id)

                if len(cluster) >= 3:
                    clusters.append(cluster)

            # Report clusters
            for cluster in clusters:
                findings.append(
                    {
                        "department_id": str(dept_id),
                        "category": category,
                        "similar_risks": [
                            {
                                "id": str(r.id),
                                "title": r.title,
                                "score": normalise_score(r.risk_score),
                            }
                            for r in cluster
                        ],
                        "count": len(cluster),
                        "flag": "Risk Register Padding — repeated risks without mitigation progress",
                    }
                )

    return findings


# ============================================================================
# DETECTOR 5: EMERGING RISK CHAINS
# ============================================================================


async def detect_emerging_risk_chains(db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Detect 3+ linked risks across different departments escalated in 30 days.

    Rule:
      - 3+ linked risks (connected in RiskLink)
      - Across different departments
      - All escalated (score increase) in past 30 days

    Flags: "Emerging Institutional Risk Chain — requires executive escalation"

    Returns:
        List of findings with keys: risk_chain, departments, flag
    """
    findings = []
    cutoff_date = datetime.utcnow() - timedelta(days=30)

    # Get all risks with score increases in past 30 days
    escalated_stmt = (
        select(RiskHistory.risk_id)
        .where(RiskHistory.action == "score_changed")
        .where(RiskHistory.changed_at >= cutoff_date)
        .where(
            func.json_extract(RiskHistory.new_values, "$.risk_score").cast(Float)
            > func.json_extract(RiskHistory.previous_values, "$.risk_score").cast(Float)
        )
        .distinct()
    )
    escalated_result = await db.execute(escalated_stmt)
    escalated_ids = set(escalated_result.scalars().all())

    if not escalated_ids:
        return findings

    # Get links between escalated risks
    links_stmt = (
        select(RiskLink)
        .where(
            or_(
                RiskLink.source_risk_id.in_(escalated_ids),
                RiskLink.target_risk_id.in_(escalated_ids),
            )
        )
        .options(
            selectinload(RiskLink.source_risk).selectinload(Risk.department),
            selectinload(RiskLink.target_risk).selectinload(Risk.department),
        )
    )
    links_result = await db.execute(links_stmt)
    links = links_result.unique().scalars().all()

    # Build graph and find chains
    graph: Dict[UUID, List[UUID]] = {}
    for link in links:
        if link.source_risk_id not in graph:
            graph[link.source_risk_id] = []
        if link.target_risk_id not in graph:
            graph[link.target_risk_id] = []

        graph[link.source_risk_id].append(link.target_risk_id)
        graph[link.target_risk_id].append(link.source_risk_id)

    # DFS to find connected components with 3+
    visited: Set[UUID] = set()

    def dfs(node: UUID, component: List[UUID]) -> None:
        visited.add(node)
        component.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, component)

    for risk_id in escalated_ids:
        if risk_id in visited:
            continue

        component: List[UUID] = []
        dfs(risk_id, component)

        if len(component) >= 3:
            # Get department info
            risks_stmt = select(Risk).where(Risk.id.in_(component)).options(selectinload(Risk.department))
            risks_result = await db.execute(risks_stmt)
            chain_risks = risks_result.unique().scalars().all()

            departments = set()
            for risk in chain_risks:
                if risk.department:
                    departments.add(risk.department.name)

            findings.append(
                {
                    "chain_size": len(component),
                    "departments_affected": list(departments),
                    "risks": [
                        {
                            "id": str(r.id),
                            "title": r.title,
                            "score": normalise_score(r.risk_score),
                        }
                        for r in chain_risks
                    ],
                    "flag": "Emerging Institutional Risk Chain — requires executive escalation",
                }
            )

    return findings


# ============================================================================
# ORCHESTRATOR
# ============================================================================


async def run_forensic_scan(db: AsyncSession) -> List[Alert]:
    """
    Run all forensic detectors and create alerts.

    Pipeline:
      1. Run all 5 detectors
      2. For each finding, create Alert record
      3. Deduplicate: skip if alert exists in past 48h
      4. Commit and return created alerts

    Returns:
        List of newly created Alert records

    Note:
        This is typically called by APScheduler every 6 hours.
    """
    created_alerts: List[Alert] = []

    # Run all detectors
    chronic_risks = await detect_chronic_unresolved_risks(db)
    score_suppressions = await detect_score_suppression(db)
    disappearances = await detect_sudden_risk_disappearance(db)
    repeated_risks = await detect_repeated_same_risk(db)
    emerging_chains = await detect_emerging_risk_chains(db)

    # Process chronic unresolved risks
    for finding in chronic_risks:
        alert = await _create_alert_if_new(
            db,
            risk_id=UUID(finding["risk_id"]),
            alert_type=AlertType.FORENSIC_FLAG,
            message=f"FORENSIC: {finding['flag']} - {finding['title']} "
            f"({finding['days_unresolved']} days, score {finding['score']})",
            severity=AlertSeverity.WARNING,
        )
        if alert:
            created_alerts.append(alert)

    # Process score suppressions
    for finding in score_suppressions:
        alert = await _create_alert_if_new(
            db,
            risk_id=UUID(finding["risk_id"]),
            alert_type=AlertType.RISK_SUPPRESSION,
            message=f"FORENSIC: {finding['flag']} - {finding['title']} "
            f"({finding['old_score']} -> {finding['new_score']}, {finding['drop_percent']}% drop)",
            severity=AlertSeverity.CRITICAL,
        )
        if alert:
            created_alerts.append(alert)

    # Process disappearances
    for finding in disappearances:
        alert = await _create_alert_if_new(
            db,
            risk_id=UUID(finding["risk_id"]),
            alert_type=AlertType.FORENSIC_FLAG,
            message=f"FORENSIC: {finding['flag']} - {finding['title']} "
            f"(was Critical: {finding['old_score']})",
            severity=AlertSeverity.CRITICAL,
        )
        if alert:
            created_alerts.append(alert)

    # Process repeated risks
    for finding in repeated_risks:
        # Create one alert per group
        alert = await _create_alert_if_new(
            db,
            risk_id=None,
            alert_type=AlertType.FORENSIC_FLAG,
            message=f"FORENSIC: {finding['flag']} - {finding['count']} similar risks "
            f"in category {finding['category']}",
            severity=AlertSeverity.WARNING,
        )
        if alert:
            created_alerts.append(alert)

    # Process emerging chains
    for finding in emerging_chains:
        alert = await _create_alert_if_new(
            db,
            risk_id=None,
            alert_type=AlertType.RISK_CHAIN_DETECTED,
            message=f"FORENSIC: {finding['flag']} - {finding['chain_size']} linked risks "
            f"escalated across {len(finding['departments_affected'])} departments",
            severity=AlertSeverity.CRITICAL,
        )
        if alert:
            created_alerts.append(alert)

    # Commit all new alerts
    if created_alerts:
        await db.commit()

    return created_alerts


async def _create_alert_if_new(
    db: AsyncSession,
    alert_type: AlertType,
    message: str,
    severity: AlertSeverity,
    risk_id: Optional[UUID] = None,
) -> Optional[Alert]:
    """
    Create alert only if no similar alert exists in past 48 hours.

    Used by run_forensic_scan to deduplicate.
    """
    cutoff_date = datetime.utcnow() - timedelta(hours=48)

    # Check for existing alert
    existing_stmt = (
        select(Alert)
        .where(
            and_(
                Alert.alert_type == alert_type,
                Alert.created_at >= cutoff_date,
            )
        )
    )

    if risk_id:
        existing_stmt = existing_stmt.where(Alert.risk_id == risk_id)

    existing_result = await db.execute(existing_stmt)
    existing = existing_result.scalar_one_or_none()

    if existing:
        return None

    # Create new alert
    alert = Alert(
        alert_type=alert_type,
        risk_id=risk_id,
        message=message,
        severity=severity,
        is_read=False,
        is_dismissed=False,
        created_for_role=AlertRole.RISK_OFFICER,
    )

    db.add(alert)
    return alert
