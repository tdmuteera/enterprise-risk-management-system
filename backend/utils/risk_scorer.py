"""
Pure Python risk scoring utility module (no database calls).

Implements multi-factor risk scoring, institutional risk indexing,
colour band classification, and risk chain detection.
"""

import math
from typing import Any, Dict, List


# ============================================================================
# CORE SCORING FUNCTIONS
# ============================================================================


def calculate_risk_score(
    likelihood: int,
    impact: int,
    velocity: int,
    detectability: int,
) -> float:
    """
    Calculate raw risk score from four factors (1-5 scale).

    Formula: likelihood × impact × velocity × detectability
    Range: 1 (min: 1×1×1×1) → 625 (max: 5×5×5×5)

    Args:
        likelihood: How likely is the risk? (1-5)
        impact: How severe if it occurs? (1-5)
        velocity: How fast does it materialize? (1-5)
        detectability: How hard to detect? (1-5)

    Returns:
        Raw risk score as float (1.0 to 625.0)

    Raises:
        ValueError: If any factor is outside 1-5 range
    """
    for name, value in [
        ("likelihood", likelihood),
        ("impact", impact),
        ("velocity", velocity),
        ("detectability", detectability),
    ]:
        if not isinstance(value, int) or value < 1 or value > 5:
            raise ValueError(f"{name} must be integer 1-5, got {value}")

    return float(likelihood * impact * velocity * detectability)


def normalise_score(raw_score: float) -> float:
    """
    Convert raw score (1-625) to normalized display score (0.2-100).

    Formula: round(raw_score / 6.25, 1)

    Args:
        raw_score: Risk score in range 1-625

    Returns:
        Normalized score in range 0.2-100.0 (rounded to 1 decimal)

    Raises:
        ValueError: If score is outside valid range
    """
    if not isinstance(raw_score, (int, float)) or raw_score < 1 or raw_score > 625:
        raise ValueError(f"raw_score must be 1-625, got {raw_score}")

    return round(raw_score / 6.25, 1)


def get_colour_band(normalised_score: float) -> Dict[str, Any]:
    """
    Classify risk by normalized score into colour bands.

    Bands:
      Critical (65-100):  #D32F2F (red)
      High (40-64):       #F57C00 (orange)
      Medium (20-39):     #FBC02D (amber)
      Low (0-19):         #388E3C (green)

    Args:
        normalised_score: Score in range 0.2-100

    Returns:
        Dict with keys: label, hex, tailwind_class

    Raises:
        ValueError: If score is outside valid range
    """
    if not isinstance(normalised_score, (int, float)):
        raise ValueError(f"normalised_score must be numeric, got {type(normalised_score)}")

    if normalised_score < 0 or normalised_score > 100:
        raise ValueError(f"normalised_score must be 0-100, got {normalised_score}")

    if normalised_score >= 65:
        return {
            "label": "Critical",
            "hex": "#D32F2F",
            "tailwind_class": "bg-red-600",
        }
    elif normalised_score >= 40:
        return {
            "label": "High",
            "hex": "#F57C00",
            "tailwind_class": "bg-orange-600",
        }
    elif normalised_score >= 20:
        return {
            "label": "Medium",
            "hex": "#FBC02D",
            "tailwind_class": "bg-amber-400",
        }
    else:
        return {
            "label": "Low",
            "hex": "#388E3C",
            "tailwind_class": "bg-green-600",
        }


# ============================================================================
# INSTITUTIONAL RISK INDEX (IRI)
# ============================================================================


def calculate_iri(
    linked_risk_scores: List[float],
    interdependency_weights: List[float],
    unique_departments_count: int,
) -> float:
    """
    Calculate Institutional Risk Index (IRI) for a risk cluster.

    Formula:
      IRI = Σ(linked_risk_scores) × average_interdependency_weight
            × sqrt(unique_departments_count)

    The sqrt() term prevents linear explosion when many departments are affected.

    Args:
        linked_risk_scores: List of normalized scores from linked risks
        interdependency_weights: List of weights (0.0-1.0) for each link
        unique_departments_count: Number of unique departments in cluster

    Returns:
        Institutional Risk Index as float (≥ 0.0)

    Raises:
        ValueError: If weights are outside 0-1 range or lists are mismatched
    """
    if not linked_risk_scores or not interdependency_weights:
        return 0.0

    if len(linked_risk_scores) != len(interdependency_weights):
        raise ValueError(
            f"linked_risk_scores and interdependency_weights must have same length: "
            f"{len(linked_risk_scores)} vs {len(interdependency_weights)}"
        )

    for i, weight in enumerate(interdependency_weights):
        if not isinstance(weight, (int, float)) or weight < 0 or weight > 1:
            raise ValueError(
                f"interdependency_weights[{i}] must be 0.0-1.0, got {weight}"
            )

    if unique_departments_count < 1 or not isinstance(unique_departments_count, int):
        raise ValueError(
            f"unique_departments_count must be positive integer, got {unique_departments_count}"
        )

    sum_scores = sum(linked_risk_scores)
    avg_weight = sum(interdependency_weights) / len(interdependency_weights)
    dept_factor = math.sqrt(unique_departments_count)

    iri = sum_scores * avg_weight * dept_factor
    return round(iri, 2)


