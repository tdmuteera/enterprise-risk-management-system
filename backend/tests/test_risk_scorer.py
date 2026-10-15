"""
Comprehensive unit tests for risk scoring module.

Tests cover:
  - Core scoring calculations
  - Normalization and scaling
  - Colour band classification (edge cases)
  - Institutional Risk Index calculation
  - Risk chain detection
  - Error handling and validation
"""

import pytest
import math
from utils.risk_scorer import (
    calculate_risk_score,
    normalise_score,
    get_colour_band,
    calculate_iri,
    get_top_n_risks,
    detect_risk_chain,
    score_and_classify_risk,
)


class TestBasicScoring:
    """Tests for core risk score calculation."""

    def test_maximum_score(self):
        """Test max score: (5,5,5,5) = 625 raw, 100.0 normalized, Critical."""
        raw = calculate_risk_score(5, 5, 5, 5)
        assert raw == 625.0

        normalised = normalise_score(raw)
        assert normalised == 100.0

        band = get_colour_band(normalised)
        assert band["label"] == "Critical"
        assert band["hex"] == "#D32F2F"

    def test_minimum_score(self):
        """Test min score: (1,1,1,1) = 1 raw, 0.2 normalized, Low."""
        raw = calculate_risk_score(1, 1, 1, 1)
        assert raw == 1.0

        normalised = normalise_score(raw)
        assert normalised == 0.2

        band = get_colour_band(normalised)
        assert band["label"] == "Low"
        assert band["hex"] == "#388E3C"

    def test_mid_range_score(self):
        """Test mid-range: (2,3,2,2) = 24 raw, 3.8 normalized, Low."""
        raw = calculate_risk_score(2, 3, 2, 2)
        assert raw == 24.0

        normalised = normalise_score(raw)
        assert normalised == 3.8

        band = get_colour_band(normalised)
        assert band["label"] == "Low"

    def test_high_score(self):
        """Test high risk: (5,5,3,3) = 225 raw, 36.0 normalized, Medium."""
        raw = calculate_risk_score(5, 5, 3, 3)
        assert raw == 225.0

        normalised = normalise_score(raw)
        assert normalised == 36.0

        band = get_colour_band(normalised)
        assert band["label"] == "Medium"
        assert band["hex"] == "#FBC02D"

    def test_critical_high_score(self):
        """Test critical high: (4,5,4,3) = 240 raw, 38.4 normalized, Medium (just below High)."""
        raw = calculate_risk_score(4, 5, 4, 3)
        assert raw == 240.0

        normalised = normalise_score(raw)
        assert normalised == 38.4

        band = get_colour_band(normalised)
        assert band["label"] == "Medium"

    def test_validation_below_range(self):
        """Test ValueError when score factor is below 1."""
        with pytest.raises(ValueError, match="must be integer 1-5"):
            calculate_risk_score(0, 3, 3, 3)

    def test_validation_above_range(self):
        """Test ValueError when score factor is above 5."""
        with pytest.raises(ValueError, match="must be integer 1-5"):
            calculate_risk_score(6, 3, 3, 3)

    def test_validation_non_integer(self):
        """Test ValueError when score factor is not integer."""
        with pytest.raises(ValueError, match="must be integer 1-5"):
            calculate_risk_score(3.5, 3, 3, 3)  # type: ignore


class TestNormalisationAndScaling:
    """Tests for score normalization."""

    def test_raw_score_validation(self):
        """Test ValueError for raw scores outside 1-625."""
        with pytest.raises(ValueError, match="must be 1-625"):
            normalise_score(0.5)

        with pytest.raises(ValueError, match="must be 1-625"):
            normalise_score(626)

    def test_normalisation_formula(self):
        """Test normalization formula: round(score / 6.25, 1)."""
        # 625 / 6.25 = 100.0
        assert normalise_score(625) == 100.0

        # 312.5 / 6.25 = 50.0
        assert normalise_score(312.5) == 50.0

        # 156.25 / 6.25 = 25.0
        assert normalise_score(156.25) == 25.0

        # 1 / 6.25 = 0.16 → round to 0.2
        assert normalise_score(1) == 0.2

    def test_rounding_precision(self):
        """Test rounding to 1 decimal place."""
        # 100 / 6.25 = 16.0
        assert normalise_score(100) == 16.0

        # 101 / 6.25 = 16.16 → round to 16.2
        assert normalise_score(101) == 16.2

        # 99 / 6.25 = 15.84 → round to 15.8
        assert normalise_score(99) == 15.8


