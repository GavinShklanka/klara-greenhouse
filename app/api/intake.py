"""Intake API — POST /api/intake."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.core.enums import Location, Goal, Budget, PropertyType, GreenhouseType, SolarExisting
from app.services.intake_service import validate_intake, create_session

router = APIRouter()


class IntakeRequest(BaseModel):
    location: str
    goal: str
    budget: str
    property_type: str
    greenhouse_type: str = "not_sure"
    solar_existing: str = "none"


@router.post("/intake")
def submit_intake(req: IntakeRequest, db: DBSession = Depends(get_db)):
    """Accept intake data, create session, return session_id."""
    data = req.model_dump()
    valid, error = validate_intake(data)
    if not valid:
        raise HTTPException(status_code=422, detail=error)

    session = create_session(db, data)
    return {"success": True, "session_id": session.id}
