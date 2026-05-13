"""Document loader for markdown runbooks.

Loads and parses markdown files from the runbooks directory,
maintaining source filename information.
"""

from pathlib import Path
from typing import List, TypedDict


class Document(TypedDict):
    """Represents a document with content and source."""

    content: str
    source: str


def load_runbooks(runbooks_dir: Path) -> List[Document]:
    """Load all markdown runbooks from a directory.

    Args:
        runbooks_dir: Path to directory containing markdown files.

    Returns:
        List of Document dictionaries with content and source filename.

    Raises:
        FileNotFoundError: If runbooks directory does not exist.
    """
    if not runbooks_dir.exists():
        raise FileNotFoundError(f"Runbooks directory not found: {runbooks_dir}")

    documents = []
    markdown_files = sorted(runbooks_dir.glob("*.md"))

    for md_file in markdown_files:
        content = md_file.read_text(encoding="utf-8")
        document: Document = {
            "content": content,
            "source": md_file.name,
        }
        documents.append(document)

    return documents


def load_single_runbook(runbook_path: Path) -> Document:
    """Load a single markdown runbook.

    Args:
        runbook_path: Path to the markdown file.

    Returns:
        Document dictionary with content and source filename.

    Raises:
        FileNotFoundError: If runbook file does not exist.
    """
    if not runbook_path.exists():
        raise FileNotFoundError(f"Runbook not found: {runbook_path}")

    content = runbook_path.read_text(encoding="utf-8")
    return {
        "content": content,
        "source": runbook_path.name,
    }
