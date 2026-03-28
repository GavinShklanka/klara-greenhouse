"""
Greenhouse proposal flow routes — Prompt 9 + Prompt 10.
Handles: intake → preview → checkout → extend → proposal → admin
         + beta codes + friction logging + analytics + checkpoint
"""
import hashlib
import json
import logging
import os
import secrets
import uuid
from collections import defaultdict
from datetime import datetime, timezone, timedelta

import stripe
from fastapi import APIRouter, Request, Form, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import GreenhouseSession, BetaCode, FrictionEvent
from app.services.routing_service import run_routing

logger = logging.getLogger(__name__)

router = APIRouter()

# Stripe config
stripe.api_key = settings.stripe_secret_key or os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_WEBHOOK_SECRET = settings.stripe_webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Rate limiting: in-memory store (resets on restart — fine for 15 beta users)
_rate_limit_store: dict[str, list[datetime]] = defaultdict(list)
RATE_LIMIT_MAX = 10  # per IP per hour
RATE_LIMIT_WINDOW = timedelta(hours=1)


def _hash_ip(ip: str) -> str:
    return hashlib.sha256(f"klara-{ip}".encode()).hexdigest()[:16]


def _check_rate_limit(request: Request) -> bool:
    """Return True if request is within rate limit, False if blocked."""
    ip = request.client.host if request.client else "unknown"
    ip_key = _hash_ip(ip)
    now = datetime.now(timezone.utc)
    cutoff = now - RATE_LIMIT_WINDOW

    # Clean old entries
    _rate_limit_store[ip_key] = [t for t in _rate_limit_store[ip_key] if t > cutoff]

    if len(_rate_limit_store[ip_key]) >= RATE_LIMIT_MAX:
        return False  # blocked

    _rate_limit_store[ip_key].append(now)
    return True


