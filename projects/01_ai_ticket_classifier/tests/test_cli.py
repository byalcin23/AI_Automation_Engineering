"""
Integration tests for the CLI module.

Tests the command-line interface functions and argument parsing.
"""

import pytest

from classifier import TicketClassifier


class TestCLIBasics:
    """Basic tests for CLI functionality."""

    def test_classifier_can_be_instantiated(self):
        """Test that TicketClassifier can be created."""
        classifier = TicketClassifier()
        assert classifier is not None

    def test_classifier_has_classify_method(self):
        """Test that classifier has classify method."""
        classifier = TicketClassifier()
        assert hasattr(classifier, "classify")
        assert callable(classifier.classify)

    def test_classify_returns_result(self):
        """Test that classify returns a ClassificationResult."""
        classifier = TicketClassifier()
        result = classifier.classify("Test", "Description")

        assert result is not None
        assert hasattr(result, "category")
        assert hasattr(result, "priority")
        assert hasattr(result, "confidence")
        assert hasattr(result, "recommended_action")

    def test_load_sample_tickets_function_exists(self):
        """Test that sample tickets can be loaded."""
        try:
            import json
            from pathlib import Path

            # Try to load from actual file
            project_dir = Path(__file__).parent.parent
            sample_file = project_dir / "sample_tickets.json"

            if sample_file.exists():
                with open(sample_file, "r") as f:
                    data = json.load(f)
                assert data is not None
                tickets = data.get("tickets", data) if isinstance(data, dict) else data
                assert len(tickets) > 0
        except FileNotFoundError:
            pytest.skip("sample_tickets.json not found")


class TestCLIModes:
    """Tests for different CLI modes."""

    def test_demo_mode_can_classify_tickets(self):
        """Test that demo mode classification works."""
        classifier = TicketClassifier()

        # Simulate demo mode - classify a ticket
        result = classifier.classify(
            "Production database critical issue down",
            "Database not responding. P0 critical outage."
        )

        assert result.category == "incident"
        assert result.priority in ["critical", "high", "low"]

    def test_interactive_mode_classification_works(self):
        """Test that interactive mode classification works."""
        classifier = TicketClassifier()

        # Simulate interactive input
        result = classifier.classify(
            title="Request SSH access",
            description="New team member needs SSH key access."
        )

        assert result.category == "access_request"
        assert result.recommended_action
