"""API routes — Proposal Engine."""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import GreenhouseSession

logger = logging.getLogger(__name__)

router = APIRouter()

ui_dir = Path(__file__).resolve().parent.parent / "ui"
templates = Jinja2Templates(directory=str(ui_dir / "templates"))


@router.get("/proposal/{session_id}/extend", response_class=HTMLResponse)
async def view_extended_intake(request: Request, session_id: str, db: Session = Depends(get_db)):
    """Render the extended intake form for a paid session."""
    session_rec = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
    if not session_rec:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session_rec.payment_status != "paid":
        # Redirect to main page with message if unpaid
        return RedirectResponse(
            url=f"/?session_id={session_id}&error=payment_required", 
            status_code=status.HTTP_302_FOUND
        )
        
    return templates.TemplateResponse(
        "extended_intake.html",
        {"request": request, "session_id": session_id}
    )


@router.post("/api/proposal/{session_id}/extend")
async def submit_extended_intake(
    request: Request,
    session_id: str,
    slope: str = Form(...),
    drainage: str = Form(...),
    nearby_structures: str = Form(...),
    seasonal_intent: str = Form(...),
    diy_or_contractor: str = Form(...),
    desired_crops: list[str] = Form(...),
    db: Session = Depends(get_db)
):
    """Save the extended intake form data."""
    session_rec = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
    if not session_rec:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session_rec.payment_status != "paid":
        raise HTTPException(status_code=403, detail="Payment required before completing extended intake")
        
    if not desired_crops:
        raise HTTPException(status_code=400, detail="Must select at least one crop or not_sure")
        
    extended_data = {
        "slope": slope,
        "drainage": drainage,
        "nearby_structures": nearby_structures,
        "seasonal_intent": seasonal_intent,
        "diy_or_contractor": diy_or_contractor,
        "desired_crops": desired_crops
    }
    
    session_rec.extended_intake_data = json.dumps(extended_data)
    db.commit()
    
    # Send operator notification
    from app.services.email_service import send_notification_email
    try:
        intake_dict = json.loads(session_rec.intake_data) if session_rec.intake_data else {}
        send_notification_email({
            "type": "extended_intake_complete",
            "email": f"Session ID: {session_id}",
            "location": intake_dict.get("location", "Unknown"),
            "notes": "User completed property details form."
        })
    except Exception as e:
        logger.error(f"Failed to send extended intake notification: {e}")
        
    # Redirect to status page
    return RedirectResponse(
        url=f"/proposal/{session_id}/status", 
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/proposal/{session_id}/status", response_class=HTMLResponse)
async def view_proposal_status(request: Request, session_id: str, db: Session = Depends(get_db)):
    """Render the proposal generation status page."""
    session_rec = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
    if not session_rec:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return templates.TemplateResponse(
        "proposal_status.html",
        {"request": request, "session_id": session_id}
    )