def _log_event(session_id: str, event_type: str, request: Request,
               page: str = None, error: str = None, time_on_page: float = None,
               metadata: dict = None):
    """Record a friction event to the database."""
    try:
        db = SessionLocal()
        ev = FrictionEvent(
            id=str(uuid.uuid4()),
            session_id=session_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            page=page or str(request.url.path),
            time_on_page_seconds=time_on_page,
            error=error,
            user_agent=request.headers.get("user-agent", "")[:500],
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        db.add(ev)
        db.commit()
        db.close()
    except Exception as e:
        logger.warning(f"Failed to log friction event: {e}")


# ═══════════════════════════════════════════════════
# ADMIN AUTH — simple password check via cookie
# ═══════════════════════════════════════════════════

ADMIN_COOKIE = "klara_admin_token"


def _admin_token() -> str:
    """Derive a stable admin token from the password."""
    return hashlib.sha256(f"klara-admin-{settings.admin_password}".encode()).hexdigest()[:32]


def _require_admin(request: Request):
    """Check admin authentication — raises 401 if not authenticated."""
    cookie = request.cookies.get(ADMIN_COOKIE, "")
    if cookie == _admin_token():
        return True
    raise HTTPException(status_code=401, detail="Admin authentication required")


HUMAN_LABELS = {
    "budget_range": {
        "under_3k": "Under $3,000",
        "3k_5k": "$3,000 – $5,000",
        "5k_8k": "$5,000 – $8,000",
        "8k_plus": "$8,000+",
    },
    "available_footprint_sqft": {
        "small_under_80": "Small (under 80 sq ft)",
        "medium_80_150": "Medium (80–150 sq ft)",
        "large_150_plus": "Large (150+ sq ft)",
    },
    "primary_use": {
        "year_round_food": "Year-Round Food Production",
        "seasonal_extension": "Season Extension",
        "educational": "Educational / Learning",
        "community": "Community Growing",
    },
    "diy_capacity": {
        "full_diy": "Full DIY — I'll build it myself",
        "partial_diy": "Partial DIY — I'll need some help",
        "need_install": "Need Full Installation",
    },
    "timeline": {
        "this_spring": "This Spring",
        "this_year": "This Year",
        "exploring": "Just Exploring",
    },
    "lot_orientation": {
        "south_facing": "South-Facing",
        "east_west": "East/West-Facing",
        "north_facing": "North-Facing",
        "not_sure": "Not Sure",
    },
    "existing_infrastructure": {
        "none": "None",
        "has_water": "Has Water Access",
        "has_electrical": "Has Electrical",
        "has_both": "Has Both Water & Electrical",
        "not_sure": "Not Sure",
    },
}


def _safe_render(request, template_name, context):
    """Render template with error catch — returns friendly error page on failure."""
    try:
        from app.main import templates as app_templates
        return app_templates.TemplateResponse(template_name, context)
    except Exception as e:
        logger.error(f"Template render error ({template_name}): {e}")
        return HTMLResponse(
            f"<html><body style='font-family:Inter,sans-serif;padding:2rem;'>"
            f"<h1>Something went wrong</h1>"
            f"<p>We encountered an error generating this page. Please try again or "
            f"<a href='/greenhouse/intake'>start a new assessment</a>.</p>"
            f"<p style='color:#888;font-size:0.8rem;'>Error ref: {type(e).__name__}</p>"
            f"</body></html>",
            status_code=500,
        )


# ════════════════════════════════════════════════════
# A. INTAKE
# ════════════════════════════════════════════════════

@router.get("/greenhouse/intake", response_class=HTMLResponse)
async def intake_form(request: Request):
    """Render the 6-field greenhouse intake form."""
    return _safe_render(request, "greenhouse/intake.html", {
        "request": request,
        "labels": HUMAN_LABELS,
    })


@router.post("/greenhouse/intake")
async def create_greenhouse_session(
    request: Request,
    postal_code: str = Form(...),
    budget_range: str = Form(...),
    available_footprint_sqft: str = Form(...),
    primary_use: str = Form(...),
    diy_capacity: str = Form(...),
    timeline: str = Form(...),
):
    """Create session from 6-field intake and redirect to preview."""
    # Rate limit
    if not _check_rate_limit(request):
        return HTMLResponse(
            "<html><body style='font-family:Inter,sans-serif;padding:2rem;'>"
            "<h1>Too many requests</h1>"
            "<p>Please wait a few minutes before submitting another assessment.</p>"
            "</body></html>",
            status_code=429,
        )

    db = SessionLocal()
    try:
        session_id = str(uuid.uuid4())
        intake_data = {
            "postal_code": postal_code.strip().upper(),
            "budget_range": budget_range,
            "available_footprint_sqft": available_footprint_sqft,
            "primary_use": primary_use,
            "diy_capacity": diy_capacity,
            "timeline": timeline,
        }

        ip = request.client.host if request.client else "unknown"
        session = GreenhouseSession(
            id=session_id,
            intake_data=json.dumps(intake_data),
            extended_intake_data="{}",
            payment_status="unpaid",
            user_agent=request.headers.get("user-agent", "")[:500],
            ip_hash=_hash_ip(ip),
        )
        db.add(session)
        db.commit()

        _log_event(session_id, "intake_complete", request, metadata=intake_data)

        return RedirectResponse(url=f"/greenhouse/preview/{session_id}", status_code=303)
    except Exception as e:
        logger.error(f"Intake error: {e}")
        return HTMLResponse(
            "<html><body style='font-family:Inter,sans-serif;padding:2rem;'>"
            "<h1>Something went wrong</h1>"
            "<p>Please try again. <a href='/greenhouse/intake'>Start over</a></p>"
            "</body></html>",
            status_code=500,
        )
    finally:
        db.close()


# ════════════════════════════════════════════════════
# B. FREE PREVIEW
# ════════════════════════════════════════════════════

@router.get("/greenhouse/preview/{session_id}", response_class=HTMLResponse)
async def preview(request: Request, session_id: str):
    """Free feasibility preview — no prices, no vendors."""
    db = SessionLocal()
    try:
        session = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        intake = json.loads(session.intake_data or "{}")
        result = run_routing(intake)

        _log_event(session_id, "preview_view", request)

        return _safe_render(request, "greenhouse/preview.html", {
            "request": request,
            "session_id": session_id,
            "intake": intake,
            "result": result,
            "labels": HUMAN_LABELS,
        })
    finally:
        db.close()


# ════════════════════════════════════════════════════
# C. PAYMENT FLOW
# ════════════════════════════════════════════════════

@router.post("/greenhouse/checkout/{session_id}")
async def checkout(request: Request, session_id: str):
    """Create Stripe Checkout session ($49 CAD)."""
    db = SessionLocal()
    try:
        session = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        _log_event(session_id, "checkout_start", request)

        base_url = str(request.base_url).rstrip("/")

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "cad",
                    "product_data": {
                        "name": "Klara Greenhouse Property Proposal",
                        "description": "Full 8-section property-specific greenhouse proposal for your NS/PEI location.",
                    },
                    "unit_amount": 4900,  # $49.00 CAD in cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{base_url}/greenhouse/extend/{session_id}?payment=success",
            cancel_url=f"{base_url}/greenhouse/preview/{session_id}?payment=cancelled",
            metadata={"session_id": session_id},
        )

        return RedirectResponse(url=checkout_session.url, status_code=303)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        if settings.environment == "development":
            # Dev fallback: mark as paid for testing
            session.payment_status = "paid"
            db.commit()
            _log_event(session_id, "checkout_complete", request, metadata={"method": "dev_fallback"})
            return RedirectResponse(url=f"/greenhouse/extend/{session_id}?payment=success", status_code=303)
        _log_event(session_id, "error", request, error=str(e))
        return HTMLResponse(
            "<html><body style='font-family:Inter,sans-serif;padding:2rem;'>"
            "<h1>Payment Error</h1>"
            "<p>We couldn't process your payment. Please try again or "
            f"<a href='/greenhouse/preview/{session_id}'>go back</a>.</p>"
            "</body></html>",
            status_code=500,
        )
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        _log_event(session_id, "error", request, error=str(e))
        if settings.environment == "development":
            session.payment_status = "paid"
            db.commit()
            return RedirectResponse(url=f"/greenhouse/extend/{session_id}?payment=success", status_code=303)
        raise
    finally:
        db.close()


