# AI Automation Engineering

A practical portfolio and learning repository focused on **AI Automation Engineering** from a DevOps/SRE perspective.

I am using this repository to build production-style AI automation projects with Python, APIs, workflow automation, RAG, observability, and SRE reliability practices.

## Career Goal

My goal is to move from a traditional **DevOps / Site Reliability Engineer** profile into roles such as:

- AI Automation Engineer
- AI Workflow Engineer
- Agentic Systems Engineer
- AI Platform / Automation Engineer
- SRE with AI Automation focus
- AIOps / Intelligent Automation Engineer

This repository is not focused on training machine learning models from scratch.  
The focus is on building useful, reliable, production-style automation systems using existing LLMs, local models, APIs, internal knowledge, and workflow orchestration.

## Why This Repository Exists

AI automation roles are increasingly asking for a combination of:

- Python automation
- LLM integration
- API-driven workflows
- RAG and internal knowledge search
- Agentic workflows
- n8n / workflow orchestration
- Observability and reliability
- Governance, security, and responsible AI
- Business value and ROI tracking

My existing background is in DevOps, SRE, CI/CD, Kubernetes, observability, production operations, and automation.  
This repository is my structured roadmap to connect that experience with AI automation engineering.

## Current Repository Structure

```text
AI_Automation_Engineering/
├── docs/                 # Notes, architecture decisions, learning documentation
├── examples/             # Small focused examples
├── notebooks/            # Experiments and learning notebooks
├── projects/             # Main portfolio projects
├── tools/                # Reusable Python utilities
├── README.md             # Main roadmap and task menu
├── ROADMAP.md            # Detailed progress tracker
└── requirements.txt      # Python dependencies
```

## API Cost Strategy

This roadmap is designed to work even without paid OpenAI API usage.

Default approach:

1. **Mock LLM mode** first  
   Build the automation logic without depending on an external model.

2. **Local LLM mode with Ollama**  
   Use local models for learning and demos.

3. **GitHub Models mode**  
   Use GitHub Models for free, rate-limited experimentation where possible.

4. **OpenAI API mode as optional**  
   Add OpenAI only as a provider behind an environment variable.

Target design:

```text
LLM_PROVIDER=mock
LLM_PROVIDER=ollama
LLM_PROVIDER=github_models
LLM_PROVIDER=openai
```

Every project should run without paid API usage by default.

## Skill Tree

### 1. Python Automation Foundation

Goal: strengthen Python for backend automation and AI workflows.

Tasks:

- [ ] Create a clean Python project structure
- [ ] Use virtual environments
- [ ] Use `.env` files for configuration
- [ ] Learn `pydantic` for structured data validation
- [ ] Learn `httpx` or `requests` for API calls
- [ ] Learn `pytest` for automated tests
- [ ] Learn basic logging patterns
- [ ] Learn exception handling for production-style scripts
- [ ] Build reusable helper functions under `tools/`

Deliverable:

- [ ] `examples/python_automation_basics/`

Success criteria:

- The project runs with one command
- The code has clear functions
- At least 5 unit tests exist
- No secrets are committed

---

### 2. AI Ticket Classification

Goal: build a simple AI-style classifier for SRE/Jira tickets.

This starts without LLM dependency. First version can be rule-based or scikit-learn based.

Tasks:

- [ ] Create `projects/01_ai_ticket_classifier/`
- [ ] Define sample ticket data in JSON
- [ ] Classify tickets into categories:
  - Incident
  - Deployment
  - Config change
  - Access request
  - Monitoring request
  - Investigation
- [ ] Add priority suggestion:
  - Low
  - Medium
  - High
  - Critical
- [ ] Add confidence score
- [ ] Add recommended next action
- [ ] Add CLI command
- [ ] Add unit tests
- [ ] Add README with examples

Optional LLM extension:

- [ ] Add `mock` provider
- [ ] Add `ollama` provider
- [ ] Add `github_models` provider
- [ ] Add `openai` provider only as optional

Deliverable:

- [ ] `projects/01_ai_ticket_classifier/`

Success criteria:

- Input: ticket title and description
- Output: category, priority, confidence, recommended action
- Works without paid API
- Has clear README and demo output

Example output:

```json
{
  "category": "incident",
  "priority": "high",
  "confidence": 0.86,
  "recommended_action": "Check related monitoring dashboards and recent deployments."
}
```

---

### 3. SRE Runbook Search

Goal: build a local knowledge search tool for SRE runbooks.

