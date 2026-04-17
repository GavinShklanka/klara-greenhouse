"""Shared FastAPI dependencies — session lookup + context building."""

from __future__ import annotations

import json

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.models import GreenhouseSession
from app.services.suitability_service import check_suitability
from app.services.design_service import recommend_design


def get_session(session_id: str, db: DBSession = Depends(get_db)) -> GreenhouseSession:
    """Look up a GreenhouseSession by ID — raises 404 if missing."""
    gh_session = db.query(GreenhouseSession).filter_by(id=session_id).first()
    if not gh_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return gh_session


def get_session_intake(session_id: str, db: DBSession = Depends(get_db)) -> tuple[GreenhouseSession, dict]:
    """Return (session, parsed intake dict)."""
    gh_session = get_session(session_id, db)
    intake = json.loads(gh_session.intake_data) if gh_session.intake_data else {}
    return gh_session, intake


def get_session_context(
    session_id: str,
    db: DBSession = Depends(get_db),
) -> tuple[GreenhouseSession, dict, dict, dict]:
    """Return (session, intake, suitability, design) — the common 4-tuple
    needed by plan sub-endpoints."""
    gh_session, intake = get_session_intake(session_id, db)
    suitability = check_suitability(intake)
    design = recommend_design(intake, suitability)
    return gh_session, intake, suitability, design
