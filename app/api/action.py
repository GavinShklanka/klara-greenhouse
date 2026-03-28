"""Action API — /action/checkout, /action/quote, /action/consultation + Stripe webhook."""

import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.core.database import get_db
from app.models import GreenhouseSession, ContactRequest
from app.services.email_service import send_notification_email, send_user_confirmation

router = APIRouter()


# ── Pydantic Models ──────────────────────────────────────────

class CheckoutRequest(BaseModel):
    session_id: str
    email: str
    plan_tier: str = "basic"   # 'basic' ($29) or 'premium' ($79)


class QuoteRequest(BaseModel):
    session_id: str
    name: str = ""
    email: str
    phone: str = ""
    notes: str = ""


class ConsultationRequest(BaseModel):
    session_id: str
    name: str = ""
    email: str
    phone: str = ""
    preferred_time: str = ""
    notes: str = ""


# ── /action/checkout — Stripe Checkout Session ───────────────

@router.post("/action/checkout")
def create_checkout(req: CheckoutRequest, db: DBSession = Depends(get_db)):
    """Create a Stripe checkout session for plan purchase."""
    gh_session = db.query(GreenhouseSession).filter_by(id=req.session_id).first()
    if not gh_session:
        return {"success": False, "error": "Session not found"}

    # Determine price
    price_cents = 2000  # $20 CAD for Property Proposal
    price_label = "$20"

    # MANUAL FALLBACK: If Stripe is not configured, this endpoint returns
    # a 'stubbed' response. The operator then:
    # 1. Emails the user a Stripe Payment Link ($20)
    # 2. Monitors Stripe dashboard for payment
    # 3. Manually sets payment_status='paid' in the DB (or via admin endpoint)
    # 4. Sends the extended intake URL to the user

    # If Stripe is configured, create real checkout session
    if settings.stripe_secret_key:
        try:
            import stripe
            stripe.api_key = settings.stripe_secret_key

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "cad",
                        "product_data": {
                            "name": "Klara Property Proposal",
                            "description": "Property-specific proposal including siting, cost line items, blocker analysis, and seasonal crop match.",
                        },
                        "unit_amount": price_cents,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"{settings.base_url}/proposal/{req.session_id}/extend?checkout_session={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.base_url}/?session_id={req.session_id}&checkout=cancelled",
                customer_email=req.email,
                metadata={
                    "greenhouse_session_id": req.session_id,
                },
            )

            # Record the contact request
            _record_contact(db, req.session_id, "checkout", req.email)

            return {
                "success": True,
                "action": "checkout",
                "checkout_url": checkout_session.url,
                "message": f"Redirecting to secure payment for your {price_label} build plan.",
            }

        except Exception as e:
            return {"success": False, "error": f"Payment setup failed: {str(e)}"}

    # Stripe not configured — stub response for development
    _record_contact(db, req.session_id, "checkout", req.email)
    gh_session.action_taken = "checkout"
    gh_session.status = "action"
    
    # In full manual mode during dev without admin endpoint, uncomment to auto-mark paid
    # gh_session.payment_status = "paid" 
    
    db.commit()

    # Email notifications
    intake = json.loads(gh_session.intake_data) if gh_session.intake_data else {}
    send_notification_email({"type": "checkout", "email": req.email, "location": intake.get("location", ""), "budget": intake.get("budget", ""), "name": ""})
    send_user_confirmation(req.email, "checkout")

    return {
        "success": True,
        "action": "checkout",
        "checkout_url": None,
        "message": (
            f"Your {price_label} Property Proposal request has been received. "
            f"Stripe is not configured — in production, you would be redirected to a secure checkout page."
        ),
        "dev_note": "Set STRIPE_SECRET_KEY in .env to enable real payments.",
    }


# ── /action/quote — Builder Quote Request ────────────────────

