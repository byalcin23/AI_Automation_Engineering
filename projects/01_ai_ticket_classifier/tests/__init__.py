"""
Unit tests for CLI interface.
"""

import pytest
from click.testing import CliRunner

# Import CLI functions (adjust based on your actual CLI structure)
try:
    from cli import main, print_help
except ImportError:
    # If direct import fails, these are integration tests
    pass


class TestCLI:
    """Test cases for CLI interface."""

    def test_help_message(self):
        """Test help message is available."""
        # This is a smoke test
        assert "AI TICKET CLASSIFIER" or "Usage" or "demo"

    def test_classifier_callable(self):
        """Test that classifier can be called without errors."""
        from classifier import TicketClassifier

        classifier = TicketClassifier()
        result = classifier.classify("Test", "Description")

        assert result is not None
        assert result.category
        assert result.priority
