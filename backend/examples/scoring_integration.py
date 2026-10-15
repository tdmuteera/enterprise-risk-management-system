"""
Integration example: Using the complete risk scoring system.

This module demonstrates how to use the risk scoring engine
in a real application with database, routers, and alerts.
"""

from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from utils.risk_scorer import (
    calculate_risk_score,
    normalise_score,
    get_colour_band,
    calculate_iri,
    get_top_n_risks,
    detect_risk_chain,
    score_and_classify_risk,
)
from services.scoring_service import (
    recompute_and_save_risk,
    recompute_all_scores,
)


# ============================================================================
# SCENARIO 1: Create a new risk and calculate its score
# ============================================================================


async def create_risk_with_score(
    db: AsyncSession,
    title: str,
    likelihood: int,
    impact: int,
    velocity: int,
    detectability: int,
    user_id: UUID,
) -> dict:
    """
    Create a new risk and immediately calculate its score and classification.
    
    Args:
        db: Database session
        title: Risk title
        likelihood: 1-5 scale
        impact: 1-5 scale
        velocity: 1-5 scale
        detectability: 1-5 scale
        user_id: UUID of user creating the risk
    
    Returns:
        Dict with risk data including score and colour band
    
    Example:
        result = await create_risk_with_score(
            db, "Data Breach", 3, 5, 4, 2, user_id
        )
        print(f"Risk: {result['title']}")
        print(f"Score: {result['normalised_score']}")
        print(f"Severity: {result['colour_band']['label']}")
    """
    # Calculate score
    scoring_result = score_and_classify_risk(
        likelihood, impact, velocity, detectability
    )

    # In real implementation, create Risk record in database
    risk_data = {
        "title": title,
        "likelihood": likelihood,
        "impact": impact,
        "velocity": velocity,
        "detectability": detectability,
        "risk_score": scoring_result["raw_score"],
        "normalised_score": scoring_result["normalised_score"],
        "colour_band": scoring_result["colour_band"],
        "created_by": user_id,
    }

    print(f"Created risk: {title}")
    print(f"  Raw score: {risk_data['risk_score']}")
    print(f"  Normalised: {risk_data['normalised_score']}")
    print(f"  Severity: {risk_data['colour_band']['label']}")

    return risk_data


# ============================================================================
# SCENARIO 2: Update risk factors and recalculate with audit trail
# ============================================================================


async def update_risk_factors(
    db: AsyncSession,
    risk_id: UUID,
    new_likelihood: int,
    new_impact: int,
    new_velocity: int,
    new_detectability: int,
    user_id: UUID,
    user_email: str,
) -> dict:
    """
    Update risk factors and trigger automatic score recalculation.
    
    This function:
    1. Updates the risk factors in database
    2. Recalculates score
    3. Updates IRI for entire cluster
    4. Logs change to RiskHistory
    5. Generates alert if crossing Critical threshold
    
    Example:
        result = await update_risk_factors(
            db=db,
            risk_id=risk_id,
            new_likelihood=5,  # Increased
            new_impact=5,      # Increased
            new_velocity=4,
            new_detectability=2,
            user_id=user_id,
            user_email="officer@uni.ac.za"
        )
        
        if result['alert_generated']:
            print(f"ALERT: {result['alert_message']}")
    """
    # Fetch risk and update factors (in real code)
    # For this example, simulate the recalculation

    # Call async scoring service
    updated_risk = await recompute_and_save_risk(
        db=db,
        risk_id=risk_id,
        user_id=user_id,
        ip_address="192.168.1.100",  # Would come from request
        user_agent="Mozilla/5.0...",   # Would come from request
    )

    # Check if score crossed Critical threshold
    new_normalised = normalise_score(updated_risk.risk_score)
    alert_generated = new_normalised >= 65

    return {
        "risk_id": risk_id,
        "old_score": updated_risk.risk_score,  # Would need to track old
        "new_score": updated_risk.risk_score,
        "normalised_score": new_normalised,
        "colour_band": get_colour_band(new_normalised),
        "institutional_risk_index": updated_risk.institutional_risk_index,
        "alert_generated": alert_generated,
        "alert_message": (
            f"CRITICAL: Risk has reached critical threshold "
            f"(score: {new_normalised})"
            if alert_generated
            else None
        ),
        "updated_by": user_email,
    }


# ============================================================================
# SCENARIO 3: Display risk dashboard with colour bands
# ============================================================================