class TestColourBandClassification:
    """Tests for colour band classification (critical edge cases)."""

    def test_critical_band_lower_boundary(self):
        """Test Critical band at lower boundary (65)."""
        band = get_colour_band(65.0)
        assert band["label"] == "Critical"
        assert band["hex"] == "#D32F2F"
        assert band["tailwind_class"] == "bg-red-600"

    def test_critical_band_upper_boundary(self):
        """Test Critical band at upper boundary (100)."""
        band = get_colour_band(100.0)
        assert band["label"] == "Critical"

    def test_high_band_lower_boundary(self):
        """Test High band at lower boundary (40)."""
        band = get_colour_band(40.0)
        assert band["label"] == "High"
        assert band["hex"] == "#F57C00"
        assert band["tailwind_class"] == "bg-orange-600"

    def test_high_band_just_below_critical(self):
        """Test High band just below Critical (64.9)."""
        band = get_colour_band(64.9)
        assert band["label"] == "High"

    def test_medium_band_lower_boundary(self):
        """Test Medium band at lower boundary (20)."""
        band = get_colour_band(20.0)
        assert band["label"] == "Medium"
        assert band["hex"] == "#FBC02D"
        assert band["tailwind_class"] == "bg-amber-400"

    def test_medium_band_just_below_high(self):
        """Test Medium band just below High (39.9)."""
        band = get_colour_band(39.9)
        assert band["label"] == "Medium"

    def test_low_band_upper_boundary(self):
        """Test Low band at upper boundary (19.9)."""
        band = get_colour_band(19.9)
        assert band["label"] == "Low"
        assert band["hex"] == "#388E3C"
        assert band["tailwind_class"] == "bg-green-600"

    def test_low_band_minimum(self):
        """Test Low band at minimum (0.2)."""
        band = get_colour_band(0.2)
        assert band["label"] == "Low"

    def test_invalid_score_too_high(self):
        """Test ValueError for score > 100."""
        with pytest.raises(ValueError, match="must be 0-100"):
            get_colour_band(100.1)

    def test_invalid_score_negative(self):
        """Test ValueError for negative score."""
        with pytest.raises(ValueError, match="must be 0-100"):
            get_colour_band(-0.1)

    def test_invalid_score_non_numeric(self):
        """Test ValueError for non-numeric score."""
        with pytest.raises(ValueError, match="must be numeric"):
            get_colour_band("50")  # type: ignore


