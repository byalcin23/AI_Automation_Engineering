"""Text chunking for document processing.

Splits documents into smaller chunks for search while maintaining
context and source information.
"""

from typing import List, TypedDict


class Chunk(TypedDict):
    """Represents a text chunk with metadata."""

    text: str
    source: str
    start_index: int
    end_index: int


def chunk_document(
    content: str,
    source: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[Chunk]:
    """Split a document into overlapping chunks.

    Args:
        content: The full document content.
        source: Source filename for attribution.
        chunk_size: Number of characters per chunk.
        overlap: Number of overlapping characters between chunks.

    Returns:
        List of Chunk dictionaries with text, source, and indices.
    """
    chunks = []
    start_index = 0

    while start_index < len(content):
        end_index = min(start_index + chunk_size, len(content))

        # Try to break at sentence boundary if not at end
        if end_index < len(content):
            # Look back for a period, newline, or sentence ending
            search_end = min(end_index + 50, len(content))
            last_period = content.rfind(".", start_index, search_end)
            last_newline = content.rfind("\n", start_index, search_end)
            boundary = max(last_period, last_newline)

            if boundary > start_index + (chunk_size // 2):
                end_index = boundary + 1

        chunk_text = content[start_index:end_index].strip()

        if chunk_text:
            chunk: Chunk = {
                "text": chunk_text,
                "source": source,
                "start_index": start_index,
                "end_index": end_index,
            }
            chunks.append(chunk)

        # Move start forward by (chunk_size - overlap)
        start_index += chunk_size - overlap

    return chunks
