"""Email service — Resend-based notifications for Klara Greenhouse."""

import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_notification_email(data: dict) -> bool:
    """Send internal notification email when a user takes action.

    Args:
        data: dict with keys: type, email, location, budget, name, notes
    """
    if not settings.resend_api_key or not settings.notification_email:
        logger.info("[EMAIL] Skipped — RESEND_API_KEY or NOTIFICATION_EMAIL not set")
        return False

    try:
        import resend
        resend.api_key = settings.resend_api_key

        action_type = data.get("type", "unknown")
        email = data.get("email", "—")
        location = data.get("location", "—")
        budget = data.get("budget", "—")
        name = data.get("name", "—")
        notes = data.get("notes", "")

        subject_map = {
            "checkout": "💰 New Plan Purchase",
            "quote": "📋 New Builder Quote Request",
            "consultation": "📞 New Consultation Request",
        }

        html = f"""
        <div style="font-family: -apple-system, sans-serif; max-width: 500px;">
            <h2 style="color: #FFD60A; background: #0b0b0b; padding: 16px; margin: 0;">
                Klara Greenhouse — {subject_map.get(action_type, 'New Lead')}
            </h2>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; color: #666;">Type</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 600;">{action_type}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; color: #666;">Email</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{email}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; color: #666;">Name</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{name}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; color: #666;">Location</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{location}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; color: #666;">Budget</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{budget}</td></tr>
            </table>
            {"<p style='padding: 8px; color: #666; font-size: 13px;'>Notes: " + notes + "</p>" if notes else ""}
        </div>
        """

        # Send to both notification emails
        recipients = [settings.notification_email]
        secondary = "gavin.shklanka@smu.ca"
        if secondary not in recipients:
            recipients.append(secondary)

        resend.Emails.send({
            "from": "Klara <onboarding@resend.dev>",
            "to": recipients,
            "subject": subject_map.get(action_type, "New Klara Lead"),
            "html": html,
        })

        logger.info(f"[EMAIL] Notification sent for {action_type} → {settings.notification_email}")
        return True

    except Exception as e:
        logger.error(f"[EMAIL] Failed to send: {e}")
        return False


def send_user_confirmation(email: str, action_type: str, plan_data: dict = None) -> bool:
    """Send confirmation email to the user after their action."""
    if not settings.resend_api_key:
        logger.info("[EMAIL] Skipped user confirmation — RESEND_API_KEY not set")
        return False

    try:
        import resend
        resend.api_key = settings.resend_api_key

        subject_map = {
            "checkout": "Your Greenhouse Build Plan",
            "quote": "Your Builder Quote Request — Confirmed",
            "consultation": "Your Consultation Request — Confirmed",
        }

        body_map = {
            "checkout": """
                <h2>Your plan is on its way!</h2>
                <p>Thank you for getting your greenhouse build plan. Here's what's included:</p>
                <ul>
                    <li>Complete materials list with quantities & local sources</li>
                    <li>Step-by-step build instructions</li>
                    <li>Foundation calculations for your region</li>
                    <li>Crop calendar with planting dates</li>
                    <li>Solar positioning & ventilation setup</li>
                </ul>
                <p><strong>Next steps:</strong></p>
                <ol>
                    <li>Review your plan</li>
                    <li>Choose your build path — DIY or get a builder quote</li>
                    <li>Source locally — seeds, materials, and support</li>
                </ol>
            """,
            "quote": """
                <h2>Quote Request Received</h2>
                <p>We've sent your greenhouse plan to a local Nova Scotia builder.
                You'll receive a contact introduction and quote within 48 hours.</p>
            """,
            "consultation": """
                <h2>Consultation Request Received</h2>
                <p>A greenhouse specialist in your area will reach out to schedule
                your 15-minute consultation. Expect to hear back within 24–48 hours.</p>
            """,
        }

        html = f"""
        <div style="font-family: -apple-system, sans-serif; max-width: 500px; padding: 20px;">
            {body_map.get(action_type, "<p>Thank you for your interest in Klara Greenhouse.</p>")}
            <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
            <p style="font-size: 12px; color: #999;">
                Built for Nova Scotia · Klara Greenhouse
            </p>
        </div>
        """

        resend.Emails.send({
            "from": "Klara <onboarding@resend.dev>",
            "to": [email],
            "subject": subject_map.get(action_type, "Klara Greenhouse — Confirmation"),
            "html": html,
        })

        logger.info(f"[EMAIL] User confirmation sent to {email} for {action_type}")
        return True

    except Exception as e:
        logger.error(f"[EMAIL] Failed user confirmation: {e}")
        return False
