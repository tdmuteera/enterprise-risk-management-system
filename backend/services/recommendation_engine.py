"""
Smart recommendation engine for context-aware risk suggestions.

Rule-based recommendation system (no ML) that generates actionable
suggestions based on risk category, impact, and detectability.
"""

from typing import List

from models.risk import Risk


def get_recommendations_for_risk(risk: Risk) -> List[str]:
    """
    Generate actionable recommendations for a specific risk.

    Uses category, impact, and detectability to determine context.

    Args:
        risk: Risk object with category, impact, detectability, risk_score

    Returns:
        List of recommendation strings (actionable steps)

    Examples:
        risk = Risk(category="Financial", impact=5, detectability=4)
        suggestions = get_recommendations_for_risk(risk)
        # Returns: ["Initiate forensic audit review", ...]
    """
    recommendations = []

    # Normalize score to 0-100
    norm_score = risk.risk_score / 6.25 if risk.risk_score else 0

    # Fallback: Any Critical risk
    if norm_score >= 65:
        recommendations.append("Escalate to institutional Risk Officer immediately")
        recommendations.append("Call emergency risk review meeting")

    # Category-specific rules
    if risk.category == "Financial":
        if risk.impact >= 4 and risk.detectability >= 4:
            recommendations.append("Initiate forensic audit review")
            recommendations.append("Implement segregation of duties")
            recommendations.append("Enable transaction-level monitoring")
        elif risk.impact >= 4:
            recommendations.append("Review monthly financial close procedures")
            recommendations.append("Strengthen internal controls")
        elif risk.detectability >= 4:
            recommendations.append("Improve financial reporting systems")

    elif risk.category == "HR":
        if risk.impact >= 3:
            recommendations.append("Review staffing levels")
            recommendations.append("Conduct exit interviews")
            recommendations.append("Implement succession planning")
        else:
            recommendations.append("Monitor key personnel retention")

    elif risk.category == "IT":
        if risk.detectability >= 4:
            recommendations.append("Deploy SIEM monitoring")
            recommendations.append("Conduct penetration test")
            recommendations.append("Review access control matrix")
        elif risk.impact >= 4:
            recommendations.append("Review backup and recovery procedures")
            recommendations.append("Update disaster recovery plan")
        else:
            recommendations.append("Implement patch management system")

    elif risk.category == "Academic":
        if risk.impact >= 4:
            recommendations.append("Activate academic continuity plan")
            recommendations.append("Notify Senate Risk Committee")
            recommendations.append("Identify substitute staffing")
        else:
            recommendations.append("Review academic quality assurance")

    elif risk.category == "Compliance":
        if risk.impact >= 4:
            recommendations.append("Engage legal counsel")
            recommendations.append("Conduct compliance audit")
            recommendations.append("Update policy documentation")
        else:
            recommendations.append("Monitor regulatory changes")

    elif risk.category == "Operational":
        if risk.impact >= 4:
            recommendations.append("Develop contingency plans")
            recommendations.append("Brief key operations staff")
        else:
            recommendations.append("Review standard operating procedures")

    elif risk.category == "Reputational":
        if risk.impact >= 4:
            recommendations.append("Prepare media response statement")
            recommendations.append("Brief leadership team")
            recommendations.append("Activate communications protocol")
        elif risk.detectability >= 4:
            recommendations.append("Monitor social media and news")
            recommendations.append("Strengthen stakeholder engagement")

    # Velocity-based recommendations (how fast it materializes)
    if risk.velocity >= 4:
        recommendations.insert(0, "Set up real-time monitoring")
        recommendations.insert(1, "Establish rapid response team")

    # Likelihood-based recommendations
    if risk.likelihood >= 4:
        recommendations.append("Create detailed response playbook")

    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = []
    for rec in recommendations:
        if rec not in seen:
            unique_recommendations.append(rec)
            seen.add(rec)

    return unique_recommendations


