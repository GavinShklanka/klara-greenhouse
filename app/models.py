"""Data models — GreenhouseSession + ContactRequest + Proposal + BetaCode + FrictionEvent."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Float, Integer
from app.core.database import Base


class GreenhouseSession(Base):
    """Tracks one user's journey through the greenhouse workflow."""
    __tablename__ = "greenhouse_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="intake")  # intake → plan → action
    # JSON-encoded intake answers
    intake_data = Column(Text, default="{}")
    # JSON-encoded build plan (populated after plan step)
    plan_data = Column(Text, default="{}")
    # Action taken: 'quote', 'diy', 'connect', or None
    action_taken = Column(String, nullable=True)
    # Extended Intake Data
    extended_intake_data = Column(Text, default="{}")
    # Payment status: unpaid, paid, refunded
    payment_status = Column(String, default="unpaid")
    # Full recommendation JSON from routing_service
    recommendation_data = Column(Text, nullable=True)
    # Operator approval gate (first 20 proposals)
    operator_approved = Column(Boolean, default=False)
    # Beta code used (if any)
    beta_code = Column(String, nullable=True)
    # User agent for analytics
    user_agent = Column(String, nullable=True)
    # IP hash for rate limiting (hashed, not raw)
    ip_hash = Column(String, nullable=True)


class ContactRequest(Base):
    """Monetization event — user requested quote, plan, or builder connection."""
    __tablename__ = "contact_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("greenhouse_sessions.id"), nullable=False)
    request_type = Column(String, nullable=False)  # 'quote', 'diy', 'connect'
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Proposal(Base):
    """Paid property-specific greenhouse proposal."""
    __tablename__ = "proposals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("greenhouse_sessions.id"), nullable=False, unique=True)
    proposal_data = Column(Text, default="{}")
    status = Column(String, default="draft")  # draft, reviewed, sent
    generated_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    reviewer_notes = Column(Text, nullable=True)


class BetaCode(Base):
    """Single-use beta codes for free proposal access."""
    __tablename__ = "beta_codes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, unique=True, nullable=False, index=True)
    used = Column(Boolean, default=False)
    used_by_session_id = Column(String, nullable=True)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)  # e.g. "reddit-user-1"


class FrictionEvent(Base):
    """Analytics event for tracking user journey friction points."""
    __tablename__ = "friction_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("greenhouse_sessions.id"), nullable=True)
    event_type = Column(String, nullable=False)
    # Event types:
    #   intake_start, intake_complete, preview_view, checkout_start,
    #   checkout_complete, checkout_abandon, extend_complete,
    #   proposal_view, proposal_download, consultation_request,
    #   error, page_view
    timestamp = Column(DateTime, default=datetime.utcnow)
    page = Column(String, nullable=True)
    time_on_page_seconds = Column(Float, nullable=True)
    error = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    feedback = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)  # extra context as JSON
