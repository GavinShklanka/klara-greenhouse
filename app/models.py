"""Data models — GreenhouseSession + ContactRequest."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
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
