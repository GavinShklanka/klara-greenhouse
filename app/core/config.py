"""Application settings — pydantic-settings from .env."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_db_url() -> str:
    """Use Railway persistent volume if RAILWAY_VOLUME_MOUNT_PATH is set."""
    vol = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")
    if vol:
        return f"sqlite:///{vol}/klara.db"
    return "sqlite:///./klara.db"


class Settings(BaseSettings):
    """KLARA Greenhouse configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    environment: str = "development"  # dev | staging | production
    debug: bool = True
    database_url: str = _default_db_url()

    # Stripe
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""  # not used yet — inline pricing

    # Plan pricing (cents)
    plan_price_basic: int = 2900       # $29
    plan_price_premium: int = 7900     # $79

    # Resend (email)
    resend_api_key: str = ""
    notification_email: str = ""       # your email for lead alerts

    # SMTP (proposal email delivery)
    smtp_host: str = ""
    smtp_user: str = ""
    smtp_pass: str = ""

    # Admin auth
    admin_password: str = "klara-admin-2026"  # override via env var

    # App
    base_url: str = "http://localhost:8000"


settings = Settings()