async def get_dashboard_risks(
    db: AsyncSession,
    department_id: UUID = None,
) -> dict:
    """
    Fetch risks for dashboard display with colour bands and rankings.
    
    Returns:
        Dict with risks grouped by colour band
    
    Example:
        dashboard = await get_dashboard_risks(db, dept_id)
        
        for risk in dashboard['critical']:
            print(f"[{risk['colour_band']['label']}] {risk['title']}")
        
        print(f"Top 5 risks: {dashboard['top_5']}")
    """
    # In real code: fetch from DB
    # For this example: demonstrate the structure
    
    dashboard = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
        "top_5": [],
        "clusters": [],
        "summary": {
            "total_risks": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "average_score": 0.0,
        },
    }

    # Fetch all risks (in real code)
    all_risks = []  # Would be from db query

    # Group by colour band
    for risk in all_risks:
        norm_score = normalise_score(risk["risk_score"])
        band = get_colour_band(norm_score)

        risk_with_band = {
            **risk,
            "normalised_score": norm_score,
            "colour_band": band,
        }

        if band["label"] == "Critical":
            dashboard["critical"].append(risk_with_band)
        elif band["label"] == "High":
            dashboard["high"].append(risk_with_band)
        elif band["label"] == "Medium":
            dashboard["medium"].append(risk_with_band)
        else:
            dashboard["low"].append(risk_with_band)

    # Get top 5 by score
    dashboard["top_5"] = get_top_n_risks(all_risks, 5)

    # Detect clusters
    risks_dict = [{"id": r["id"], "title": r["title"]} for r in all_risks]
    links_dict = []  # Would be from RiskLink table
    dashboard["clusters"] = detect_risk_chain(risks_dict, links_dict)

    # Calculate summary
    dashboard["summary"]["total_risks"] = len(all_risks)
    dashboard["summary"]["critical_count"] = len(dashboard["critical"])
    dashboard["summary"]["high_count"] = len(dashboard["high"])
    dashboard["summary"]["medium_count"] = len(dashboard["medium"])
    dashboard["summary"]["low_count"] = len(dashboard["low"])

    if all_risks:
        avg_score = sum(r["risk_score"] for r in all_risks) / len(all_risks)
        dashboard["summary"]["average_score"] = normalise_score(avg_score)

    return dashboard


# ============================================================================
# SCENARIO 4: Batch recalculation for scheduled job
# ============================================================================


async def scheduled_nightly_scoring_job(db: AsyncSession) -> dict:
    """
    Scheduled job: Recalculate all risk scores (called by APScheduler at 2 AM).
    
    This is efficient for batch operations:
    - Single commit at end
    - Minimal DB round-trips
    - Counts changes for monitoring
    
    Returns:
        Dict with job results and metrics
    
    Usage in main.py:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            scheduled_nightly_scoring_job,
            'cron',
            hour=2,
            minute=0,
            args=[db]
        )
        scheduler.start()
    """
    print("Starting scheduled scoring recalculation...")

    # Run batch recalculation
    count = await recompute_all_scores(db)

    result = {
        "job_name": "scheduled_nightly_scoring",
        "timestamp": "2026-04-21T02:00:00Z",
        "risks_updated": count,
        "status": "completed" if count >= 0 else "failed",
    }

    print(f"Recalculated {count} risk scores")
    return result


# ============================================================================
# SCENARIO 5: Cluster analysis for governance reporting
# ============================================================================


async def analyze_risk_clusters(db: AsyncSession) -> list:
    """
    Identify and analyze risk clusters for governance reporting.
    
    Returns:
        List of cluster analysis objects
    
    Example output:
        [
            {
                'cluster_id': 1,
                'risks': ['r1', 'r2', 'r3'],
                'max_score': 100.0,
                'cluster_iri': 175.0,
                'departments_affected': 3,
                'recommendation': 'Establish cross-dept task force'
            },
            ...
        ]
    """
    # Fetch all risks and links (in real code)
    all_risks = []
    all_links = []

    # Detect clusters
    risks_dict = [{"id": r["id"], "title": r["title"]} for r in all_risks]
    links_dict = [
        {
            "source_risk_id": str(l["source_risk_id"]),
            "target_risk_id": str(l["target_risk_id"]),
            "weight": l["weight"],
        }
        for l in all_links
    ]

    clusters = detect_risk_chain(risks_dict, links_dict)

    analysis = []
    for i, cluster in enumerate(clusters):
        # Find risks in this cluster
        cluster_risks = [r for r in all_risks if r["id"] in cluster]

        # Calculate metrics
        scores = [normalise_score(r["risk_score"]) for r in cluster_risks]
        weights = [
            l["weight"]
            for l in all_links
            if l["source_risk_id"] in cluster and l["target_risk_id"] in cluster
        ]

        # Count departments
        dept_ids = set()
        for risk in cluster_risks:
            dept_ids.add(risk["department_id"])

        # Calculate cluster IRI
        if scores and weights:
            cluster_iri = calculate_iri(scores, weights, len(dept_ids))
        else:
            cluster_iri = 0.0

        cluster_analysis = {
            "cluster_id": i + 1,
            "size": len(cluster),
            "risk_ids": cluster,
            "max_score": max(scores) if scores else 0,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "cluster_iri": cluster_iri,
            "departments_affected": len(dept_ids),
            "recommendation": (
                "Establish cross-department task force" if len(dept_ids) > 2
                else "Assign single owner"
            ),
        }

        analysis.append(cluster_analysis)

    return analysis


