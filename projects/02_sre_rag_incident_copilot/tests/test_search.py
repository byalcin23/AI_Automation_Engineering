"""Tests for search functionality."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from search import keyword_search, tfidf_search


class TestSearch:
    """Tests for search functions."""

    @pytest.fixture
    def sample_chunks(self):
        """Provide sample chunks for testing."""
        return [
            {
                "text": "Database replication lag is a critical issue affecting read performance",
                "source": "db_runbook.md",
            },
            {
                "text": "High CPU usage typically indicates memory leaks or inefficient queries",
                "source": "cpu_runbook.md",
            },
            {
                "text": "Disk space can fill quickly with log files and temporary data",
                "source": "disk_runbook.md",
            },
            {
                "text": "Deployment failures occur due to health check timeouts",
                "source": "deploy_runbook.md",
            },
        ]

    def test_keyword_search_returns_results(self, sample_chunks):
        """Test that keyword search returns relevant results."""
        results = keyword_search("database replication", sample_chunks)

        assert len(results) > 0
        assert results[0]["source"] == "db_runbook.md"

    def test_keyword_search_respects_top_k(self, sample_chunks):
        """Test that top_k parameter is respected."""
        results = keyword_search("database", sample_chunks, top_k=1)
        assert len(results) == 1

    def test_keyword_search_empty_query(self, sample_chunks):
        """Test keyword search with empty query."""
        results = keyword_search("", sample_chunks)
        assert results == []

    def test_keyword_search_no_matches(self, sample_chunks):
        """Test keyword search with no matches."""
        results = keyword_search("kubernetes prometheus grafana", sample_chunks)
        assert len(results) == 0

    def test_keyword_search_case_insensitive(self, sample_chunks):
        """Test that search is case-insensitive."""
        results1 = keyword_search("DATABASE", sample_chunks)
        results2 = keyword_search("database", sample_chunks)

        assert len(results1) == len(results2)
        assert results1[0]["source"] == results2[0]["source"]

    def test_keyword_search_returns_truncated_text(self, sample_chunks):
        """Test that search results are truncated."""
        results = keyword_search("database", sample_chunks)
        # Result text should be max 500 chars
        assert len(results[0]["text"]) <= 500

    def test_tfidf_search_returns_results(self, sample_chunks):
        """Test that TF-IDF search returns relevant results."""
        results = tfidf_search("database replication", sample_chunks)

        assert len(results) > 0
        assert results[0]["source"] == "db_runbook.md"

    def test_tfidf_search_respects_top_k(self, sample_chunks):
        """Test that TF-IDF top_k parameter is respected."""
        results = tfidf_search("database", sample_chunks, top_k=2)
        assert len(results) <= 2

    def test_tfidf_search_scoring_order(self, sample_chunks):
        """Test that TF-IDF results are ordered by score."""
        results = tfidf_search("database", sample_chunks)

        for i in range(len(results) - 1):
            assert results[i]["score"] >= results[i + 1]["score"]

    def test_tfidf_search_empty_query(self, sample_chunks):
        """Test TF-IDF search with empty query."""
        results = tfidf_search("", sample_chunks)
        assert results == []

    def test_search_results_contain_source(self, sample_chunks):
        """Test that search results include source information."""
        results = keyword_search("database", sample_chunks)

        assert "source" in results[0]
        assert results[0]["source"] in [c["source"] for c in sample_chunks]

    def test_search_results_contain_score(self, sample_chunks):
        """Test that search results include scores."""
        results = keyword_search("database", sample_chunks)

        assert "score" in results[0]
        assert isinstance(results[0]["score"], (int, float))
