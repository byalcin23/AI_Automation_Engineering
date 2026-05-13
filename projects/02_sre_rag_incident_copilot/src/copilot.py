"""SRE RAG Incident Copilot core logic.

Orchestrates document loading, search, and LLM-based incident analysis
to provide grounded, actionable recommendations.
"""

import json
from dataclasses import dataclass
from typing import List, Optional

from chunker import Chunk, chunk_document
from config import Config
from document_loader import Document, load_runbooks
from llm_provider import BaseLLMProvider, LLMResponse
from search import SearchResult, tfidf_search


@dataclass
class IncidentAnalysis:
    """Result of incident analysis."""

    incident_title: str
    incident_description: str
    category: str
    urgency: str
    relevant_sources: List[str]
    action_plan: str
    first_checks: List[str]
    escalation_recommendation: str
    confidence_score: float


class IncidentCopilot:
    """SRE Incident Copilot for analyzing incidents and recommending actions."""

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        runbooks_dir: str = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        top_k_results: int = 3,
    ):
        """Initialize the incident copilot.

        Args:
            llm_provider: Configured LLM provider instance.
            runbooks_dir: Path to runbooks directory (uses Config default if None).
            chunk_size: Size of text chunks for search.
            chunk_overlap: Overlap between chunks.
            top_k_results: Number of top search results to return.
        """
        self.llm_provider = llm_provider
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k_results = top_k_results

        # Load and chunk runbooks
        if runbooks_dir is None:
            runbooks_dir = Config.RUNBOOKS_DIR
        else:
            from pathlib import Path

            runbooks_dir = Path(runbooks_dir)

        self.documents = load_runbooks(runbooks_dir)
        self.chunks = self._create_chunks()

    def _create_chunks(self) -> List[Chunk]:
        """Create searchable chunks from all documents.

        Returns:
            List of chunks with text and source information.
        """
        all_chunks = []

        for doc in self.documents:
            chunks = chunk_document(
                doc["content"],
                doc["source"],
                chunk_size=self.chunk_size,
                overlap=self.chunk_overlap,
            )
            all_chunks.extend(chunks)

        return all_chunks

    def analyze_incident(
        self,
        title: str,
        description: str,
    ) -> IncidentAnalysis:
        """Analyze an incident and generate recommendations.

        Args:
            title: Incident title/summary.
            description: Detailed incident description.

        Returns:
            IncidentAnalysis with grounded recommendations.
        """
        # Search for relevant runbooks
        query = f"{title} {description}"
        search_results = tfidf_search(
            query,
            self.chunks,
            top_k=self.top_k_results,
        )

        # Extract unique sources
        relevant_sources = list(set(r["source"] for r in search_results))

        # Prepare context for LLM
        runbook_context = self._prepare_runbook_context(search_results)

        # Generate analysis using LLM
        llm_analysis = self._generate_llm_analysis(
            title,
            description,
            runbook_context,
            search_results,
        )

        # Parse LLM response
        parsed = self._parse_llm_response(llm_analysis["content"])

        return IncidentAnalysis(
            incident_title=title,
            incident_description=description,
            category=parsed.get("category", "Unknown"),
            urgency=parsed.get("urgency", "medium"),
            relevant_sources=relevant_sources,
            action_plan=parsed.get("action_plan", ""),
            first_checks=parsed.get("first_checks", []),
            escalation_recommendation=parsed.get("escalation", ""),
            confidence_score=parsed.get("confidence", 0.0),
        )

    def _prepare_runbook_context(self, search_results: List[SearchResult]) -> str:
        """Prepare context from search results for LLM.

        Args:
            search_results: List of relevant chunks from search.

        Returns:
            Formatted context string for LLM.
        """
        if not search_results:
            return "No relevant runbooks found. Manual investigation required."

        context = "Relevant Runbook Sections:\n\n"

        for i, result in enumerate(search_results, 1):
            context += f"[Source: {result['source']}]\n"
            context += f"{result['text']}\n"
            context += "-" * 40 + "\n\n"

        return context

    def _generate_llm_analysis(
        self,
        title: str,
        description: str,
        runbook_context: str,
        search_results: List[SearchResult],
    ) -> LLMResponse:
        """Generate LLM analysis of the incident.

        Args:
            title: Incident title.
            description: Incident description.
            runbook_context: Context from relevant runbooks.
            search_results: Search results for confidence calculation.

        Returns:
            LLM response with analysis.
        """
        system_prompt = (
            "You are an expert SRE (Site Reliability Engineer) incident analyst. "
            "Analyze the incident using the provided runbook context. "
            "Be grounded in the runbooks - do not invent solutions. "
            "If no relevant runbook is found, state that clearly. "
            "Provide structured, actionable recommendations."
        )

        user_message = (
            f"Analyze this incident:\n\n"
            f"Title: {title}\n"
            f"Description: {description}\n\n"
            f"Relevant Documentation:\n{runbook_context}\n\n"
            f"Provide your analysis in JSON format with keys: "
            f"category, urgency (critical/high/medium/low), "
            f"action_plan, first_checks (list), escalation, confidence (0.0-1.0)"
        )

        return self.llm_provider.generate(system_prompt, user_message)

    def _parse_llm_response(self, response_text: str) -> dict:
        """Parse LLM response to extract structured data.

        Args:
            response_text: Raw LLM response text.

        Returns:
            Parsed dictionary with analysis fields.
        """
        try:
            # Try to extract JSON from response
            json_str = response_text

            # If response contains JSON block, extract it
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]

            parsed = json.loads(json_str.strip())
            return parsed

        except (json.JSONDecodeError, IndexError, AttributeError):
            # Fallback if parsing fails
            return {
                "category": "Unknown",
                "urgency": "medium",
                "action_plan": "Unable to parse LLM response. Manual review required.",
                "first_checks": ["Review incident logs", "Check metrics"],
                "escalation": "Escalate to on-call engineer",
                "confidence": 0.3,
            }
