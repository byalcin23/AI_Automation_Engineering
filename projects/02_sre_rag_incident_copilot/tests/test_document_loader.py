"""Tests for document loading functionality."""

import tempfile
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_loader import load_runbooks, load_single_runbook


class TestDocumentLoader:
    """Tests for document loading functions."""

    def test_load_runbooks_returns_list(self):
        """Test that load_runbooks returns a list of documents."""
        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test markdown files
            (tmppath / "test1.md").write_text("# Test 1\nContent 1")
            (tmppath / "test2.md").write_text("# Test 2\nContent 2")

            # Load
            docs = load_runbooks(tmppath)

            # Assert
            assert isinstance(docs, list)
            assert len(docs) == 2

    def test_load_runbooks_preserves_source(self):
        """Test that source filename is preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "example.md").write_text("Test content")

            docs = load_runbooks(tmppath)

            assert docs[0]["source"] == "example.md"

    def test_load_runbooks_preserves_content(self):
        """Test that document content is preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            content = "# Header\nSome content here"
            (tmppath / "test.md").write_text(content)

            docs = load_runbooks(tmppath)

            assert docs[0]["content"] == content

    def test_load_runbooks_empty_directory(self):
        """Test loading from empty directory returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            docs = load_runbooks(tmppath)
            assert docs == []

    def test_load_runbooks_nonexistent_directory(self):
        """Test loading from nonexistent directory raises error."""
        with pytest.raises(FileNotFoundError):
            load_runbooks(Path("/nonexistent/path"))

    def test_load_single_runbook(self):
        """Test loading a single runbook file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            content = "# Runbook\nInstructions here"
            filepath = tmppath / "runbook.md"
            filepath.write_text(content)

            doc = load_single_runbook(filepath)

            assert doc["source"] == "runbook.md"
            assert doc["content"] == content

    def test_load_single_runbook_nonexistent(self):
        """Test loading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_single_runbook(Path("/nonexistent/runbook.md"))

    def test_load_runbooks_sorted(self):
        """Test that runbooks are loaded in sorted order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create files in random order
            (tmppath / "z_file.md").write_text("Z")
            (tmppath / "a_file.md").write_text("A")
            (tmppath / "m_file.md").write_text("M")

            docs = load_runbooks(tmppath)

            sources = [doc["source"] for doc in docs]
            assert sources == ["a_file.md", "m_file.md", "z_file.md"]