@router.post("/action/quote")
def request_quote(req: QuoteRequest, db: DBSession = Depends(get_db)):
    """Capture a builder quote request (lead gen)."""
    gh_session = db.query(GreenhouseSession).filter_by(id=req.session_id).first()
    if not gh_session:
        return {"success": False, "error": "Session not found"}

    # Get plan data for context
    plan_data = json.loads(gh_session.plan_data) if gh_session.plan_data else {}
    recommendation = ""
    if plan_data and "design" in plan_data:
        recommendation = plan_data["design"].get("recommendation", "")

    _record_contact(
        db, req.session_id, "quote", req.email,
        phone=req.phone,
        notes=f"Name: {req.name}\nRecommendation: {recommendation}\nNotes: {req.notes}",
    )

    gh_session.action_taken = "quote"
    gh_session.status = "action"
    db.commit()

    # Email notifications
    intake = json.loads(gh_session.intake_data) if gh_session.intake_data else {}
    send_notification_email({"type": "quote", "email": req.email, "name": req.name, "location": intake.get("location", ""), "budget": intake.get("budget", ""), "notes": req.notes})
    send_user_confirmation(req.email, "quote")

    return {
        "success": True,
        "action": "quote",
        "message": "Your quote request has been submitted. A local Nova Scotia greenhouse builder will contact you within 48 hours.",
        "recommendation": recommendation,
        "why": "We match you with builders who specialize in your greenhouse type and service your region.",
        "next_step": "Check your email for builder contact and quote details.",
    }


# ── /action/consultation — Book Local Consultation ───────────

@router.post("/action/consultation")
def book_consultation(req: ConsultationRequest, db: DBSession = Depends(get_db)):
    """Capture consultation booking request."""
    gh_session = db.query(GreenhouseSession).filter_by(id=req.session_id).first()
    if not gh_session:
        return {"success": False, "error": "Session not found"}

    _record_contact(
        db, req.session_id, "consultation", req.email,
        phone=req.phone,
        notes=f"Name: {req.name}\nPreferred time: {req.preferred_time}\nNotes: {req.notes}",
    )

    gh_session.action_taken = "consultation"
    gh_session.status = "action"
    db.commit()

    # Email notifications
    intake = json.loads(gh_session.intake_data) if gh_session.intake_data else {}
    send_notification_email({"type": "consultation", "email": req.email, "name": req.name, "location": intake.get("location", ""), "budget": intake.get("budget", ""), "notes": req.notes})
    send_user_confirmation(req.email, "consultation")

    return {
        "success": True,
        "action": "consultation",
        "message": "Your consultation request has been received. A greenhouse specialist will reach out to schedule your session.",
        "why": "A local consultation lets you discuss site-specific factors like drainage, sun exposure, and access.",
        "next_step": "You'll receive a confirmation email with scheduling options.",
    }


# ── /webhooks/stripe — Handle Checkout Completion ────────────

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: DBSession = Depends(get_db)):
    """Process Stripe checkout completion — unlock/deliver full plan."""
    if not settings.stripe_secret_key:
        return JSONResponse({"status": "stripe_not_configured"}, status_code=200)

    import stripe
    stripe.api_key = settings.stripe_secret_key

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        if settings.stripe_webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
        else:
            event = json.loads(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    if event.get("type") == "checkout.session.completed":
        session_data = event["data"]["object"]
        metadata = session_data.get("metadata", {})
        gh_session_id = metadata.get("greenhouse_session_id")

        if gh_session_id:
            gh_session = db.query(GreenhouseSession).filter_by(id=gh_session_id).first()
            if gh_session:
                gh_session.action_taken = "paid"
                gh_session.status = "paid"
                gh_session.payment_status = "paid"
                db.commit()
            else:
                import logging
                logging.getLogger(__name__).warning(f"Webhook fired for session {gh_session_id} but it was not found in DB.")

    return JSONResponse({"status": "ok"}, status_code=200)


# ── /admin/sessions/{session_id}/mark-paid ───────────────────

@router.post("/admin/sessions/{session_id}/mark-paid")
def admin_mark_paid(session_id: str, db: DBSession = Depends(get_db)):
    """Manually mark a session as paid (for fallback operator flows)."""
    gh_session = db.query(GreenhouseSession).filter_by(id=session_id).first()
    if not gh_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    gh_session.payment_status = "paid"
    gh_session.action_taken = "paid"
    gh_session.status = "paid"
    db.commit()
    
    return {"success": True, "message": f"Session {session_id} marked as paid."}


# ── Helper ───────────────────────────────────────────────────

def _record_contact(
    db: DBSession,
    session_id: str,
    request_type: str,
    email: str,
    phone: str = "",
    notes: str = "",
):
    """Create a ContactRequest record."""
    contact = ContactRequest(
        id=str(uuid.uuid4()),
        session_id=session_id,
        request_type=request_type,
        email=email,
        phone=phone,
        notes=notes,
    )
    db.add(contact)
    db.commit()
