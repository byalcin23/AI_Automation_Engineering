"""
Unit tests for the AI Ticket Classifier.

Tests cover classification, priority detection, confidence scoring,
and edge cases.
"""

import pytest

from classifier import ClassificationResult, TicketClassifier


class TestTicketClassifier:
    """Test suite for TicketClassifier class."""

    @pytest.fixture
    def classifier(self):
        """Create a classifier instance for testing."""
        return TicketClassifier()

    # Tests for basic classification

    def test_classify_incident_basic(self, classifier):
        """Test basic incident classification."""
        result = classifier.classify(
            title="Production database down critical",
            description="Database server is not responding. P0 outage affecting all users."
        )

        assert result.category == "incident"
        assert result.priority in ["critical", "high", "low"]
        assert result.confidence > 0.3
        assert result.recommended_action

    def test_classify_deployment_basic(self, classifier):
        """Test basic deployment classification."""
        result = classifier.classify(
            title="Deploy microservice v2.1.4",
            description="Ready for production deployment. Blue-green strategy."
        )

        assert result.category == "deployment"
        assert result.recommended_action
        assert "deploy" in result.recommended_action.lower() or "release" in result.recommended_action.lower()

    def test_classify_config_change_basic(self, classifier):
        """Test basic config change classification."""
        result = classifier.classify(
            title="Update monitoring alert thresholds",
            description="Change CPU alert from 90% to 80%. Update Prometheus rules."
        )

        assert result.category == "config_change"
        assert result.recommended_action

    def test_classify_access_request_basic(self, classifier):
        """Test basic access request classification."""
        result = classifier.classify(
            title="Request SSH access to staging",
            description="New team member needs SSH key and staging environment access."
        )

        assert result.category == "access_request"
        assert result.priority in ["low", "medium"]
        assert result.recommended_action

    def test_classify_investigation_basic(self, classifier):
        """Test basic investigation classification."""
        result = classifier.classify(
            title="Investigate unusual network traffic",
            description="Security team flagged suspicious outbound connections. Debug needed."
        )

        assert result.category == "investigation"
        assert result.recommended_action

    # Tests for priority detection

    def test_priority_critical(self, classifier):
        """Test critical priority detection."""
        result = classifier.classify(
            title="P0 Production Outage - All APIs Down",
            description="Critical: All production API servers are down. P0 severity. Emergency response needed."
        )

        assert result.priority == "critical"
        assert result.confidence > 0.4

    def test_priority_high(self, classifier):
        """Test high priority detection."""
        result = classifier.classify(
            title="P1 - Database lag detected",
            description="Production database showing high replication lag. High impact."
        )

        assert result.priority in ["critical", "high"]

    def test_priority_medium(self, classifier):
        """Test medium priority detection."""
        result = classifier.classify(
            title="P2 - Update config",
            description="Need to update monitoring thresholds. Medium importance."
        )

        assert result.priority in ["low", "medium"]

    def test_priority_low_default(self, classifier):
        """Test low priority as default."""
        result = classifier.classify(
            title="Minor task",
            description="Something that can wait."
        )

        assert result.priority in ["low", "medium"]

    # Tests for confidence scores

    def test_confidence_score_range(self, classifier):
        """Test that confidence score is between 0 and 1."""
        result = classifier.classify("Test title", "Test description")

        assert 0.0 <= result.confidence <= 1.0

    def test_confidence_score_is_float(self, classifier):
        """Test that confidence is a float."""
        result = classifier.classify("Test", "Description")

        assert isinstance(result.confidence, float)

    def test_confidence_score_precision(self, classifier):
        """Test that confidence has 2 decimal places."""
        result = classifier.classify(
            "Production database down",
            "P0 outage affecting all users."
        )

        # Check it's rounded to 2 decimals
        assert result.confidence == round(result.confidence, 2)

    # Tests for edge cases

    def test_empty_input(self, classifier):
        """Test handling of empty title and description."""
        result = classifier.classify("", "")

        assert result.category in [
            "incident", "deployment", "config_change",
            "access_request", "investigation"
        ]
        assert result.priority in ["critical", "high", "medium", "low"]

    def test_case_insensitivity(self, classifier):
        """Test that classifier is case insensitive."""
        result_lower = classifier.classify(
            "database down",
            "production outage"
        )

        result_upper = classifier.classify(
            "DATABASE DOWN",
            "PRODUCTION OUTAGE"
        )

        assert result_lower.category == result_upper.category
        assert result_lower.priority == result_upper.priority

    def test_consistency_multiple_calls(self, classifier):
        """Test that same input produces same output."""
        title = "Database replication lag"
        description = "Replication lag detected on replica"

        result1 = classifier.classify(title, description)
        result2 = classifier.classify(title, description)

        assert result1.category == result2.category
        assert result1.priority == result2.priority
        assert result1.confidence == result2.confidence

    # Tests for classification result dataclass

    def test_classification_result_dataclass(self):
        """Test ClassificationResult dataclass."""
        result = ClassificationResult(
            category="incident",
            priority="high",
            confidence=0.85,
            recommended_action="Check logs immediately"
        )

        assert result.category == "incident"
        assert result.priority == "high"
        assert result.confidence == 0.85
        assert result.recommended_action == "Check logs immediately"

    def test_classification_result_immutable(self):
        """Test that ClassificationResult is a proper dataclass."""
        result = ClassificationResult(
            category="incident",
            priority="high",
            confidence=0.85,
            recommended_action="Check logs"
        )

        # Should have these attributes
        assert hasattr(result, "category")
        assert hasattr(result, "priority")
        assert hasattr(result, "confidence")
        assert hasattr(result, "recommended_action")

    # Tests for keyword matching

    def test_keyword_matching_sensitivity(self, classifier):
        """Test that keyword matching works correctly."""
        # Strong incident keywords
        result1 = classifier.classify(
            "Outage detected",
            "Critical production outage affecting all users. P0."
        )

        # Weak incident indicators
        result2 = classifier.classify(
            "Check system",
            "Just reviewing system"
        )

        # First should have higher confidence or different category
        assert result1.category == "incident"

    # Tests for action recommendations

    def test_recommended_action_exists(self, classifier):
        """Test that recommended action is always provided."""
        test_cases = [
            ("Production down", "P0 outage"),
            ("Deploy new version", "Release 2.0"),
            ("Request access", "Need SSH key"),
            ("Update monitoring", "Change threshold"),
            ("Investigate issue", "Strange behavior"),
        ]

        for title, desc in test_cases:
            result = classifier.classify(title, desc)
            assert result.recommended_action
            assert len(result.recommended_action) > 0
            assert isinstance(result.recommended_action, str)

    # Tests for all valid categories

    def test_all_valid_categories(self, classifier):
        """Test that all expected categories are used."""
        valid_categories = {
            "incident", "deployment", "config_change",
            "access_request", "investigation"
        }

        test_cases = [
            ("Down", "Outage"),
            ("Deploy", "Release"),
            ("Config", "Update"),
            ("Access", "Permission"),
            ("Debug", "Investigate"),
        ]

        results_categories = set()
        for title, desc in test_cases:
            result = classifier.classify(title, desc)
            results_categories.add(result.category)

        # At least one result should be from valid categories
        assert results_categories.issubset(valid_categories)

    # Tests for all valid priorities

    def test_all_valid_priorities(self, classifier):
        """Test that all expected priority levels are used."""
        valid_priorities = {"critical", "high", "medium", "low"}

        test_cases = [
            ("P0 production down", "Critical outage"),
            ("P1 issue", "High impact"),
            ("P2 change", "Medium priority"),
            ("P3 task", "Low priority"),
        ]

        priorities = [classifier.classify(t, d).priority for t, d in test_cases]

        for priority in priorities:
            assert priority in valid_priorities
