"""FastAPI entrypoint — KLARA Greenhouse."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.intake import router as intake_router
from app.api.plan import router as plan_router
from app.api.action import router as action_router
from app.api.health import router as health_router
from app.core.database import engine, Base

app = FastAPI(
    title="KLARA Greenhouse",
    description="Greenhouse planning for Nova Scotia — from idea to build plan.",
    version="1.0.0",
)

# CORS: allow Next.js dev server or any frontend to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8100"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(intake_router, prefix="/api")
app.include_router(plan_router, prefix="/api")
app.include_router(action_router, prefix="/api")
app.include_router(health_router)


@app.on_event("startup")
async def startup():
    """Create tables on startup."""
    import app.models  # noqa: F401 — register models
    Base.metadata.create_all(bind=engine)


# Mount UI
ui_dir = Path(__file__).resolve().parent / "ui"
if ui_dir.exists():
    app.mount("/static", StaticFiles(directory=str(ui_dir / "static")), name="static")
    templates = Jinja2Templates(directory=str(ui_dir / "templates"))
else:
    templates = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if templates is None:
        return HTMLResponse("<p>UI not configured.</p>")
    template = templates.env.get_template("index.html")
    html = template.render(request=request)
    return HTMLResponse(html)
