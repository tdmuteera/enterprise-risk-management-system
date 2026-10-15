"""
Async risk scoring service for database integration.

Handles automatic score recalculation, institutional risk index updates,
audit trail logging, and alert generation on score changes.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func

from models.risk import Risk, RiskHistory, Alert, RiskLink
from models.alert import AlertType, AlertSeverity, AlertCreatedForRole
from utils.risk_scorer import (
    calculate_risk_score,
    normalise_score,
    calculate_iri,
    detect_risk_chain,
)


async def recompute_and_save_risk(
    db: AsyncSession,
    risk_id: UUID,
    user_id: UUID,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Risk:
    """
    Recalculate risk score, update linked IRI, log change, and trigger alerts.

    Pipeline:
      1. Fetch the risk with relationships
      2. Calculate new score from factors
      3. If score changed, update risk record
      4. Recalculate IRI for all risks in cluster
      5. Write RiskHistory audit entry
      6. Generate alert if crossing into Critical
      7. Commit transaction

    Args:
        db: SQLAlchemy async session
        risk_id: UUID of risk to update
        user_id: UUID of user making the change
        ip_address: Optional IP for audit trail
        user_agent: Optional browser user-agent for audit trail

    Returns:
        Updated Risk object

    Raises:
        ValueError: If risk not found
    """
    # Fetch risk with relationships
    stmt = (
        select(Risk)
        .where(Risk.id == risk_id)
        .options(
            selectinload(Risk.department),
            selectinload(Risk.owner),
            selectinload(Risk.source_links),
            selectinload(Risk.target_links),
        )
    )
    result = await db.execute(stmt)
    risk = result.scalar_one_or_none()

    if not risk:
        raise ValueError(f"Risk {risk_id} not found")

    # Calculate new score
    new_score = calculate_risk_score(
        risk.likelihood,
        risk.impact,
        risk.velocity,
        risk.detectability,
    )
    new_normalised = normalise_score(new_score)

    # Store previous values for audit
    previous_values = {
        "risk_score": risk.risk_score,
        "institutional_risk_index": risk.institutional_risk_index,
    }

    score_changed = risk.risk_score != new_score

    if score_changed:
        risk.risk_score = new_score

    # Recalculate IRI for entire cluster
    await _update_cluster_iri(db, risk)

    # Log change to audit trail
    if score_changed or risk.risk_score != previous_values["risk_score"]:
        history_entry = RiskHistory(
            risk_id=risk.id,
            action="score_changed",
            changed_by_id=user_id,
            changed_at=datetime.utcnow(),
            previous_values=previous_values,
            new_values={
                "risk_score": risk.risk_score,
                "institutional_risk_index": risk.institutional_risk_index,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(history_entry)

    # Generate alert if crossing into Critical
    if new_normalised >= 65 and (
        not risk.risk_score or normalise_score(risk.risk_score) < 65
    ):
        critical_alert = Alert(
            alert_type=AlertType.HighRisk,
            risk_id=risk.id,
            message=f"CRITICAL: Risk '{risk.title}' has reached critical threshold "
            f"(score: {new_normalised})",
            severity=AlertSeverity.Critical,
            is_read=False,
            is_dismissed=False,
            created_for_role=AlertCreatedForRole.Executive,
        )
        db.add(critical_alert)

    await db.commit()
    await db.refresh(risk)

    return risk


async def recompute_all_scores(db: AsyncSession) -> int:
    """
    Recalculate raw scores for all risks, refresh institutional risk indexes, commit once.

    Intended for the nightly scheduled job (23:00 UTC).
    """
    stmt = select(Risk)
    result = await db.execute(stmt)
    risks = result.scalars().all()

    score_updates = 0
    for risk in risks:
        try:
            new_score = calculate_risk_score(
                risk.likelihood,
                risk.impact,
                risk.velocity,
                risk.detectability,
            )
            if risk.risk_score != new_score:
                risk.risk_score = new_score
                score_updates += 1
        except Exception as e:
            print(f"Error recalculating score for risk {risk.id}: {e}")
            continue

    await db.flush()

    # Recompute IRI for each risk (cluster-aware; redundant calls are safe)
    for risk in risks:
        try:
            await _update_cluster_iri(db, risk)
        except Exception as e:
            print(f"Error refreshing IRI for risk {risk.id}: {e}")
            continue

    await db.commit()
    return score_updates


# ============================================================================
# INTERNAL HELPERS
# ============================================================================


async def _update_cluster_iri(db: AsyncSession, root_risk: Risk) -> None:
    """
    Recalculate institutional risk index for all risks in a cluster.

    When a risk score changes, all linked risks in the cluster must have
    their IRI recalculated to reflect the new institutional impact.

    Algorithm:
      1. Detect all risks in cluster (connected graph)
      2. For each risk in cluster:
         a. Get all linked risks (source and target)
         b. Collect normalized scores and weights
         c. Count unique departments
         d. Calculate new IRI = Σ(scores) × avg_weight × sqrt(dept_count)

    Args:
        db: SQLAlchemy async session
        root_risk: Risk that changed (starting point for cluster detection)
    """
    # Fetch all risks and links to build cluster graph
    all_risks_stmt = select(Risk)
    all_risks_result = await db.execute(all_risks_stmt)
    all_risks = all_risks_result.scalars().all()

    all_links_stmt = select(RiskLink)
    all_links_result = await db.execute(all_links_stmt)
    all_links = all_links_result.scalars().all()

    # Convert to dicts for risk chain detection
    risks_dict = [{"id": str(r.id), "title": r.title} for r in all_risks]
    links_dict = [
        {
            "source_risk_id": str(l.source_risk_id),
            "target_risk_id": str(l.target_risk_id),
            "weight": l.weight,
        }
        for l in all_links
    ]

    # Detect cluster containing root_risk
    clusters = detect_risk_chain(risks_dict, links_dict)
    cluster_ids = None

    for cluster in clusters:
        if str(root_risk.id) in cluster:
            cluster_ids = [UUID(rid) for rid in cluster]
            break

    if not cluster_ids:
        return

    # Update IRI for each risk in cluster
    for risk in all_risks:
        if risk.id not in cluster_ids:
            continue

        # Get all linked risks
        source_stmt = (
            select(RiskLink)
            .where(RiskLink.source_risk_id == risk.id)
            .options(selectinload(RiskLink.target_risk))
        )
        source_result = await db.execute(source_stmt)
        source_links = source_result.scalars().all()

        target_stmt = (
            select(RiskLink)
            .where(RiskLink.target_risk_id == risk.id)
            .options(selectinload(RiskLink.source_risk))
        )
        target_result = await db.execute(target_stmt)
        target_links = target_result.scalars().all()

        # Collect scores and weights
        linked_scores = []
        weights = []
        departments = set()

        for link in source_links:
            if link.target_risk:
                linked_scores.append(
                    normalise_score(link.target_risk.risk_score or 1.0)
                )
                weights.append(link.weight)
                departments.add(link.target_risk.department_id)

        for link in target_links:
            if link.source_risk:
                linked_scores.append(
                    normalise_score(link.source_risk.risk_score or 1.0)
                )
                weights.append(link.weight)
                departments.add(link.source_risk.department_id)

        # Calculate new IRI
        if linked_scores and weights:
            new_iri = calculate_iri(
                linked_scores,
                weights,
                len(departments),
            )
            risk.institutional_risk_index = new_iri
