"""Tests for incident copilot functionality."""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from copilot import IncidentCopilot
from llm_provider import MockLLMProvider


class TestIncidentCopilot:
    """Tests for IncidentCopilot functionality."""

    @pytest.fixture
    def temp_runbooks_dir(self):
        """Create temporary runbooks directory with sample files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create sample runbooks
            (tmppath / "database_runbook.md").write_text(
                "# Database Runbook\n"
                "Check replication lag with SHOW SLAVE STATUS\n"
                "Severity increases with lag time"
            )

            (tmppath / "cpu_runbook.md").write_text(
                "# CPU Runbook\n"
                "High CPU typically from queries or memory leaks\n"
                "Use top to identify processes"
            )

            yield tmppath

    @pytest.fixture
    def copilot(self, temp_runbooks_dir):
        """Create copilot instance with temporary runbooks."""
        provider = MockLLMProvider()
        return IncidentCopilot(
            llm_provider=provider,
            runbooks_dir=str(temp_runbooks_dir),
        )

    def test_copilot_initialization(self, copilot):
        """Test that copilot initializes successfully."""
        assert copilot is not None
        assert copilot.llm_provider is not None

    def test_copilot_loads_runbooks(self, copilot):
        """Test that copilot loads runbooks."""
        assert len(copilot.documents) == 2

    def test_copilot_creates_chunks(self, copilot):
        """Test that copilot creates searchable chunks."""
        assert len(copilot.chunks) > 0

    def test_analyze_incident_returns_analysis(self, copilot):
        """Test that analyze_incident returns IncidentAnalysis."""
        analysis = copilot.analyze_incident(
            title="Database lag detected",
            description="Replication lag is 10 seconds",
        )

        assert analysis is not None
        assert analysis.incident_title == "Database lag detected"
        assert analysis.category is not None
        assert analysis.urgency is not None

    def test_analyze_incident_finds_relevant_sources(self, copilot):
        """Test that analysis finds relevant runbook sources."""
        analysis = copilot.analyze_incident(
            title="Database lag",
            description="MySQL replication is lagging",
        )

        # Should find database_runbook.md
        assert len(analysis.relevant_sources) > 0

    def test_analyze_incident_provides_action_plan(self, copilot):
        """Test that analysis includes action plan."""
        analysis = copilot.analyze_incident(
            title="High CPU",
            description="CPU usage at 95%",
        )

        assert len(analysis.action_plan) > 0

    def test_analyze_incident_provides_first_checks(self, copilot):
        """Test that analysis includes first checks."""
        analysis = copilot.analyze_incident(
            title="CPU issue",
            description="Server CPU high",
        )

        assert isinstance(analysis.first_checks, list)
        assert len(analysis.first_checks) > 0

    def test_analyze_incident_provides_confidence(self, copilot):
        """Test that analysis includes confidence score."""
        analysis = copilot.analyze_incident(
            title="Database issue",
            description="Database is slow",
        )

        assert 0 <= analysis.confidence_score <= 1.0

    def test_analyze_incident_with_empty_title(self, copilot):
        """Test analyze_incident with empty title."""
        # Should not crash, but will likely have lower confidence
        analysis = copilot.analyze_incident(
            title="",
            description="Some issue description",
        )

        assert analysis is not None

    def test_analyze_incident_provides_escalation(self, copilot):
        """Test that analysis includes escalation recommendation."""
        analysis = copilot.analyze_incident(
            title="Service down",
            description="Production service is offline",
        )

        assert len(analysis.escalation_recommendation) > 0

    def test_copilot_search_functionality(self, copilot):
        """Test that copilot can search chunks effectively."""
        from search import tfidf_search

        # Search for database-related content
        results = tfidf_search("database", copilot.chunks, top_k=3)

        # Should find results
        assert len(results) > 0
        assert all("source" in r for r in results)
        assert all("text" in r for r in results)

    def test_copilot_gracefully_handles_no_runbooks(self, temp_runbooks_dir):
        """Test copilot behavior when no relevant runbooks found."""
        provider = MockLLMProvider()

        # Create copilot with empty runbooks
        empty_dir = temp_runbooks_dir / "empty"
        empty_dir.mkdir()

        # Create one simple file
        (empty_dir / "test.md").write_text("# Empty\nNo content")

        copilot = IncidentCopilot(
            llm_provider=provider,
            runbooks_dir=str(empty_dir),
        )

        # Analyze should still work
        analysis = copilot.analyze_incident(
            title="Unknown issue",
            description="Something completely different",
        )

        assert analysis is not None

    def test_analyze_incident_with_mock_provider(self, copilot):
        """Test incident analysis with mock provider."""
        analysis = copilot.analyze_incident(
            title="Database replication lag",
            description="Lag is 8 seconds behind primary",
        )

        # Mock provider should classify as database issue
        assert "database" in analysis.category.lower()

    def test_analyze_incident_consistency(self, copilot):
        """Test that same incident produces consistent results."""
        analysis1 = copilot.analyze_incident(
            title="CPU issue",
            description="High CPU on prod",
        )

        analysis2 = copilot.analyze_incident(
            title="CPU issue",
            description="High CPU on prod",
        )

        assert analysis1.category == analysis2.category
        assert analysis1.urgency == analysis2.urgency