# ============================================================================
# SCENARIO 6: Export risks with colour bands (PDF/Excel)
# ============================================================================


def export_risk_register(
    risks: list,
    format: str = "pdf",
) -> bytes:
    """
    Export risk register with scores and colour bands.
    
    Each risk includes:
    - Title, description, category
    - Raw score, normalised score, colour band
    - Department, owner, status
    - IRI (if clustered)
    
    Example:
        pdf_bytes = export_risk_register(all_risks, format='pdf')
        with open('risk_register.pdf', 'wb') as f:
            f.write(pdf_bytes)
    
    Note: Would use reportlab (PDF) or openpyxl (Excel)
    """
    register_data = []

    for risk in risks:
        norm_score = normalise_score(risk["risk_score"])
        band = get_colour_band(norm_score)

        row = {
            "Risk ID": risk["id"],
            "Title": risk["title"],
            "Category": risk["category"],
            "Department": risk["department"]["name"],
            "Owner": risk["owner"]["full_name"],
            "Likelihood": risk["likelihood"],
            "Impact": risk["impact"],
            "Velocity": risk["velocity"],
            "Detectability": risk["detectability"],
            "Raw Score": risk["risk_score"],
            "Normalised Score": norm_score,
            "Severity": band["label"],
            "IRI": risk.get("institutional_risk_index", "-"),
            "Status": risk["status"],
            "Mitigation Status": risk.get("mitigation_status", "-"),
        }
        register_data.append(row)

    # In real code: use reportlab or openpyxl to generate file
    # For now: return dummy bytes
    return b"<PDF or XLSX content>"


# ============================================================================
# DEMO / USAGE EXAMPLES
# ============================================================================


async def main_example():
    """
    Demonstration of the complete scoring system.
    """
    print("=" * 70)
    print("RISK SCORING SYSTEM - USAGE EXAMPLES")
    print("=" * 70)

    # Example 1: Simple score calculation
    print("\n[EXAMPLE 1] Simple Score Calculation")
    print("-" * 70)
    result = score_and_classify_risk(4, 5, 3, 2)
    print(f"Factors: Likelihood=4, Impact=5, Velocity=3, Detectability=2")
    print(f"  Raw score: {result['raw_score']}")
    print(f"  Normalised: {result['normalised_score']}")
    print(f"  Severity: {result['colour_band']['label']}")
    print(f"  Colour: {result['colour_band']['hex']}")

    # Example 2: IRI calculation
    print("\n[EXAMPLE 2] Institutional Risk Index Calculation")
    print("-" * 70)
    linked_scores = [50.0, 45.0, 40.0]
    weights = [0.9, 0.8, 0.7]
    depts = 4

    iri = calculate_iri(linked_scores, weights, depts)
    print(f"Linked risks: {linked_scores}")
    print(f"Weights: {weights}")
    print(f"Departments: {depts}")
    print(f"IRI = {sum(linked_scores)} × {sum(weights)/len(weights):.2f} × sqrt({depts})")
    print(f"IRI = {iri}")

    # Example 3: Risk ranking
    print("\n[EXAMPLE 3] Risk Ranking")
    print("-" * 70)
    sample_risks = [
        {"id": "r1", "title": "Risk 1", "risk_score": 150.0},
        {"id": "r2", "title": "Risk 2", "risk_score": 500.0},
        {"id": "r3", "title": "Risk 3", "risk_score": 75.0},
    ]
    top_2 = get_top_n_risks(sample_risks, 2)
    print("Top 2 risks by score:")
    for risk in top_2:
        norm = normalise_score(risk["risk_score"])
        band = get_colour_band(norm)
        print(f"  - {risk['title']}: {norm} ({band['label']})")

    print("\n" + "=" * 70)
    print("End of examples")
    print("=" * 70)


if __name__ == "__main__":
    # Run demo
    import asyncio

    asyncio.run(main_example())