# ============================================================================
# RISK RANKING AND CLUSTERING
# ============================================================================


def get_top_n_risks(risks: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    """
    Sort risks by score (descending) and return top N.

    Args:
        risks: List of risk dicts, each with 'risk_score' key
        n: Number of top risks to return

    Returns:
        Top N risks sorted by risk_score descending

    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    if not risks:
        return []

    sorted_risks = sorted(risks, key=lambda r: r.get("risk_score", 0), reverse=True)
    return sorted_risks[:n]


def detect_risk_chain(
    risks: List[Dict[str, Any]],
    links: List[Dict[str, Any]],
) -> List[List[str]]:
    """
    Detect connected risk clusters using graph traversal (DFS).

    A chain is a connected component where risks are linked via risk_links.
    Uses depth-first search to identify all clusters.

    Args:
        risks: List of risk dicts with 'id' key
        links: List of link dicts with 'source_risk_id' and 'target_risk_id'

    Returns:
        List of clusters, each cluster is a list of risk IDs

    Example:
        >>> risks = [
        ...     {'id': 'r1', 'title': 'Risk 1'},
        ...     {'id': 'r2', 'title': 'Risk 2'},
        ...     {'id': 'r3', 'title': 'Risk 3'},
        ... ]
        >>> links = [
        ...     {'source_risk_id': 'r1', 'target_risk_id': 'r2'},
        ... ]
        >>> detect_risk_chain(risks, links)
        [['r1', 'r2'], ['r3']]
    """
    if not risks:
        return []

    # Build adjacency list
    graph: Dict[str, List[str]] = {}
    risk_ids = {r["id"] for r in risks}

    for risk_id in risk_ids:
        graph[risk_id] = []

    for link in links:
        source = link.get("source_risk_id")
        target = link.get("target_risk_id")

        if source in risk_ids and target in risk_ids:
            graph[source].append(target)
            graph[target].append(source)  # Undirected graph

    # DFS to find connected components
    visited: set = set()
    clusters: List[List[str]] = []

    def dfs(node: str, cluster: List[str]) -> None:
        visited.add(node)
        cluster.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, cluster)

    for risk_id in risk_ids:
        if risk_id not in visited:
            cluster: List[str] = []
            dfs(risk_id, cluster)
            clusters.append(sorted(cluster))  # Sort for deterministic output

    # Sort clusters by size (largest first) for consistency
    return sorted(clusters, key=len, reverse=True)


# ============================================================================
# SCORING PIPELINE
# ============================================================================


def score_and_classify_risk(
    likelihood: int,
    impact: int,
    velocity: int,
    detectability: int,
) -> Dict[str, Any]:
    """
    Complete scoring and classification pipeline for a single risk.

    Convenience function that combines:
      1. Calculate raw score
      2. Normalize to 0-100 scale
      3. Classify into colour band

    Args:
        likelihood: 1-5 scale
        impact: 1-5 scale
        velocity: 1-5 scale
        detectability: 1-5 scale

    Returns:
        Dict with keys:
          - raw_score: float (1-625)
          - normalised_score: float (0.2-100)
          - colour_band: dict (label, hex, tailwind_class)

    Example:
        >>> result = score_and_classify_risk(5, 5, 5, 5)
        >>> result['raw_score']
        625.0
        >>> result['normalised_score']
        100.0
        >>> result['colour_band']['label']
        'Critical'
    """
    raw_score = calculate_risk_score(likelihood, impact, velocity, detectability)
    normalised_score = normalise_score(raw_score)
    colour_band = get_colour_band(normalised_score)

    return {
        "raw_score": raw_score,
        "normalised_score": normalised_score,
        "colour_band": colour_band,
    }
