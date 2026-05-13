"""FastAPI application for SRE RAG Incident Copilot."""

import sys
from pathlib import Path
from typing import List, Optional

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import Config
from copilot import IncidentCopilot
from llm_provider import get_llm_provider


class IncidentRequest(BaseModel):
    """Request model for incident analysis."""

    title: str
    description: str


class FirstCheck(BaseModel):
    """First check item."""

    text: str


class AnalysisResponse(BaseModel):
    """Response model for incident analysis."""

    incident_title: str
    incident_description: str
    category: str
    urgency: str
    relevant_sources: List[str]
    action_plan: str
    first_checks: List[str]
    escalation_recommendation: str
    confidence_score: float


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    llm_provider: str


# Initialize app and copilot
app = FastAPI(
    title="SRE RAG Incident Copilot",
    description="Analyzes SRE incidents using grounded runbook knowledge",
    version="1.0.0",
)

# Initialize global copilot instance
_copilot: Optional[IncidentCopilot] = None


@app.on_event("startup")
def startup():
    """Initialize copilot on app startup."""
    global _copilot

    Config.validate()

    llm_provider = get_llm_provider(
        provider_name=Config.LLM_PROVIDER,
        github_token=Config.GITHUB_TOKEN,
        github_model=Config.GITHUB_MODEL,
        github_endpoint=Config.GITHUB_MODELS_ENDPOINT,
    )

    _copilot = IncidentCopilot(
        llm_provider=llm_provider,
        runbooks_dir=str(Config.RUNBOOKS_DIR),
    )


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Check API health status.

    Returns:
        HealthResponse with status and provider info.
    """
    return {
        "status": "ok",
        "llm_provider": Config.LLM_PROVIDER,
    }


@app.post("/analyze", response_model=AnalysisResponse)
def analyze_incident(request: IncidentRequest):
    """Analyze an incident and generate recommendations.

    Args:
        request: IncidentRequest with title and description.

    Returns:
        AnalysisResponse with analysis results.

    Raises:
        HTTPException: If analysis fails.
    """
    if not _copilot:
        raise HTTPException(status_code=500, detail="Copilot not initialized")

    if not request.title or not request.description:
        raise HTTPException(
            status_code=400,
            detail="Both title and description are required",
        )

    try:
        analysis = _copilot.analyze_incident(
            title=request.title,
            description=request.description,
        )

        return {
            "incident_title": analysis.incident_title,
            "incident_description": analysis.incident_description,
            "category": analysis.category,
            "urgency": analysis.urgency,
            "relevant_sources": analysis.relevant_sources,
            "action_plan": analysis.action_plan,
            "first_checks": analysis.first_checks,
            "escalation_recommendation": analysis.escalation_recommendation,
            "confidence_score": analysis.confidence_score,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
