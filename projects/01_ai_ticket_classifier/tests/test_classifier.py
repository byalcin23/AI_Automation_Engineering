"""
Unit tests for ticket classifier.
"""

import pytest

from classifier import ClassificationResult, TicketClassifier


class TestTicketClassifier:
    """Test cases for TicketClassifier."""

    @pytest.fixture
    def classifier(self):
        """Create a classifier instance."""
        return TicketClassifier()

    def test_classify_incident_high_priority(self, classifier):
        """Test incident classification with high priority."""
        result = classifier.classify(
            title="Production database down",
            description="Database server is not responding. P1 outage affecting all users."
        )

        assert result.category == "incident"
        assert result.priority == "critical"
        assert result.confidence > 0.5
        assert result.recommended_action

    def test_classify_deployment(self, classifier):
        """Test deployment classification."""
        result = classifier.classify(
            title="Deploy microservice v2.1.4",
            description="Ready for production deployment. Blue-green strategy."
        )

        assert result.category == "deployment"
        assert result.recommended_action

    def test_classify_config_change(self, classifier):
        """Test config change classification."""
        result = classifier.classify(
            title="Update monitoring alert thresholds",
            description="Change CPU alert from 90% to 80%. Update Prometheus rules."
        )

        assert result.category == "config_change"
        assert "config" in result.category.lower() or "monitoring" in result.recommended_action.lower()

    def test_classify_access_request(self, classifier):
        """Test access request classification."""
        result = classifier.classify(
            title="Request SSH access to staging",
            description="New team member needs SSH key and staging environment access."
        )

        assert result.category == "access_request"
        assert result.priority in ["low", "medium"]

    def test_classify_investigation(self, classifier):
        """Test investigation classification."""
        result = classifier.classify(
            title="Investigate unusual network traffic",
            description="Security team flagged suspicious outbound connections. Debug needed."
        )

        assert result.category == "investigation"

    def test_confidence_score_range(self, classifier):
        """Test that confidence score is between 0 and 1."""
        result = classifier.classify(
            title="Some ticket",
            description="Some description"
        )

        assert 0.0 <= result.confidence <= 1.0

    def test_priority_levels(self, classifier):
        """Test all priority levels."""
        priorities = []

        # Critical
        result = classifier.classify("P0 production outage", "System completely down")
        priorities.append(result.priority)

        # High
        result = classifier.classify("Production issue detected", "High impact")
        priorities.append(result.priority)

        # Medium/Low
        result = classifier.classify("Update config", "Minor change")
        priorities.append(result.priority)

        # All should be valid priority levels
        for priority in priorities:
            assert priority in ["critical", "high", "medium", "low"]

    def test_empty_ticket_handling(self, classifier):
        """Test handling of empty or minimal input."""
        result = classifier.classify("", "")
        assert result.category in ["incident", "deployment", "config_change", "access_request", "investigation"]
        assert result.priority in ["critical", "high", "medium", "low"]

    def test_result_dataclass(self):
        """Test ClassificationResult dataclass."""
        result = ClassificationResult(
            category="incident",
            priority="high",
            confidence=0.85,
            recommended_action="Check logs"
        )

        assert result.category == "incident"
        assert result.priority == "high"
        assert result.confidence == 0.85
        assert result.recommended_action == "Check logs"

    def test_multiple_classifications_consistency(self, classifier):
        """Test that same input produces same output."""
        title = "Database replication lag"
        description = "Replication lag detected on replica"

        result1 = classifier.classify(title, description)
        result2 = classifier.classify(title, description)

        assert result1.category == result2.category
        assert result1.priority == result2.priority
        assert result1.confidence == result2.confidence

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
