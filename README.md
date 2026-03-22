# KLARA Greenhouse

**Commercial Wedge App** — Help a Nova Scotian go from idea → actionable greenhouse build plan → next step (DIY or contractor).

## Quick Start

```bash
# 1. Create virtual env
python -m venv .venv
.venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env
copy .env.example .env

# 4. Run
python -m uvicorn app.main:app --reload --port 8100
```

Open **http://localhost:8100** and complete the guided workflow.

## What It Does

1. **Intake** — Guided form: budget, space, location, use case, experience
2. **Suitability Check** — Climate zone + space + budget validation
3. **Build Plan** — Greenhouse type, size, materials, foundation recommendation
4. **Cost & Timeline** — Materials breakdown, labor estimate, build timeline
5. **Action** — Request Quote / Get DIY Plan ($29) / Connect to Builder

## Stack

- **Backend**: FastAPI + SQLAlchemy (SQLite)
- **Frontend**: Jinja2 templates + vanilla JS
- **Data**: Hardcoded Nova Scotia greenhouse knowledge (no LLM)

## Revenue Model

- **Request a Quote** → contractor connection (lead gen)
- **Get DIY Plan** → $29 detailed plan download
- **Connect to Builder** → partner referral
