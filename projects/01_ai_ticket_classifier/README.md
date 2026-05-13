# AI Ticket Classifier

**A rule-based SRE/infrastructure ticket classifier built with Python.**

This is the first portfolio project from the AI Automation Engineering roadmap. It demonstrates the ability to build intelligent classification systems without external API dependencies.

## Problem Statement

SRE and infrastructure teams receive tickets from multiple sources (Jira, Pagerduty, email) with varying levels of urgency and different action requirements. Manually triaging tickets is:

- Time-consuming
- Error-prone
- Inconsistent across team members

**Solution**: An automated classifier that:
- Categorizes tickets by type
- Assigns priority levels
- Provides confidence scores
- Recommends next actions

## Features

### ✅ No External Dependencies
- Rule-based classification (no LLM API required)
- Works offline
- Zero API costs
- Runs with just Python standard library

### 📊 Classification Categories
1. **Incident** - Production issues, system outages, performance problems
2. **Deployment** - Release planning, version upgrades, rollouts
3. **Config Change** - Monitoring updates, threshold changes, policy updates
4. **Access Request** - Permissions, credentials, SSH keys
5. **Investigation** - Root cause analysis, debugging, security review

### 🎯 Priority Levels
- **Critical** - P0, production-down scenarios
- **High** - P1, significant impact
- **Medium** - P2, moderate impact
- **Low** - P3, minor or non-urgent

### 📈 Output
Every classification includes:
- **Category** - Ticket type
- **Priority** - Urgency level
- **Confidence** - 0.0 to 1.0 score
- **Recommended Action** - Specific next steps

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Demo Mode (Sample Tickets)
```bash
python cli.py demo
```

Output:
```
============================================================
AI TICKET CLASSIFIER - Sample Tickets Demo
============================================================

[1/10] JIRA-001: Database replication lag detected on prod-db-02

  Category:            INCIDENT
  Priority:            HIGH
  Confidence:          86%
  Recommended Action:  1. Monitor dashboards. 2. Check logs for errors. 3. Investigate related components.
------------------------------------------------------------
```

#### Interactive Mode
```bash
python cli.py interactive
```

Example:
```
============================================================
AI TICKET CLASSIFIER - Interactive Mode
============================================================

Enter ticket title: API timeout errors in production

Enter ticket description: Requests to /api/users timing out after 60s. Load average normal. 
Started 5 min ago. P1 impact.

  Category:            INCIDENT
  Priority:            CRITICAL
  Confidence:          92%
  Recommended Action:  1. Check status dashboards immediately. 2. Page on-call engineer. 3. Review recent deployments.
------------------------------------------------------------
```

#### Help
```bash
python cli.py help
```

## Example Outputs

### Example 1: Critical Production Incident
```json
{
  "category": "incident",
  "priority": "critical",
  "confidence": 0.94,
  "recommended_action": "1. Check status dashboards immediately. 2. Page on-call engineer. 3. Review recent deployments."
}
```

### Example 2: Config Change
```json
{
  "category": "config_change",
  "priority": "medium",
  "confidence": 0.78,
  "recommended_action": "1. Validate change in test environment. 2. Plan monitoring."
}
```

### Example 3: Access Request
```json
{
  "category": "access_request",
  "priority": "low",
  "confidence": 0.85,
  "recommended_action": "1. Queue for next access review batch."
}
```

## Architecture

### Core Components

```
classifier.py
├── TicketClassifier
│   ├── _score_category()       # Match keywords against category
│   ├── _determine_priority()   # Assess urgency indicators
│   └── _get_recommended_action() # Generate action based on classification
└── ClassificationResult (dataclass)
    ├── category: str
    ├── priority: str
    ├── confidence: float
    └── recommended_action: str

cli.py
├── classify_sample_tickets()   # Run demo
├── classify_ticket_interactive() # Interactive mode
└── main()                        # Entry point
```

### Classification Algorithm

