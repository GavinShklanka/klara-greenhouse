"""Action Service — handles monetization events (quote, diy plan, connect)."""

from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session as DBSession

from app.core.data_loader import get_greenhouse_data
from app.models import GreenhouseSession, ContactRequest


def handle_action(
    db: DBSession,
    session_id: str,
    action_type: str,
    email: str = "",
    phone: str = "",
    notes: str = "",
) -> dict:
    """
    Process user action choice. Returns confirmation + next steps.

    action_type: 'quote' | 'diy' | 'connect'
    """
    # Update session
    gh_session = db.query(GreenhouseSession).filter_by(id=session_id).first()
    if not gh_session:
        return {"error": "Session not found", "success": False}

    gh_session.action_taken = action_type
    gh_session.status = "action"

    # Create contact request
    contact = ContactRequest(
        id=str(uuid.uuid4()),
        session_id=session_id,
        request_type=action_type,
        email=email,
        phone=phone,
        notes=notes,
    )
    db.add(contact)
    db.commit()

    data = get_greenhouse_data()

    if action_type == "quote":
        # Find relevant contractors for the user's region
        intake = json.loads(gh_session.intake_data)
        location = intake.get("location", "halifax")
        contractors = _match_contractors(data, location)
        return {
            "success": True,
            "action": "quote",
            "message": "Your quote request has been submitted. A local builder will contact you within 48 hours.",
            "contractors": contractors,
        }

    elif action_type == "diy":
        return {
            "success": True,
            "action": "diy",
            "message": "Your detailed build plan is being prepared.",
            "price": 29,
            "includes": [
                "Complete materials list with quantities",
                "Step-by-step build instructions",
                "Foundation depth calculations for your region",
                "Ventilation setup guide",
                "Seasonal planting calendar",
            ],
        }

    elif action_type == "connect":
        intake = json.loads(gh_session.intake_data)
        location = intake.get("location", "halifax")
        contractors = _match_contractors(data, location)
        return {
            "success": True,
            "action": "connect",
            "message": "We'll connect you with a local builder who specializes in your area.",
            "contractors": contractors,
        }

    return {"error": f"Unknown action type: {action_type}", "success": False}


def _match_contractors(data: dict, location: str) -> list[dict]:
    """Find contractors that serve the user's region."""
    climate = data["climate_zones"].get(location, {})
    region_label = climate.get("label", "")

    matched = []
    for contractor in data.get("contractors", []):
        # Simple region matching
        if any(
            r.strip().lower() in contractor["region"].lower()
            for r in [location.replace("_", " "), region_label.lower()]
        ):
            matched.append({
                "name": contractor["name"],
                "phone": contractor["phone"],
                "email": contractor["email"],
                "region": contractor["region"],
            })

    # If no match, return all (it's NS, they're all relatively close)
    if not matched:
        matched = [
            {
                "name": c["name"],
                "phone": c["phone"],
                "email": c["email"],
                "region": c["region"],
            }
            for c in data.get("contractors", [])
        ]

    return matched
