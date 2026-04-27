# Klara Greenhouse

**A decision-support layer for Nova Scotia’s protected-growing ecosystem.**

Klara helps growers, serious home growers, buyers, suppliers, and institutional partners move from fragmented options to viable next steps. Klara does not replace markets, advisers, or extension services. It suggests feasible paths through the network that already exists — including local suppliers, farmers’ markets, food hubs, advisory bodies, applied-research partners, and commercialization channels.

Klara suggests; humans decide.

## What Klara Does

Klara is not a listing site. It suggests feasible paths through five functions:
1. **Grower Improvement** — Viable next actions based on current scale, season, inventory, and channel access
2. **Prosumer Setup** — Structured paths from intention to confident decision for households and new growers
3. **Forward-Demand Declaration** — Translates buyer needs (restaurants, institutions) into grower-actionable signals
4. **Supplier/Advisory Routing** — Suggests vetted suppliers and extension resources at the right moment
5. **Excess-Supply Commercialization** — Routes overflow into channels with inventory gaps (nearby markets, food hubs, CSA)

## Quick Start (Presentation Deck)

**Live Streamlit App:** [PASTE CONFIRMED STREAMLIT URL HERE]
*(If the link fails, log into Streamlit Cloud, verify the app visibility is set to Public, and open it directly from the dashboard: `klara-greenhouse · main · presentation/streamlit_app.py`)*

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run presentation/streamlit_app.py
```

Open **http://localhost:8501** to view the PIVP Project Brief.

## Quick Start (Application)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --port 8100
```

Open **http://localhost:8100** for the guided decision-support flow.

## Stack

- **Presentation**: Streamlit (PIVP project brief / stakeholder deck)
- **Application**: FastAPI + SQLAlchemy (SQLite)
- **Frontend**: Jinja2 templates + vanilla JS
- **Data**: Nova Scotia-specific greenhouse knowledge (no LLM)

## Reference Documents

See the `/docs` folder for detailed research, partner maps, and strategic memos:
- [Founder Brief](docs/founder_brief.md)
- [Partnerships](docs/partnerships.md)
- [Who Benefits](docs/who_benefits.md)
- [Commercialization & Excess Supply](docs/commercialization_excess_supply.md)
- [Stakeholder Map](docs/stakeholder_map.md)
- [Gap Memo](docs/gap_memo.md)

## Territory Acknowledgment

Klara Greenhouse operates on the ancestral and unceded Mi'kmaw territory
of Mi'kma'ki, governed by the Peace and Friendship Treaties of 1725–1779,
which did not cede land and remain in force.

---

*Black Point Analytics — Nova Scotia*
