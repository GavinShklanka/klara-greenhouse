"""Intake Service — validates and structures user intake data."""

from __future__ import annotations

import json
import uuid
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.core.enums import Location, Goal, Budget, PropertyType, GreenhouseType
from app.models import GreenhouseSession


def validate_intake(data: dict) -> tuple[bool, Optional[str]]:
    """Validate intake answers using enum membership checks."""
    location = data.get("location", "")
    if location not in [e.value for e in Location]:
        return False, f"Invalid location: {location}"

    goal = data.get("goal", "")
    if goal not in [e.value for e in Goal]:
        return False, f"Invalid goal: {goal}"

    budget = data.get("budget", "")
    if budget not in [e.value for e in Budget]:
        return False, f"Invalid budget range: {budget}"

    prop = data.get("property_type", "")
    if prop not in [e.value for e in PropertyType]:
        return False, f"Invalid property type: {prop}"

    gh_type = data.get("greenhouse_type", "not_sure")
    if gh_type not in [e.value for e in GreenhouseType]:
        return False, f"Invalid greenhouse type: {gh_type}"

    return True, None


def create_session(db: DBSession, intake_data: dict) -> GreenhouseSession:
    """Create a new GreenhouseSession from validated intake data."""
    session = GreenhouseSession(
        id=str(uuid.uuid4()),
        status="intake",
        intake_data=json.dumps(intake_data),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
