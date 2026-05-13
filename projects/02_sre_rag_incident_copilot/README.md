# SRE RAG Incident Copilot

A Python-first Retrieval-Augmented Generation (RAG) system for analyzing SRE incidents using local runbook knowledge. Provides grounded, actionable recommendations based on documented procedures.

## Problem Statement

SRE teams face critical time pressure during incidents. Traditional incident response requires:
- Manually searching through documentation
- Pattern matching against past incidents
- Making decisions without full context
- Risk of hallucinated or incorrect recommendations

**Solution**: A grounded RAG system that:
- Automatically retrieves relevant runbooks
- Analyzes incidents using LLM + documentation context
- Provides source-cited recommendations
- Works offline with mock provider, scales with GitHub Models API

## Why This Matters for SRE/DevOps

1. **Faster MTTR (Mean Time To Resolution)**: Immediate access to relevant procedures
2. **Consistency**: Same incident = same recommended approach
3. **Knowledge Preservation**: Institutional knowledge is formalized and searchable
4. **Confidence**: Every recommendation is grounded in documented runbooks
5. **Scaling**: Works for new team members learning on the job

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   CLI / FastAPI                              │
│        (demo, interactive, analyze, HTTP endpoints)          │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│            IncidentCopilot (Orchestrator)                    │
│  • Loads runbooks and creates searchable chunks              │
│  • Routes to search, LLM, and formatting                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
┌───────▼──┐  ┌───▼────┐  ┌──▼────────┐
│ Document │  │ Search │  │ LLM       │
│ Loader   │  │ (TF-IDF)  │ Provider  │
└──────────┘  └────────┘  └───┬──────┘
                               │
                   ┌───────────┼───────────┐
                   │           │           │
              ┌────▼──┐   ┌────▼──┐  ┌───▼────┐
              │ Mock  │   │GitHub │  │Config  │
              │(Test) │   │Models │  │(.env)  │
              └───────┘   └───────┘  └────────┘
```

## Key Features

- **5 Core SRE Runbooks**: Database lag, high CPU, disk full, deployment failure, error spikes
- **TF-IDF Search**: Intelligent retrieval of relevant documentation sections
- **Dual LLM Support**:
  - **Mock Provider** (default): Works immediately without API keys
  - **GitHub Models** (optional): Uses GitHub Copilot Pro token for better analysis
- **Source Attribution**: Every recommendation includes which runbook was used
- **Grounded Responses**: Refuses to generate information not in runbooks
- **Multiple Interfaces**:
  - CLI (demo, interactive, analyze)
  - FastAPI HTTP endpoints
  - Python API (import and use directly)

## Installation

### Prerequisites
- Python 3.9+
- pip or poetry

### Setup

1. **Clone the project** (or navigate to project directory)

2. **Install dependencies**:
```bash
cd projects/02_sre_rag_incident_copilot
pip install -r requirements.txt
```

3. **Create environment file** (optional, for GitHub Models):
```bash
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN if using GitHub Models
```

## Configuration

### Environment Variables

**Default Configuration** (no setup needed):
```bash
LLM_PROVIDER=mock          # Uses mock provider (no API required)
```

**For GitHub Models** (requires GitHub Copilot Pro):
```bash
LLM_PROVIDER=github_models
GITHUB_TOKEN=your_token_here
GITHUB_MODEL=openai/gpt-4o-mini
GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference/chat/completions
```

### How to Get GitHub Token

1. Go to https://github.com/settings/tokens/new
2. Create a token with `repo` and `codespace` scopes
3. Copy the token and add to `.env` file
4. **Security**: Never commit `.env` to version control

## Usage

### CLI Mode - Demo

Analyze sample incidents with one command:
```bash
python src/cli.py demo
```

**Output**:
```
======================================================================
SRE RAG INCIDENT COPILOT - DEMO MODE
======================================================================

──────────────────────────────────────────────────────────────
Incident 1/3: INC-001
──────────────────────────────────────────────────────────────
Title: Database replication lag detected
Description: Alert fired for MySQL replication lag. Primary DB is at 5 seconds lag...

Analysis Results:
  Category: Database Issue
  Urgency: high
  Confidence: 0.82
  Relevant Sources: stream_lag_runbook.md

  First Checks:
    • Check replication status: SHOW SLAVE STATUS\G;
    • Verify network connectivity between primary and replica
    • Check disk I/O on both servers: iostat -x 1

  Action Plan:
    Check query load on primary. Optimize slow queries, add indexes, scale read replicas...

  Escalation: Immediate escalation to database team, consider failover