class TestInstitutionalRiskIndex:
    """Tests for IRI calculation with dept clustering."""

    def test_iri_single_department(self):
        """Test IRI with single linked risk in one department."""
        scores = [50.0]
        weights = [0.8]
        depts = 1

        iri = calculate_iri(scores, weights, depts)
        # 50.0 × 0.8 × sqrt(1) = 40.0
        assert iri == 40.0

    def test_iri_increases_with_departments(self):
        """Test IRI increases with sqrt(number of departments)."""
        scores = [50.0]
        weights = [0.8]

        iri_1dept = calculate_iri(scores, weights, 1)  # sqrt(1) = 1
        iri_4dept = calculate_iri(scores, weights, 4)  # sqrt(4) = 2
        iri_9dept = calculate_iri(scores, weights, 9)  # sqrt(9) = 3

        assert iri_1dept == 40.0
        assert iri_4dept == 80.0
        assert iri_9dept == 120.0

    def test_iri_multiple_linked_risks(self):
        """Test IRI with multiple linked risks."""
        scores = [50.0, 40.0, 30.0]  # sum = 120
        weights = [0.9, 0.8, 0.7]  # avg = 0.8
        depts = 4  # sqrt(4) = 2

        iri = calculate_iri(scores, weights, depts)
        # 120.0 × 0.8 × 2 = 192.0
        assert iri == 192.0

    def test_iri_zero_for_empty_lists(self):
        """Test IRI returns 0 for empty score/weight lists."""
        iri = calculate_iri([], [], 1)
        assert iri == 0.0

    def test_iri_validation_mismatched_lengths(self):
        """Test ValueError for mismatched score/weight lengths."""
        with pytest.raises(ValueError, match="must have same length"):
            calculate_iri([50.0], [0.8, 0.9], 1)

    def test_iri_validation_weight_out_of_range(self):
        """Test ValueError for weights outside 0-1."""
        with pytest.raises(ValueError, match="must be 0.0-1.0"):
            calculate_iri([50.0], [1.5], 1)

    def test_iri_validation_departments_invalid(self):
        """Test ValueError for invalid department count."""
        with pytest.raises(ValueError, match="must be positive integer"):
            calculate_iri([50.0], [0.8], 0)

    def test_iri_rounding_to_2_decimals(self):
        """Test IRI rounding to 2 decimals."""
        scores = [50.0]
        weights = [0.33]  # May create non-round result
        depts = 1

        iri = calculate_iri(scores, weights, depts)
        # 50 × 0.33 × 1 = 16.5
        assert iri == 16.5


class TestRiskRanking:
    """Tests for get_top_n_risks."""

    def test_top_n_sorting_descending(self):
        """Test risks sorted by score descending."""
        risks = [
            {"id": "r1", "risk_score": 10.0},
            {"id": "r2", "risk_score": 50.0},
            {"id": "r3", "risk_score": 30.0},
        ]

        top = get_top_n_risks(risks, 2)
        assert len(top) == 2
        assert top[0]["id"] == "r2"  # 50.0
        assert top[1]["id"] == "r3"  # 30.0

    def test_top_n_more_than_available(self):
        """Test requesting more risks than available."""
        risks = [
            {"id": "r1", "risk_score": 10.0},
            {"id": "r2", "risk_score": 50.0},
        ]

        top = get_top_n_risks(risks, 10)
        assert len(top) == 2

    def test_top_n_zero(self):
        """Test requesting top 0 risks."""
        risks = [{"id": "r1", "risk_score": 10.0}]
        top = get_top_n_risks(risks, 0)
        assert len(top) == 0

    def test_top_n_empty_list(self):
        """Test empty risks list."""
        top = get_top_n_risks([], 5)
        assert len(top) == 0

    def test_top_n_validation_negative_n(self):
        """Test ValueError for negative n."""
        with pytest.raises(ValueError, match="must be non-negative"):
            get_top_n_risks([], -1)