1. **Keyword Matching**: Combine ticket title + description
2. **Category Scoring**: Count keyword matches for each category
3. **Normalize Score**: 0.0-1.0 confidence range
4. **Determine Priority**: Look for P0/P1/P2/P3 or severity keywords
5. **Combine Scores**: Weighted average of category + priority confidence
6. **Generate Action**: Look up recommended action from decision matrix

### Decision Matrix

Actions are determined by (category, priority) tuple. For example:

| Category | Priority | Action |
|----------|----------|--------|
| incident | critical | "Page on-call engineer" |
| incident | high | "Check logs immediately" |
| deployment | high | "Verify tests pass and follow deployment procedure" |
| config_change | medium | "Validate in test environment first" |
| access_request | low | "Queue for next batch" |

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test
```bash
pytest tests/test_classifier.py::TestTicketClassifier::test_classify_incident_high_priority -v
```

### Test Coverage
The project includes:
- ✅ 11+ unit tests
- ✅ Incident classification tests
- ✅ All category tests
- ✅ Priority level tests
- ✅ Confidence score validation
- ✅ Edge case handling
- ✅ Consistency tests

### Sample Test
```python
def test_classify_incident_high_priority(classifier):
    """Test incident classification with high priority."""
    result = classifier.classify(
        title="Production database down",
        description="Database server is not responding. P1 outage affecting all users."
    )

    assert result.category == "incident"
    assert result.priority == "critical"
    assert result.confidence > 0.5
    assert result.recommended_action
```

## Project Structure

```
01_ai_ticket_classifier/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment config template
├── __init__.py                  # Package init
├── classifier.py                # Main classification logic
├── cli.py                        # Command-line interface
├── sample_tickets.json          # 10 sample tickets
└── tests/
    ├── __init__.py
    ├── test_classifier.py       # Classifier tests
    └── test_cli.py              # CLI tests
```

## Future Extensions

This is a rule-based MVP. Future versions can add:

### Phase 2: LLM Integration
- Add optional LLM provider interface
- Support mock provider for demos
- Support Ollama for local models
- Support GitHub Models for free tier
- Keep rule-based as fallback

### Phase 3: Learning
- Track actual SRE ticket classifications
- Calculate category confidence from historical data
- Build training dataset from real incidents
- Fine-tune priorities based on actual impact

### Phase 4: Advanced Features
- RAG integration for related tickets
- Batch classification
- REST API endpoint
- Slack/Teams integration
- Jira webhook handler

## Success Criteria Met

✅ **Input**: Ticket title and description  
✅ **Output**: Category, priority, confidence, recommended action  
✅ **Works offline**: No API required  
✅ **Has tests**: 11+ unit tests  
✅ **Clear README**: This file with examples  
✅ **Portfolio-friendly**: Public-safe, clean code  
✅ **Runnable**: `python cli.py demo` works  
✅ **Extensible**: Foundation for LLM integration  

## Running in Your Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python cli.py demo
```

### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python cli.py demo
```

## Business Value

This project demonstrates:

1. **Automation**: Eliminates manual ticket triage
2. **Consistency**: Applies rules uniformly across all tickets
3. **Efficiency**: Instant classification vs manual review
4. **Scalability**: Can handle high ticket volume
5. **Cost**: No API dependencies, runs anywhere

## Skills Demonstrated

- ✅ Python engineering (clean code, type hints, docstrings)
- ✅ Software design patterns (dataclasses, strategy pattern)
- ✅ Testing (pytest, unit tests, edge cases)
- ✅ CLI development (user-friendly interfaces)
- ✅ Documentation (clear examples, architecture)
- ✅ DevOps/SRE domain knowledge

## Notes

- **Keywords**: The classifier uses a curated keyword list. Can be expanded based on domain knowledge.
- **Confidence**: Confidence score reflects keyword match density, not probability. It indicates how many category indicators were found.
- **Extensibility**: Designed to be a foundation for future LLM integration without breaking changes.

## License

MIT License - see repository for details.

---

**Next Project**: [02 - SRE Runbook Search](../02_sre_runbook_search/)

**Status**: ✅ Complete and tested  
**Last Updated**: May 2026