First version should be simple and free. Use TF-IDF or keyword search before vector databases.

Tasks:

- [ ] Create `projects/02_sre_runbook_search/`
- [ ] Add sample runbooks under `docs/sample_runbooks/`
- [ ] Build document loader
- [ ] Split documents into chunks
- [ ] Add keyword search
- [ ] Add TF-IDF search with scikit-learn
- [ ] Return top 3 matching runbook sections
- [ ] Add source file name and section title
- [ ] Add CLI command
- [ ] Add tests

Optional vector extension:

- [ ] Add ChromaDB or FAISS
- [ ] Add embeddings
- [ ] Compare keyword search vs vector search

Deliverable:

- [ ] `projects/02_sre_runbook_search/`

Success criteria:

- User can search a problem
- Tool returns relevant runbook sections
- Output always includes source reference
- No LLM needed

---

### 4. SRE RAG Incident Copilot

Goal: combine ticket classification + runbook search + LLM summary.

This is the first proper AI automation portfolio project.

Tasks:

- [ ] Create `projects/03_sre_rag_incident_copilot/`
- [ ] Accept incident title and description
- [ ] Classify incident category and urgency
- [ ] Search relevant runbooks
- [ ] Generate short action plan
- [ ] Include source references
- [ ] Refuse to answer if no relevant source exists
- [ ] Add FastAPI endpoint
- [ ] Add CLI command
- [ ] Add Dockerfile
- [ ] Add unit tests
- [ ] Add demo examples

LLM provider tasks:

- [ ] Implement `mock` provider
- [ ] Implement `ollama` provider
- [ ] Implement `github_models` provider
- [ ] Keep `openai` optional

Deliverable:

- [ ] `projects/03_sre_rag_incident_copilot/`

Success criteria:

- Works locally
- Can run without paid API
- Produces grounded answers
- Shows source documents
- Has a clear architecture diagram

---

### 5. Agentic SRE Workflow Engine

Goal: build a multi-step AI workflow that behaves like an operational assistant.

Tasks:

- [ ] Create `projects/04_agentic_sre_workflow_engine/`
- [ ] Define workflow states:
  - Receive ticket
  - Classify ticket
  - Search runbooks
  - Check mock monitoring data
  - Check mock deployment data
  - Generate action plan
  - Require human approval for risky actions
  - Produce Slack/Jira response
- [ ] Use plain Python state machine first
- [ ] Add LangGraph later if needed
- [ ] Add retry logic
- [ ] Add failure handling
- [ ] Add structured logs
- [ ] Add tests for each workflow step

Deliverable:

- [ ] `projects/04_agentic_sre_workflow_engine/`

Success criteria:

- Workflow can be replayed
- Each step has clear input and output
- Failed steps do not crash the whole system
- Human approval is required before risky actions

---

### 6. n8n AI Ops Automation Pack

Goal: show workflow automation skills using n8n.

Tasks:

- [ ] Create `projects/05_n8n_ai_ops_automation_pack/`
- [ ] Create a webhook workflow
- [ ] Accept a fake Jira ticket payload
- [ ] Call local Python API
- [ ] Generate ticket classification
- [ ] Send formatted Slack-style output
- [ ] Add error workflow
- [ ] Export n8n workflow JSON
- [ ] Document setup steps

Deliverable:

- [ ] `projects/05_n8n_ai_ops_automation_pack/`

Success criteria:

- n8n workflow JSON exists
- Python API can be called from n8n
- Workflow handles success and failure cases
- README includes screenshots or sample output

---

### 7. LLM Observability and Cost Tracking

Goal: apply SRE observability thinking to AI workflows.

Tasks:

- [ ] Create `projects/06_llm_observability_lab/`
- [ ] Log every model request
- [ ] Track provider name
- [ ] Track model name
- [ ] Track latency
- [ ] Track input and output token estimate
- [ ] Track success and failure count
- [ ] Track cost estimate where possible
- [ ] Expose `/metrics` endpoint
- [ ] Add Prometheus compatible metrics
- [ ] Add Grafana dashboard JSON
- [ ] Add failure examples

Deliverable:

- [ ] `projects/06_llm_observability_lab/`

Success criteria:

- Every LLM call has logs
- Metrics are visible
- Dashboard can show latency, errors, token usage, and estimated cost
- This project clearly connects AI automation with SRE experience

---

### 8. AI Synthetic Monitoring Analyst

Goal: turn existing synthetic monitoring experience into an AI automation project.

Tasks:

