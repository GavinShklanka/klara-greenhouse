"""FastAPI entrypoint — KLARA Greenhouse."""

import sqlite3
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.intake import router as intake_router
from app.api.plan import router as plan_router
from app.api.action import router as action_router
from app.api.health import router as health_router
from app.api.proposal import router as proposal_router
from app.api.greenhouse import router as greenhouse_router
from app.core.database import engine, Base
from app.core.config import settings

app = FastAPI(
    title="KLARA Greenhouse",
    description="Greenhouse intelligence for Atlantic Canada — from idea to build plan.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [
        settings.base_url,
        "https://greenhouse.blackpointanalytics.ca",
        "https://klaragreenhouse.ca",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(intake_router, prefix="/api")
app.include_router(plan_router, prefix="/api")
app.include_router(action_router, prefix="/api")
app.include_router(health_router)
app.include_router(proposal_router)
app.include_router(greenhouse_router)


# Idempotent SQLite migration columns — each wrapped in try/except
_MIGRATIONS = [
    ("extended_intake_data", "ALTER TABLE greenhouse_sessions ADD COLUMN extended_intake_data TEXT DEFAULT '{}'"),
    ("payment_status", "ALTER TABLE greenhouse_sessions ADD COLUMN payment_status TEXT DEFAULT 'unpaid'"),
    ("recommendation_data", "ALTER TABLE greenhouse_sessions ADD COLUMN recommendation_data TEXT"),
    ("operator_approved", "ALTER TABLE greenhouse_sessions ADD COLUMN operator_approved BOOLEAN DEFAULT 0"),
    ("beta_code", "ALTER TABLE greenhouse_sessions ADD COLUMN beta_code TEXT"),
    ("user_agent", "ALTER TABLE greenhouse_sessions ADD COLUMN user_agent TEXT"),
    ("ip_hash", "ALTER TABLE greenhouse_sessions ADD COLUMN ip_hash TEXT"),
]


@app.on_event("startup")
async def startup():
    """Create tables and migrate schema on startup."""
    import app.models  # noqa: F401 — register all models
    Base.metadata.create_all(bind=engine)

    # Idempotent SQLite Schema Migration
    try:
        db_path = settings.database_url.replace("sqlite:///", "")
        if db_path and not db_path.startswith("postgres"):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            for col_name, alter_sql in _MIGRATIONS:
                try:
                    cursor.execute(f"SELECT {col_name} FROM greenhouse_sessions LIMIT 1")
                except sqlite3.OperationalError:
                    cursor.execute(alter_sql)
                    print(f"Migration: Added {col_name} column to greenhouse_sessions")

            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Migration error: {e}")


# Mount UI
ui_dir = Path(__file__).resolve().parent / "ui"
if ui_dir.exists():
    app.mount("/static", StaticFiles(directory=str(ui_dir / "static")), name="static")
    templates = Jinja2Templates(directory=str(ui_dir / "templates"))
else:
    templates = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Redirect root to greenhouse intake."""
    return RedirectResponse(url="/greenhouse/intake")