@router.post("/greenhouse/webhook/stripe")
async def stripe_webhook(request: Request):
    """Stripe webhook — marks session as paid."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        checkout_data = event["data"]["object"]
        session_id = checkout_data.get("metadata", {}).get("session_id")

        if session_id:
            db = SessionLocal()
            try:
                session = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
                if session:
                    session.payment_status = "paid"
                    db.commit()
                    _log_event(session_id, "checkout_complete", request, metadata={"method": "stripe_webhook"})
                    logger.info(f"Session {session_id} marked as paid via webhook")
            finally:
                db.close()

    return JSONResponse({"status": "ok"})


# ════════════════════════════════════════════════════
# D. BETA CODE FLOW
# ════════════════════════════════════════════════════

@router.get("/greenhouse/beta/{code}", response_class=HTMLResponse)
async def beta_entry(request: Request, code: str):
    """Beta code entry — bypasses Stripe payment and renders intake form."""
    db = SessionLocal()
    try:
        beta = db.query(BetaCode).filter(BetaCode.code == code).first()
        if not beta:
            return HTMLResponse(
                "<html><body style='font-family:Inter,sans-serif;padding:2rem;text-align:center;'>"
                "<h1>Invalid Beta Code</h1>"
                "<p>This code is not recognized. <a href='/greenhouse/intake'>Start a regular assessment</a></p>"
                "</body></html>",
                status_code=404,
            )
        if beta.used:
            return HTMLResponse(
                "<html><body style='font-family:Inter,sans-serif;padding:2rem;text-align:center;'>"
                "<h1>Code Already Used</h1>"
                "<p>This beta code has already been redeemed. "
                "<a href='/greenhouse/intake'>Start a regular assessment</a></p>"
                "</body></html>",
                status_code=410,
            )

        _log_event(None, "beta_code_entry", request, metadata={"code": code})

        return _safe_render(request, "greenhouse/intake.html", {
            "request": request,
            "labels": HUMAN_LABELS,
            "beta_code": code,
        })
    finally:
        db.close()


@router.post("/greenhouse/beta/{code}/intake")
async def beta_intake(
    request: Request,
    code: str,
    postal_code: str = Form(...),
    budget_range: str = Form(...),
    available_footprint_sqft: str = Form(...),
    primary_use: str = Form(...),
    diy_capacity: str = Form(...),
    timeline: str = Form(...),
):
    """Beta intake — creates paid session from beta code."""
    db = SessionLocal()
    try:
        beta = db.query(BetaCode).filter(BetaCode.code == code, BetaCode.used == False).first()
        if not beta:
            raise HTTPException(status_code=410, detail="Beta code invalid or already used")

        session_id = str(uuid.uuid4())
        intake_data = {
            "postal_code": postal_code.strip().upper(),
            "budget_range": budget_range,
            "available_footprint_sqft": available_footprint_sqft,
            "primary_use": primary_use,
            "diy_capacity": diy_capacity,
            "timeline": timeline,
        }

        ip = request.client.host if request.client else "unknown"
        session = GreenhouseSession(
            id=session_id,
            intake_data=json.dumps(intake_data),
            extended_intake_data="{}",
            payment_status="paid",  # beta = free
            beta_code=code,
            user_agent=request.headers.get("user-agent", "")[:500],
            ip_hash=_hash_ip(ip),
        )
        db.add(session)

        # Mark beta code as used
        beta.used = True
        beta.used_by_session_id = session_id
        beta.used_at = datetime.now(timezone.utc)
        db.commit()

        _log_event(session_id, "intake_complete", request, metadata={**intake_data, "beta_code": code})
        _log_event(session_id, "checkout_complete", request, metadata={"method": "beta_code", "code": code})

        # Skip preview + checkout — go straight to extended intake
        return RedirectResponse(url=f"/greenhouse/extend/{session_id}?payment=success", status_code=303)
    finally:
        db.close()


# ════════════════════════════════════════════════════
# E. EXTENDED INTAKE
# ════════════════════════════════════════════════════

@router.get("/greenhouse/extend/{session_id}", response_class=HTMLResponse)
async def extend_intake_form(request: Request, session_id: str):
    """Extended intake form — collects lot_orientation and existing_infrastructure."""
    db = SessionLocal()
    try:
        session = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Auto-mark as paid if coming from Stripe success redirect
        payment_param = request.query_params.get("payment")
        if payment_param == "success" and session.payment_status != "paid":
            session.payment_status = "paid"
            db.commit()

        if session.payment_status != "paid":
            return RedirectResponse(url=f"/greenhouse/preview/{session_id}")

        return _safe_render(request, "greenhouse/extend_intake.html", {
            "request": request,
            "session_id": session_id,
            "labels": HUMAN_LABELS,
        })
    finally:
        db.close()


@router.post("/greenhouse/extend/{session_id}")
async def submit_extended_intake(
    request: Request,
    session_id: str,
    lot_orientation: str = Form(...),
    existing_infrastructure: str = Form(...),
):
    """Store extended intake and redirect to proposal."""
    db = SessionLocal()
    try:
        session = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        extended = {
            "lot_orientation": lot_orientation,
            "existing_infrastructure": existing_infrastructure,
        }
        session.extended_intake_data = json.dumps(extended)

        # Merge and generate full recommendation
        intake = json.loads(session.intake_data or "{}")
        intake.update(extended)
        result = run_routing(intake)

        # Store recommendation JSON
        session.recommendation_data = json.dumps(result.to_dict(), default=str)
        db.commit()

        _log_event(session_id, "extend_complete", request, metadata=extended)

        return RedirectResponse(url=f"/greenhouse/proposal/{session_id}", status_code=303)
    except Exception as e:
        logger.error(f"Extended intake error: {e}")
        _log_event(session_id, "error", request, error=str(e), page="/greenhouse/extend")
        return HTMLResponse(
            "<html><body style='font-family:Inter,sans-serif;padding:2rem;'>"
            "<h1>Something went wrong</h1>"
            "<p>We couldn't generate your proposal. Please try again.</p>"
            f"<a href='/greenhouse/extend/{session_id}'>Try again</a>"
            "</body></html>",
            status_code=500,
        )
    finally:
        db.close()


# ════════════════════════════════════════════════════
# F. FULL PROPOSAL VIEW
# ════════════════════════════════════════════════════

@router.get("/greenhouse/proposal/{session_id}", response_class=HTMLResponse)
async def proposal_view(request: Request, session_id: str):
    """Full 8-section proposal — gated behind payment."""
    db = SessionLocal()
    try:
        session = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.payment_status != "paid":
            return RedirectResponse(url=f"/greenhouse/preview/{session_id}")

        # Load recommendation or generate fresh
        if session.recommendation_data:
            rec = json.loads(session.recommendation_data)
        else:
            intake = json.loads(session.intake_data or "{}")
            extended = json.loads(session.extended_intake_data or "{}")
            intake.update(extended)
            result = run_routing(intake)
            rec = result.to_dict()
            session.recommendation_data = json.dumps(rec, default=str)
            db.commit()

        _log_event(session_id, "proposal_view", request)

        return _safe_render(request, "greenhouse/proposal.html", {
            "request": request,
            "session_id": session_id,
            "rec": rec,
            "labels": HUMAN_LABELS,
        })
    except Exception as e:
        logger.error(f"Proposal view error: {e}")
        _log_event(session_id, "error", request, error=str(e), page="/greenhouse/proposal")
        return HTMLResponse(
            "<html><body style='font-family:Inter,sans-serif;padding:2rem;'>"
            "<h1>Something went wrong</h1>"
            "<p>We couldn't load your proposal. Please try again.</p>"
            f"<a href='/greenhouse/proposal/{session_id}'>Try again</a>"
            "</body></html>",
            status_code=500,
        )
    finally:
        db.close()


# ════════════════════════════════════════════════════
# G. FRICTION EVENT ENDPOINT (client-side JS)
# ════════════════════════════════════════════════════

@router.post("/greenhouse/events")
async def record_event(request: Request):
    """Record friction events from client-side JavaScript."""
    try:
        body = await request.json()
        _log_event(
            session_id=body.get("session_id"),
            event_type=body.get("event_type", "page_view"),
            request=request,
            page=body.get("page"),
            time_on_page=body.get("time_on_page_seconds"),
            error=body.get("error"),
            metadata=body.get("metadata"),
        )
        return JSONResponse({"status": "ok"})
    except Exception as e:
        logger.warning(f"Event recording failed: {e}")
        return JSONResponse({"status": "error"}, status_code=400)


# ════════════════════════════════════════════════════
# H. ADMIN — AUTH + DASHBOARD + ANALYTICS + CHECKPOINT
# ════════════════════════════════════════════════════

@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Render admin login form."""
    return HTMLResponse(
        """<!DOCTYPE html><html><head><title>Klara Admin</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="/static/css/klara.css"></head>
        <body><nav class="nav"><div class="nav-inner"><a href="/" class="nav-logo">Klara</a>
        <span class="nav-tagline">Admin Login</span></div></nav>
        <main class="container"><div class="intake-hero"><h1>Admin Access</h1></div>
        <form action="/admin/login" method="POST" class="intake-form" style="max-width:400px">
        <div class="form-group"><label for="password">Password</label>
        <input type="password" id="password" name="password" required></div>
        <button type="submit" class="btn btn-primary btn-lg">Login</button>
        </form></main></body></html>"""
    )