```

### CLI Mode - Interactive

Analyze custom incidents interactively:
```bash
python src/cli.py interactive
```

**Example Session**:
```
Incident Title: Sudden error spike in API gateway
Incident Description: Error rate jumped from 0.1% to 8.5% in last 15 minutes. No obvious service changes or deployments. Spans show database connection pool exhaustion. 503s being returned.

[Analysis output...]
```

### CLI Mode - Single Analysis

Analyze a specific incident:
```bash
python src/cli.py analyze \
  --title "High CPU on production server" \
  --description "CPU at 95% on prod-app-03. Memory at 87%. Process is main application container."
```

### FastAPI Server

Start the HTTP API server:
```bash
# Install uvicorn if needed
pip install uvicorn

# Start server
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Analyze Incident**:
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database replication lag",
    "description": "Replication lag is 10 seconds behind primary"
  }'
```

**Response**:
```json
{
  "incident_title": "Database replication lag",
  "incident_description": "Replication lag is 10 seconds behind primary",
  "category": "Database Issue",
  "urgency": "high",
  "relevant_sources": ["stream_lag_runbook.md"],
  "action_plan": "1. Check replication status with SHOW SLAVE STATUS...",
  "first_checks": [
    "Check replication status: SHOW SLAVE STATUS\\G;",
    "Verify network connectivity between primary and replica",
    "Check disk I/O on both servers: iostat -x 1"
  ],
  "escalation_recommendation": "Escalate to database team if lag exceeds 30 seconds",
  "confidence_score": 0.82
}
```

### Python API

Use directly in your Python code:
```python
from src.config import Config
from src.copilot import IncidentCopilot
from src.llm_provider import get_llm_provider

# Initialize
Config.validate()
llm_provider = get_llm_provider(
    provider_name=Config.LLM_PROVIDER,
    github_token=Config.GITHUB_TOKEN,
)
copilot = IncidentCopilot(llm_provider=llm_provider)

# Analyze
analysis = copilot.analyze_incident(
    title="Production incident",
    description="Service is returning 500 errors"
)

# Use results
print(f"Category: {analysis.category}")
print(f"Urgency: {analysis.urgency}")
print(f"Action Plan: {analysis.action_plan}")
```

## Example Scenarios

### Scenario 1: Database Issue

**Input**:
```
Title: MySQL replication lag spike
Description: Alert shows 12 second lag between primary and replica. 
Query logs show heavy INSERT/UPDATE activity.
```

**Output**:
```
Category: Database Issue
Urgency: high
Relevant Sources: stream_lag_runbook.md
First Checks:
  • Check replication status
  • Verify network latency
  • Analyze query load on primary