def get_recommendations_by_category(
    category: str,
    impact: int,
    detectability: int,
) -> List[str]:
    """
    Get recommendations for a specific category without a full Risk object.

    Useful for previewing recommendations when creating a risk.

    Args:
        category: Risk category (Financial, HR, IT, Academic, etc.)
        impact: Impact level 1-5
        detectability: Detectability level 1-5

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Category-specific rules
    if category == "Financial":
        if impact >= 4 and detectability >= 4:
            recommendations = [
                "Initiate forensic audit review",
                "Implement segregation of duties",
                "Enable transaction-level monitoring",
            ]
        elif impact >= 4:
            recommendations = [
                "Review monthly financial close procedures",
                "Strengthen internal controls",
            ]
        elif detectability >= 4:
            recommendations = [
                "Improve financial reporting systems",
                "Enhance monitoring dashboards",
            ]
        else:
            recommendations = [
                "Review accounting policies",
                "Update financial procedures",
            ]

    elif category == "HR":
        if impact >= 3:
            recommendations = [
                "Review staffing levels",
                "Conduct exit interviews",
                "Implement succession planning",
            ]
        else:
            recommendations = [
                "Monitor key personnel retention",
                "Review HR policies",
            ]

    elif category == "IT":
        if detectability >= 4:
            recommendations = [
                "Deploy SIEM monitoring",
                "Conduct penetration test",
                "Review access control matrix",
            ]
        elif impact >= 4:
            recommendations = [
                "Review backup and recovery procedures",
                "Update disaster recovery plan",
            ]
        else:
            recommendations = [
                "Implement patch management system",
                "Review IT security policies",
            ]

    elif category == "Academic":
        if impact >= 4:
            recommendations = [
                "Activate academic continuity plan",
                "Notify Senate Risk Committee",
                "Identify substitute staffing",
            ]
        else:
            recommendations = [
                "Review academic quality assurance",
                "Update course delivery plans",
            ]

    elif category == "Compliance":
        if impact >= 4:
            recommendations = [
                "Engage legal counsel",
                "Conduct compliance audit",
                "Update policy documentation",
            ]
        else:
            recommendations = [
                "Monitor regulatory changes",
                "Review compliance procedures",
            ]

    elif category == "Operational":
        if impact >= 4:
            recommendations = [
                "Develop contingency plans",
                "Brief key operations staff",
            ]
        else:
            recommendations = [
                "Review standard operating procedures",
                "Conduct operational review",
            ]

    elif category == "Reputational":
        if impact >= 4:
            recommendations = [
                "Prepare media response statement",
                "Brief leadership team",
                "Activate communications protocol",
            ]
        elif detectability >= 4:
            recommendations = [
                "Monitor social media and news",
                "Strengthen stakeholder engagement",
            ]
        else:
            recommendations = [
                "Review reputation management policy",
                "Strengthen communications",
            ]

    return recommendations


def get_critical_risk_recommendations() -> List[str]:
    """
    Get universal recommendations for any Critical risk (score >= 65).

    These apply regardless of category.

    Returns:
        List of critical response recommendations
    """
    return [
        "Escalate to institutional Risk Officer immediately",
        "Call emergency risk review meeting",
        "Notify executive leadership",
        "Document decision trail for audit",
        "Establish 24-hour reporting protocol",
        "Prepare board notification materials",
    ]


def get_remediation_checklist(
    category: str,
    impact: int,
    likelihood: int,
) -> List[str]:
    """
    Get a comprehensive remediation checklist for a risk.

    Combines immediate actions with longer-term remediation.

    Args:
        category: Risk category
        impact: Impact level 1-5
        likelihood: Likelihood level 1-5

    Returns:
        List of checklist items (immediate + follow-up)
    """
    checklist = []

    # Immediate actions (always)
    checklist.extend([
        "[IMMEDIATE] Document current state of risk",
        "[IMMEDIATE] Assign owner to remediation",
        "[IMMEDIATE] Create risk register entry",
    ])

    # Impact-based urgency
    if impact >= 4:
        checklist.extend([
            "[URGENT] Brief executive stakeholders",
            "[URGENT] Determine escalation path",
        ])

    if impact >= 3:
        checklist.append("[URGENT] Assess third-party notifications")

    # Category-specific checklist
    if category == "Financial":
        checklist.extend([
            "[1 WEEK] Review control environment",
            "[1 WEEK] Identify process improvements",
            "[2 WEEKS] Implement preliminary controls",
            "[1 MONTH] Complete control effectiveness testing",
        ])

    elif category == "HR":
        checklist.extend([
            "[1 WEEK] Review recruitment/retention strategy",
            "[2 WEEKS] Update training programs",
            "[1 MONTH] Assess organizational capacity",
        ])

    elif category == "IT":
        checklist.extend([
            "[1 WEEK] Conduct security assessment",
            "[2 WEEKS] Apply security patches",
            "[1 MONTH] Complete security hardening",
        ])

    elif category == "Academic":
        checklist.extend([
            "[1 WEEK] Consult with academic leadership",
            "[2 WEEKS] Activate contingency plans",
            "[1 MONTH] Resume normal operations",
        ])

    elif category == "Compliance":
        checklist.extend([
            "[1 WEEK] Determine regulatory impact",
            "[2 WEEKS] Notify compliance officer",
            "[1 MONTH] File required disclosures",
        ])

    elif category == "Operational":
        checklist.extend([
            "[1 WEEK] Activate contingency plans",
            "[2 WEEKS] Restore normal operations",
            "[1 MONTH] Post-incident review",
        ])

    elif category == "Reputational":
        checklist.extend([
            "[URGENT] Issue holding statement",
            "[1 WEEK] Complete communications strategy",
            "[2 WEEKS] Resume stakeholder engagement",
        ])

    # Likelihood-based follow-up
    if likelihood >= 4:
        checklist.append("[ONGOING] Maintain heightened monitoring")

    return checklist
