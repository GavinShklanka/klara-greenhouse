"""Application settings — pydantic-settings from .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """KLARA Greenhouse configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    environment: str = "development"
    debug: bool = True
    database_url: str = "sqlite:///./greenhouse.db"

    # Stripe
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    # Plan pricing (cents)
    plan_price_basic: int = 2900       # $29
    plan_price_premium: int = 7900     # $79

    # Resend (email)
    resend_api_key: str = ""
    notification_email: str = ""       # your email for lead alerts

    # App
    base_url: str = "http://localhost:8100"


settings = Settings()
