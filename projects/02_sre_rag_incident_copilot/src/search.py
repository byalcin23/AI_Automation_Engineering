"""Search functionality for runbook chunks.

Provides keyword-based search with TF-IDF scoring for finding
relevant documentation chunks.
"""

import math
from collections import Counter
from typing import List, TypedDict


class SearchResult(TypedDict):
    """Represents a search result."""

    text: str
    source: str
    score: float


def keyword_search(
    query: str,
    chunks: List[dict],
    top_k: int = 3,
) -> List[SearchResult]:
    """Simple keyword-based search through chunks.

    Args:
        query: Search query string.
        chunks: List of chunk dictionaries with 'text' and 'source'.
        top_k: Number of top results to return.

    Returns:
        List of SearchResult dictionaries sorted by score (highest first).
    """
    query_terms = _normalize_text(query).split()

    if not query_terms:
        return []

    results = []

    for chunk in chunks:
        chunk_text = _normalize_text(chunk["text"])
        score = 0

        for term in query_terms:
            if term in chunk_text:
                # Count occurrences
                count = chunk_text.count(term)
                score += count

        if score > 0:
            result: SearchResult = {
                "text": chunk["text"][:500],  # Truncate for readability
                "source": chunk["source"],
                "score": float(score),
            }
            results.append(result)

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]


def tfidf_search(
    query: str,
    chunks: List[dict],
    top_k: int = 3,
) -> List[SearchResult]:
    """TF-IDF based search through chunks.

    Args:
        query: Search query string.
        chunks: List of chunk dictionaries with 'text' and 'source'.
        top_k: Number of top results to return.

    Returns:
        List of SearchResult dictionaries sorted by score (highest first).
    """
    query_terms = _normalize_text(query).split()

    if not query_terms:
        return []

    # Build vocabulary and term frequencies
    all_terms = set()
    chunk_terms = []

    for chunk in chunks:
        terms = _normalize_text(chunk["text"]).split()
        chunk_terms.append(Counter(terms))
        all_terms.update(terms)

    # Calculate IDF for query terms
    doc_count_with_term = {}
    for term in query_terms:
        count = sum(1 for ct in chunk_terms if term in ct)
        doc_count_with_term[term] = max(count, 1)

    # Calculate TF-IDF scores
    results = []
    total_chunks = len(chunks)

    for i, chunk in enumerate(chunks):
        chunk_counter = chunk_terms[i]
        score = 0

        for term in query_terms:
            # TF: term frequency in this chunk
            tf = chunk_counter.get(term, 0)

            # IDF: inverse document frequency
            idf = math.log(total_chunks / doc_count_with_term[term])

            score += tf * idf

        if score > 0:
            result: SearchResult = {
                "text": chunk["text"][:500],  # Truncate for readability
                "source": chunk["source"],
                "score": score,
            }
            results.append(result)

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]


def _normalize_text(text: str) -> str:
    """Normalize text for search.

    Args:
        text: Raw text to normalize.

    Returns:
        Normalized text (lowercase, no punctuation).
    """
    # Convert to lowercase
    text = text.lower()

    # Remove common punctuation
    for char in ".,:;!?\"'()[]{}":
        text = text.replace(char, " ")

    return text