class TestRiskChainDetection:
    """Tests for detect_risk_chain (clustering)."""

    def test_single_connected_chain(self):
        """Test single chain detection."""
        risks = [
            {"id": "r1"},
            {"id": "r2"},
            {"id": "r3"},
        ]
        links = [
            {"source_risk_id": "r1", "target_risk_id": "r2"},
            {"source_risk_id": "r2", "target_risk_id": "r3"},
        ]

        clusters = detect_risk_chain(risks, links)
        assert len(clusters) == 1
        assert set(clusters[0]) == {"r1", "r2", "r3"}

    def test_multiple_disconnected_chains(self):
        """Test multiple disconnected clusters."""
        risks = [
            {"id": "r1"},
            {"id": "r2"},
            {"id": "r3"},
            {"id": "r4"},
        ]
        links = [
            {"source_risk_id": "r1", "target_risk_id": "r2"},
            {"source_risk_id": "r3", "target_risk_id": "r4"},
        ]

        clusters = detect_risk_chain(risks, links)
        assert len(clusters) == 2
        # Largest clusters first
        assert len(clusters[0]) == 2
        assert len(clusters[1]) == 2

    def test_isolated_risks(self):
        """Test isolated risks with no links."""
        risks = [
            {"id": "r1"},
            {"id": "r2"},
            {"id": "r3"},
        ]
        links = []

        clusters = detect_risk_chain(risks, links)
        assert len(clusters) == 3
        assert ["r1"] in clusters
        assert ["r2"] in clusters
        assert ["r3"] in clusters

    def test_empty_risks(self):
        """Test empty risks list."""
        clusters = detect_risk_chain([], [])
        assert clusters == []

    def test_link_to_nonexistent_risk(self):
        """Test links referencing non-existent risks are ignored."""
        risks = [
            {"id": "r1"},
            {"id": "r2"},
        ]
        links = [
            {"source_risk_id": "r1", "target_risk_id": "r2"},
            {"source_risk_id": "r1", "target_risk_id": "r99"},  # r99 doesn't exist
        ]

        clusters = detect_risk_chain(risks, links)
        # Should only have r1 and r2 linked
        assert len(clusters) == 1
        assert set(clusters[0]) == {"r1", "r2"}

    def test_cluster_sorting_deterministic(self):
        """Test clusters are sorted deterministically."""
        risks = [
            {"id": "r1"},
            {"id": "r2"},
            {"id": "r3"},
            {"id": "r4"},
            {"id": "r5"},
        ]
        links = [
            {"source_risk_id": "r2", "target_risk_id": "r3"},
            {"source_risk_id": "r3", "target_risk_id": "r4"},
        ]

        clusters = detect_risk_chain(risks, links)
        # Largest cluster first (r2, r3, r4), then singles (r1, r5)
        assert clusters[0] == ["r2", "r3", "r4"]
        assert ["r1"] in clusters
        assert ["r5"] in clusters


class TestScoringPipeline:
    """Tests for score_and_classify_risk convenience function."""

    def test_pipeline_maximum(self):
        """Test pipeline with max values."""
        result = score_and_classify_risk(5, 5, 5, 5)

        assert result["raw_score"] == 625.0
        assert result["normalised_score"] == 100.0
        assert result["colour_band"]["label"] == "Critical"

    def test_pipeline_minimum(self):
        """Test pipeline with min values."""
        result = score_and_classify_risk(1, 1, 1, 1)

        assert result["raw_score"] == 1.0
        assert result["normalised_score"] == 0.2
        assert result["colour_band"]["label"] == "Low"

    def test_pipeline_structure(self):
        """Test pipeline returns correct structure."""
        result = score_and_classify_risk(3, 3, 3, 3)

        assert "raw_score" in result
        assert "normalised_score" in result
        assert "colour_band" in result

        band = result["colour_band"]
        assert "label" in band
        assert "hex" in band
        assert "tailwind_class" in band


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_score_at_band_boundaries(self):
        """Test scores exactly at band boundaries."""
        # Critical boundary (65)
        score_65 = calculate_risk_score(5, 5, 2, 1)  # 5×5×2×1 = 50 raw, 8.0 norm
        # Actually this gives 50 raw, 8 norm, which is Low
        # Let's calculate what gives exactly 65 normalized
        # 65 × 6.25 = 406.25
        assert normalise_score(406.25) == 65.0
        band = get_colour_band(65.0)
        assert band["label"] == "Critical"

        # High boundary (40)
        assert normalise_score(250.0) == 40.0
        band = get_colour_band(40.0)
        assert band["label"] == "High"

        # Medium boundary (20)
        assert normalise_score(125.0) == 20.0
        band = get_colour_band(20.0)
        assert band["label"] == "Medium"

    def test_normalization_consistency(self):
        """Test normalization is consistent across multiple calls."""
        raw = 200.0
        result1 = normalise_score(raw)
        result2 = normalise_score(raw)
        assert result1 == result2