- [ ] Create `projects/07_ai_synthetic_monitoring_analyst/`
- [ ] Use Playwright or Selenium
- [ ] Open a demo web page
- [ ] Take screenshot
- [ ] Validate page status
- [ ] Detect UI changes
- [ ] Generate short monitoring report
- [ ] Add optional LLM-based analysis
- [ ] Add alert output format
- [ ] Add Dockerfile
- [ ] Add GitHub Actions workflow

Deliverable:

- [ ] `projects/07_ai_synthetic_monitoring_analyst/`

Success criteria:

- Browser automation works
- Monitoring report is generated
- LLM analysis is optional
- Project is safe for public GitHub

---

## Suggested Learning Order

### Month 1

- [ ] Python project structure
- [ ] Ticket classifier
- [ ] Runbook search
- [ ] Unit tests
- [ ] README quality

### Month 2

- [ ] Local LLM with Ollama
- [ ] RAG Incident Copilot
- [ ] FastAPI
- [ ] Docker
- [ ] Source-grounded answers

### Month 3

- [ ] Agentic workflow engine
- [ ] Human approval flow
- [ ] n8n integration
- [ ] Error handling and retries

### Month 4

- [ ] LLM observability
- [ ] Prometheus metrics
- [ ] Grafana dashboard
- [ ] Cost tracking

### Month 5

- [ ] AI synthetic monitoring
- [ ] Playwright or Selenium
- [ ] GitHub Actions
- [ ] Public demo documentation

### Month 6

- [ ] Polish portfolio
- [ ] Add architecture diagrams
- [ ] Add demo GIFs or screenshots
- [ ] Rewrite CV project section
- [ ] Prepare LinkedIn portfolio post

## Portfolio Rules

Every project should include:

- [ ] Clear problem statement
- [ ] Architecture overview
- [ ] How to run locally
- [ ] Example input
- [ ] Example output
- [ ] Tests
- [ ] Docker support where useful
- [ ] No secrets
- [ ] No company data
- [ ] Public-safe sample data
- [ ] Short explanation of business value

## Recommended First Task

Start with:

```text
projects/01_ai_ticket_classifier/
```

Reason:

- It is simple
- It is Python-first
- It does not require paid API
- It connects directly to SRE work
- It becomes the first building block for all later projects

## Progress Tracker

### Foundation

- [ ] Python project template created
- [ ] `.env.example` added
- [ ] `requirements.txt` cleaned
- [ ] `pytest` configured
- [ ] Basic CI added with GitHub Actions

### Project 1: AI Ticket Classifier

- [ ] Sample tickets added
- [ ] Rule-based classifier added
- [ ] CLI added
- [ ] Tests added
- [ ] README added
- [ ] Optional LLM provider interface added

### Project 2: SRE Runbook Search

- [ ] Sample runbooks added
- [ ] Document loader added
- [ ] Chunking added
- [ ] Search function added
- [ ] CLI added
- [ ] Tests added

### Project 3: SRE RAG Incident Copilot

- [ ] FastAPI app added
- [ ] Classifier integrated
- [ ] Search integrated
- [ ] LLM provider integrated
- [ ] Source-grounded response added
- [ ] Dockerfile added

### Project 4: Agentic SRE Workflow Engine

- [ ] Workflow states defined
- [ ] State machine implemented
- [ ] Mock tools added
- [ ] Human approval step added
- [ ] Retry logic added
- [ ] Tests added

### Project 5: n8n AI Ops Automation Pack

- [ ] n8n installed locally
- [ ] Webhook workflow created
- [ ] Python API connected
- [ ] Workflow JSON exported
- [ ] Setup documentation added

### Project 6: LLM Observability Lab

- [ ] Request logging added
- [ ] Latency tracking added
- [ ] Token estimate added
- [ ] Prometheus metrics added
- [ ] Grafana dashboard added

### Project 7: AI Synthetic Monitoring Analyst

- [ ] Browser automation added
- [ ] Screenshot capture added
- [ ] Validation logic added
- [ ] Report generation added
- [ ] Optional LLM analysis added

## Final Portfolio Outcome

After completing this roadmap, this repository should demonstrate:

- Python automation engineering
- AI workflow design
- LLM integration
- RAG and internal knowledge search
- Agentic automation
- n8n orchestration
- AI observability
- SRE-style reliability thinking
- Public, production-style project documentation

## Status

Current status: Active learning and portfolio development  
Main focus: Python-first AI automation for SRE and business workflows  
Last updated: May 2026
