"""Intake Service — validates and structures user intake data."""

from __future__ import annotations

import json
import uuid
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models import GreenhouseSession


VALID_LOCATIONS = [
    "halifax", "annapolis_valley", "south_shore", "cape_breton",
    "north_shore", "central_ns", "eastern_shore",
]

VALID_GOALS = ["grow_food", "save_money", "sustainability", "mixed"]

VALID_BUDGETS = ["under_5k", "5k_10k", "over_10k"]

VALID_PROPERTY = ["backyard", "rural", "small_lot", "not_sure"]

VALID_GREENHOUSE_TYPES = ["polycarbonate", "polytunnel", "passive_solar", "not_sure"]


def validate_intake(data: dict) -> tuple[bool, Optional[str]]:
    """Validate intake answers."""
    location = data.get("location", "")
    if location not in VALID_LOCATIONS:
        return False, f"Invalid location: {location}"

    goal = data.get("goal", "")
    if goal not in VALID_GOALS:
        return False, f"Invalid goal: {goal}"

    budget = data.get("budget", "")
    if budget not in VALID_BUDGETS:
        return False, f"Invalid budget range: {budget}"

    prop = data.get("property_type", "")
    if prop not in VALID_PROPERTY:
        return False, f"Invalid property type: {prop}"

    gh_type = data.get("greenhouse_type", "not_sure")
    if gh_type not in VALID_GREENHOUSE_TYPES:
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
