---
title: Founderos
emoji: 💻
colorFrom: blue
colorTo: yellow
sdk: docker
pinned: false
---
# FounderOS — Multi-Agent AI Startup Platform

> Describe your startup idea in 2 sentences. Three specialized AI agents will analyze the market, validate your users, and write your PRD — in minutes.

---

## Architecture

```
founderos/
├── backend/                    # FastAPI + Python agents
│   ├── main.py                 # API entry point (SSE streaming)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── orchestrator/
│   │   └── graph.py            # Sequences agents, manages shared context
│   ├── agents/
│   │   ├── base_agent.py       # Abstract base — wraps Claude API
│   │   ├── strategist.py       # Market sizing + competitive analysis
│   │   ├── user_research.py    # Persona generation + simulated interviews
│   │   └── product.py          # PRD + feature roadmap + GTM
│   ├── eval/
│   │   ├── scorer.py           # Per-agent quality scoring rubric
│   │   └── logger.py           # SQLite session logging
│   └── schemas/
│       └── brief.py            # Pydantic output models
│
├── frontend/
│   └── index.html              # Single-file React-like UI (4 screens)
│
├── infra/
│   └── docker-compose.yml      # API + Frontend containers
│
├── .env.example
└── README.md
```

## Agent Pipeline

```
User Idea
    │
    ▼
Orchestrator (graph.py)
    ├── 1. Strategist Agent ──────► Market data: TAM/SAM/SOM, competitors, gaps
    │        └── result passed to ↓
    ├── 2. User Research Agent ───► 3 personas + simulated interviews + pain points
    │        └── result passed to ↓
    └── 3. Product Agent ─────────► PRD: features, MVP scope, GTM, milestones
                 └── all results assembled into Startup Brief
                              └── Eval scorer grades each agent (A–F)
                                           └── Logged to SQLite
```

## Quick Start

### Option A: Local Python (recommended for development)

**Prerequisites:** Python 3.11+

```bash
# 1. Clone / unzip the project
cd founderos/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
cp ../.env.example ../.env
# Edit .env and add your Anthropic API key

export ANTHROPIC_API_KEY=your_key_here

# 4. Run the API
uvicorn main:app --reload --port 8000

# 5. Open the frontend
# Open frontend/index.html in your browser
# (or serve it: python -m http.server 3000 --directory ../frontend)
```

### Option B: Docker Compose

```bash
cd founderos

# Set your API key
cp .env.example .env
# Edit .env

# Run everything
cd infra
docker-compose up --build

# Frontend: http://localhost:3000
# API:      http://localhost:8000
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | Your Anthropic API key (get one at console.anthropic.com) |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/launch` | Launch agents (SSE stream) |
| `GET` | `/api/sessions` | List all past sessions |
| `GET` | `/api/health` | Detailed health status |

### POST /api/launch

**Request body:**
```json
{
  "idea": "A platform that helps solo founders validate startup ideas using AI agents",
  "industry": "saas"
}
```

**Streams Server-Sent Events:**
```
data: {"type": "session_start", "session_id": "..."}
data: {"type": "orchestrator", "message": "Dispatching agents..."}
data: {"type": "agent_status", "agent": "Strategist", "status": "thinking", "message": "..."}
data: {"type": "memory_update", "key": "TAM", "value": "$47B", "agent": "Strategist"}
data: {"type": "agent_status", "agent": "Strategist", "status": "done", "message": "..."}
data: {"type": "brief_ready", "data": {...}, "eval": {...}}
data: {"type": "done"}
```

## UI Screens

| Screen | Description |
|--------|-------------|
| **Idea Intake** | Minimal form — idea textarea + industry dropdown + Launch button |
| **Agent Workspace** | Live dashboard: agent status sidebar, streaming activity feed, shared memory panel |
| **Startup Brief** | Full structured output: Executive Summary, Market Analysis, Personas, Feature Roadmap, GTM |
| **Sessions** | Table of all past runs with eval scores per agent |

## Eval Scoring

Each agent is graded A–F based on output completeness:

| Agent | Checks |
|-------|--------|
| Strategist | Market summary, TAM present, 3+ competitors, gaps & trends |
| User Research | 3+ personas, interview insights, pain points, JTBD, buying triggers |
| Product | 5+ features, product named, MVP scoped, GTM defined, wireframes |

## Tech Stack

| Layer | Choice |
|-------|--------|
| LLM | Claude Sonnet via Anthropic API |
| Backend | FastAPI + SSE streaming |
| Frontend | Vanilla HTML/JS (single file, no build step) |
| Storage | SQLite (sessions) |
| Containerization | Docker + nginx |

## Adding More Agents

The architecture is designed for easy extension. To add a new agent:

1. Create `backend/agents/your_agent.py` extending `BaseAgent`
2. Implement `async def run(self, context: dict) -> AsyncGenerator[dict, None]`
3. Add it to `orchestrator/graph.py` after the existing agents
4. Pass results into `context` for downstream agents to use
5. Add it to `eval/scorer.py` scoring rubric

## License

MIT

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