@router.post("/admin/login")
async def admin_login(request: Request, password: str = Form(...)):
    """Verify admin password and set cookie."""
    if password == settings.admin_password:
        response = RedirectResponse(url="/admin/proposals", status_code=303)
        response.set_cookie(ADMIN_COOKIE, _admin_token(), httponly=True, max_age=86400)
        return response
    return HTMLResponse(
        """<!DOCTYPE html><html><head><title>Klara Admin</title>
        <link rel="stylesheet" href="/static/css/klara.css"></head>
        <body><nav class="nav"><div class="nav-inner"><a href="/" class="nav-logo">Klara</a></div></nav>
        <main class="container"><div class="alert alert-red">Incorrect password.</div>
        <a href="/admin/login" class="btn btn-secondary">Try again</a></main></body></html>""",
        status_code=401,
    )


@router.get("/admin/proposals", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """List all proposals with status."""
    _require_admin(request)
    db = SessionLocal()
    try:
        sessions = db.query(GreenhouseSession).order_by(GreenhouseSession.created_at.desc()).all()

        proposals = []
        for s in sessions:
            intake = json.loads(s.intake_data or "{}")
            rec = json.loads(s.recommendation_data or "{}") if s.recommendation_data else {}

            proposals.append({
                "session_id": s.id,
                "postal_code": intake.get("postal_code", "—"),
                "budget_range": HUMAN_LABELS.get("budget_range", {}).get(intake.get("budget_range", ""), "—"),
                "score": rec.get("scores", {}).get("weighted_total", "—"),
                "confidence": rec.get("confidence", "—"),
                "decision": rec.get("route_decision", "—"),
                "payment_status": s.payment_status or "unpaid",
                "approved": getattr(s, "operator_approved", False),
                "beta_code": s.beta_code or "",
                "created_at": str(s.created_at) if s.created_at else "—",
            })

        return _safe_render(request, "admin/dashboard.html", {
            "request": request,
            "proposals": proposals,
        })
    finally:
        db.close()


@router.get("/admin/proposal/{session_id}/audit", response_class=HTMLResponse)
async def admin_audit(request: Request, session_id: str):
    """View full audit trail for a proposal."""
    _require_admin(request)
    db = SessionLocal()
    try:
        session = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        rec = json.loads(session.recommendation_data or "{}") if session.recommendation_data else {}
        intake = json.loads(session.intake_data or "{}")
        extended = json.loads(session.extended_intake_data or "{}")

        # Get friction events for this session
        events = db.query(FrictionEvent).filter(
            FrictionEvent.session_id == session_id
        ).order_by(FrictionEvent.timestamp.asc()).all()

        return _safe_render(request, "admin/audit.html", {
            "request": request,
            "session_id": session_id,
            "intake": intake,
            "extended": extended,
            "rec": rec,
            "rec_json": json.dumps(rec, indent=2, default=str),
            "events": events,
            "session_obj": session,
        })
    finally:
        db.close()


@router.post("/admin/proposal/{session_id}/approve")
async def admin_approve(request: Request, session_id: str):
    """Mark a proposal as operator-approved."""
    _require_admin(request)
    db = SessionLocal()
    try:
        session = db.query(GreenhouseSession).filter(GreenhouseSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session.operator_approved = True
        db.commit()
        return RedirectResponse(url="/admin/proposals", status_code=303)
    finally:
        db.close()


# ════════════════════════════════════════════════════
# I. ADMIN ANALYTICS
# ════════════════════════════════════════════════════

@router.get("/admin/analytics", response_class=HTMLResponse)
async def admin_analytics(request: Request):
    """Funnel analytics and friction analysis."""
    _require_admin(request)
    db = SessionLocal()
    try:
        events = db.query(FrictionEvent).order_by(FrictionEvent.timestamp.asc()).all()
        sessions = db.query(GreenhouseSession).all()
        beta_codes = db.query(BetaCode).all()

        # Funnel counts
        event_counts = defaultdict(int)
        for e in events:
            event_counts[e.event_type] += 1

        # Time-on-page averages
        time_by_type = defaultdict(list)
        for e in events:
            if e.time_on_page_seconds and e.time_on_page_seconds > 0:
                time_by_type[e.event_type].append(e.time_on_page_seconds)

        avg_times = {}
        for k, v in time_by_type.items():
            avg_times[k] = round(sum(v) / len(v), 1) if v else 0

        # Error breakdown
        errors = [e for e in events if e.event_type == "error"]
        error_counts = defaultdict(int)
        for e in errors:
            error_counts[e.error or "unknown"] += 1

        # Beta code usage
        beta_used = sum(1 for b in beta_codes if b.used)
        beta_total = len(beta_codes)

        # Session stats
        total_sessions = len(sessions)
        paid_sessions = sum(1 for s in sessions if s.payment_status == "paid")
        beta_sessions = sum(1 for s in sessions if s.beta_code)
        with_rec = sum(1 for s in sessions if s.recommendation_data)

        funnel = {
            "intake_complete": event_counts.get("intake_complete", 0),
            "preview_view": event_counts.get("preview_view", 0),
            "checkout_start": event_counts.get("checkout_start", 0),
            "checkout_complete": event_counts.get("checkout_complete", 0),
            "extend_complete": event_counts.get("extend_complete", 0),
            "proposal_view": event_counts.get("proposal_view", 0),
            "proposal_download": event_counts.get("proposal_download", 0),
        }

        return _safe_render(request, "admin/analytics.html", {
            "request": request,
            "funnel": funnel,
            "avg_times": avg_times,
            "error_counts": dict(error_counts),
            "beta_used": beta_used,
            "beta_total": beta_total,
            "total_sessions": total_sessions,
            "paid_sessions": paid_sessions,
            "beta_sessions": beta_sessions,
            "with_rec": with_rec,
            "total_events": len(events),
        })
    finally:
        db.close()


# ════════════════════════════════════════════════════
# J. ADMIN CHECKPOINT (Week 4 criteria)
# ════════════════════════════════════════════════════

@router.get("/admin/checkpoint", response_class=HTMLResponse)
async def admin_checkpoint(request: Request):
    """Week 4 checkpoint — auto-calculates CONTINUE / NARROW / PAUSE signals."""
    _require_admin(request)
    db = SessionLocal()
    try:
        sessions = db.query(GreenhouseSession).all()
        events = db.query(FrictionEvent).all()
        beta_codes = db.query(BetaCode).all()

        # Beta sessions that completed full journey
        beta_sessions = [s for s in sessions if s.beta_code]
        beta_complete = [s for s in beta_sessions if s.recommendation_data]
        beta_paid = [s for s in beta_sessions if s.payment_status == "paid"]

        # Event type counts
        event_counts = defaultdict(int)
        for e in events:
            event_counts[e.event_type] += 1

        # Error analysis
        errors = [e for e in events if e.event_type == "error"]

        # Preview-to-checkout drop-off
        preview_views = event_counts.get("preview_view", 0)
        checkout_starts = event_counts.get("checkout_start", 0)

        # Data quality assessment from recommendations
        data_errors = 0
        estimated_heavy = 0
        for s in sessions:
            if s.recommendation_data:
                try:
                    rec = json.loads(s.recommendation_data)
                    assumptions = rec.get("assumptions", [])
                    if any("estimated" in a.lower() for a in assumptions):
                        estimated_heavy += 1
                    gaps = rec.get("component_gaps", [])
                    if len(gaps) > 2:
                        data_errors += 1
                except json.JSONDecodeError:
                    data_errors += 1

        # Signal calculations
        signals = {
            "continue": {
                "beta_journey_complete": {
                    "value": len(beta_complete),
                    "target": 3,
                    "of": min(5, len(beta_sessions)) if beta_sessions else 5,
                    "met": len(beta_complete) >= 3,
                    "label": "Beta users complete full journey (≥3 of first 5)",
                },
                "no_critical_errors": {
                    "value": len(errors),
                    "target": 0,
                    "met": len(errors) == 0,
                    "label": "No critical data errors in proposals",
                },
                "audit_complete": {
                    "value": len([s for s in sessions if s.recommendation_data and s.payment_status == "paid"]),
                    "target": len(beta_paid),
                    "met": all(s.recommendation_data for s in beta_paid) if beta_paid else True,
                    "label": "Audit trail complete for every paid proposal",
                },
            },
            "narrow": {
                "preview_abandon": {
                    "value": preview_views - checkout_starts if preview_views > checkout_starts else 0,
                    "total": preview_views,
                    "triggered": preview_views > 5 and checkout_starts < preview_views * 0.3,
                    "label": "Users complete intake but abandon at preview",
                },
                "data_stale": {
                    "value": estimated_heavy,
                    "total": len([s for s in sessions if s.recommendation_data]),
                    "triggered": estimated_heavy > len(sessions) * 0.5 if sessions else False,
                    "label": "Proposal data frequently stale or estimated",
                },
            },
            "pause": {
                "low_completion": {
                    "value": len(beta_complete),
                    "target": 2,
                    "triggered": len(beta_sessions) >= 5 and len(beta_complete) < 2,
                    "label": "<2 of 5 beta users complete the flow",
                },
                "factual_errors": {
                    "value": data_errors,
                    "triggered": data_errors > 0,
                    "label": "Factual errors found in proposals",
                },
                "critical_errors": {
                    "value": len(errors),
                    "triggered": len(errors) >= 3,
                    "label": "Scoring engine produces wrong recommendations",
                },
            },
        }

        # Overall signal
        continue_met = sum(1 for s in signals["continue"].values() if s.get("met"))
        narrow_triggered = any(s.get("triggered") for s in signals["narrow"].values())
        pause_triggered = any(s.get("triggered") for s in signals["pause"].values())

        if pause_triggered:
            overall = "pause"
        elif narrow_triggered:
            overall = "narrow"
        elif continue_met >= 2:
            overall = "continue"
        else:
            overall = "waiting"

        return _safe_render(request, "admin/checkpoint.html", {
            "request": request,
            "signals": signals,
            "overall": overall,
            "beta_total": len(beta_sessions),
            "beta_complete": len(beta_complete),
            "total_sessions": len(sessions),
            "total_events": len(events),
            "total_errors": len(errors),
        })
    finally:
        db.close()


# ════════════════════════════════════════════════════
# K. ADMIN — GENERATE BETA CODES
# ════════════════════════════════════════════════════

@router.post("/admin/beta/generate")
async def generate_beta_codes(request: Request, count: int = Form(default=15)):
    """Generate single-use beta codes."""
    _require_admin(request)
    db = SessionLocal()
    try:
        codes = []
        for i in range(min(count, 50)):
            code = f"KLARA-{secrets.token_hex(3).upper()}"
            beta = BetaCode(
                id=str(uuid.uuid4()),
                code=code,
                used=False,
                notes=f"Generated batch {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            )
            db.add(beta)
            codes.append(code)
        db.commit()

        return JSONResponse({"codes": codes, "count": len(codes)})
    finally:
        db.close()


# ════════════════════════════════════════════════════
# L. HEALTH CHECK
# ════════════════════════════════════════════════════

@router.get("/greenhouse/health")
async def greenhouse_health():
    """Health check for Railway deployment."""
    db = SessionLocal()
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return JSONResponse({
            "status": "healthy",
            "environment": settings.environment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        return JSONResponse({"status": "unhealthy", "error": str(e)}, status_code=500)
    finally:
        db.close()