Action Plan: Optimize slow queries, add indexes to hot tables...
Escalation: Contact database team if lag > 30 seconds
Confidence: 0.85
```

### Scenario 2: Infrastructure Issue

**Input**:
```
Title: Disk full warning on logging server
Description: /var/log is at 98% capacity. New logs cannot be written.
Service is becoming unresponsive.
```

**Output**:
```
Category: Infrastructure Issue
Urgency: critical
Relevant Sources: disk_full_runbook.md
First Checks:
  • Check disk usage: df -h
  • Find largest files: du -sh /*
  • Identify culprit service
Action Plan: Archive old logs, configure log rotation, expand storage...
Escalation: Immediate action required, may trigger escalation
Confidence: 0.91
```

## Mock vs. GitHub Models Provider

### Mock Provider (Default)
- **When**: Testing, CI/CD, no API key available
- **Requires**: Nothing (works offline)
- **Accuracy**: Good (keyword-based classification)
- **Speed**: Instant
- **Cost**: Free

**Example Mock Analysis**:
```json
{
  "category": "Performance Issue",
  "urgency": "high",
  "initial_checks": [
    "Check recent changes or deployments",
    "Monitor system resources",
    "Review application logs"
  ],
  "confidence": 0.72
}
```

### GitHub Models Provider
- **When**: Production, need better analysis, have GitHub Copilot Pro
- **Requires**: GITHUB_TOKEN environment variable
- **Accuracy**: Very good (LLM-based with context)
- **Speed**: ~2-3 seconds
- **Cost**: Covered by GitHub Copilot Pro subscription

**Example GitHub Models Analysis**:
```json
{
  "category": "Database Performance Degradation",
  "urgency": "high",
  "action_plan": "1. Immediately check MySQL SHOW SLAVE STATUS to verify lag...",
  "first_checks": [
    "SHOW SLAVE STATUS\\G; on replica to measure lag",
    "Check network latency between primary and replica",
    "Monitor binary log position on primary"
  ],
  "escalation": "If lag exceeds 30s, page on-call DBA",
  "confidence": 0.88
}
```

## Testing

Run comprehensive test suite:
```bash
pytest tests/ -v
```

**Test Coverage**:
- ✓ Document loading and source attribution
- ✓ Search functionality (keyword + TF-IDF)
- ✓ LLM provider interfaces
- ✓ Mock provider keyword detection
- ✓ GitHub Models provider error handling
- ✓ Copilot analysis workflow
- ✓ Edge cases and error scenarios

**Example Test Output**:
```
tests/test_document_loader.py::TestDocumentLoader::test_load_runbooks_returns_list PASSED
tests/test_search.py::TestSearch::test_keyword_search_returns_results PASSED
tests/test_llm_provider.py::TestMockLLMProvider::test_mock_provider_generates_response PASSED
tests/test_copilot.py::TestIncidentCopilot::test_analyze_incident_returns_analysis PASSED
...

======================== 24 passed in 0.45s ========================
```

## Project Structure

```
02_sre_rag_incident_copilot/
├── README.md                      # This file
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
│
├── data/
│   ├── sample_incidents.json      # 5 sample incidents for demo
│   └── runbooks/
│       ├── stream_lag_runbook.md          # Database replication lag
│       ├── high_cpu_runbook.md            # High CPU usage
│       ├── deployment_failure_runbook.md  # Deployment issues
│       └── disk_full_runbook.md           # Disk space exhaustion
│
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── document_loader.py     # Load markdown runbooks
│   ├── chunker.py             # Split docs into chunks
│   ├── search.py              # TF-IDF search
│   ├── llm_provider.py        # LLM provider abstraction
│   ├── copilot.py             # Main incident analysis
│   ├── cli.py                 # Command-line interface
│   └── api.py                 # FastAPI HTTP server
│
└── tests/
    ├── test_document_loader.py
    ├── test_search.py
    ├── test_llm_provider.py
    ├── test_copilot.py
    └── __init__.py
```

## Future Enhancements

### Phase 2: Advanced Capabilities
- **Vector Database**: Upgrade from TF-IDF to embeddings (Chroma, Pinecone)
- **Multi-runbook Context**: Support for >100 runbooks efficiently
- **Incident Correlation**: Link to related incidents from past
- **Automated Remediation**: Execute suggested checks automatically

### Phase 3: Integration
- **Atlassian Rovo Integration**: Use as Rovo skill for incident analysis
- **PagerDuty Integration**: Auto-create incidents with analysis
- **Slack Bot**: `/analyze` command for incident analysis
- **DataDog Integration**: Query metrics for incident context

### Phase 4: AI Ops
- **Predictive Incidents**: ML model predicting issues before they occur
- **Automated Runbook Generation**: LLM creates runbooks from logs
- **Custom Training**: Fine-tune on organization's incident history
- **Observability Integration**: Pull context from Prometheus, logs, traces

## Limitations

1. **Runbook-Only**: Only as good as the runbooks provided
2. **No Real-Time Data**: Doesn't pull live metrics (can be added)
3. **No Automatic Actions**: Recommendations only (safety-first)
4. **Single Incident**: Analyzes one incident at a time (batch coming later)

## Architecture Decisions

### Why No LangChain?
- Simpler dependencies for portfolio project
- More transparent and understandable code
- Easier to modify and extend
- Can add later when needed

### Why TF-IDF Before Vector DB?
- Works great for small-medium runbook sets
- No external dependencies
- Explainable and debuggable
- Perfect for MVP

### Why Mock Provider by Default?
- Works immediately for everyone
- No credential management issues
- Great for testing and CI/CD
- Can always upgrade to GitHub Models

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Load runbooks | <50ms | One-time startup cost |
| Create chunks | <100ms | One-time at startup |
| Search (mock) | ~5ms | Per analysis |
| Mock LLM analysis | <10ms | Instant, no API call |
| GitHub Models | 2-3s | Includes network latency |
| Full analysis (mock) | ~50ms | Start to finish |
| Full analysis (GitHub) | 3-4s | With API latency |

## Contributing

This is part of a portfolio project. For contributions:
1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Add tests for new functionality
4. Ensure 100% test coverage
5. Submit pull request

## License

MIT License - See LICENSE file in parent directory

## Contact

Part of the AI Automation Engineering portfolio project.

For questions, refer to the main [portfolio repository](https://github.com/byalcin23/AI_Automation_Engineering).
