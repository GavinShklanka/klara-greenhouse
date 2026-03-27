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

VALID_WIND_EXPOSURE = ["sheltered", "moderate", "coastal_exposed", "not_sure"]

VALID_SOUTH_WALL = ["yes", "no", "not_sure"]

VALID_EXPERIENCE = ["first_time", "some_experience", "experienced"]


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

    # New fields — optional with defaults (backward compatible)
    wind = data.get("wind_exposure", "moderate")
    if wind not in VALID_WIND_EXPOSURE:
        return False, f"Invalid wind exposure: {wind}"

    south_wall = data.get("has_south_wall", "not_sure")
    if south_wall not in VALID_SOUTH_WALL:
        return False, f"Invalid south wall value: {south_wall}"

    experience = data.get("experience_level", "first_time")
    if experience not in VALID_EXPERIENCE:
        return False, f"Invalid experience level: {experience}"

    return True, None


def normalize_intake(data: dict) -> dict:
    """Ensure all intake fields have values (apply defaults for missing fields)."""
    return {
        "location": data.get("location", "halifax"),
        "goal": data.get("goal", "grow_food"),
        "budget": data.get("budget", "under_5k"),
        "property_type": data.get("property_type", "backyard"),
        "greenhouse_type": data.get("greenhouse_type", "not_sure"),
        "wind_exposure": data.get("wind_exposure", "moderate"),
        "has_south_wall": data.get("has_south_wall", "not_sure"),
        "experience_level": data.get("experience_level", "first_time"),
    }


def create_session(db: DBSession, intake_data: dict) -> GreenhouseSession:
    """Create a new GreenhouseSession from validated intake data."""
    session = GreenhouseSession(
        id=str(uuid.uuid4()),
        status="intake",
        intake_data=json.dumps(normalize_intake(intake_data)),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
