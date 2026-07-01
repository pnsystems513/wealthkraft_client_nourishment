"""
MailerSend email service.

Sends transactional welcome and birthday emails using the MailerSend API.
Required .env keys:
    MAILERSEND_API_KEY — your MailerSend API key
    EMAIL_FROM         — sender email address (must be verified in MailerSend)
    EMAIL_FROM_NAME    — sender display name
"""

import os
import logging
from mailersend import MailerSendClient, EmailBuilder
from app.template.email_template import _welcome_html, _birthday_html

logger = logging.getLogger(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────

_API_KEY = os.getenv("MAILERSEND_API_KEY", "")
_FROM_EMAIL = os.getenv("EMAIL_FROM", "noreply@yourdomain.com")
_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "WealthKraft")


# ─── Internal helper ──────────────────────────────────────────────────────────

def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Low-level function to send an email via MailerSend.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        html_body: HTML content for the email body.

    Returns:
        True if MailerSend accepted the message, False otherwise.
    """
    if not _API_KEY:
        logger.warning(
            "[Email] MAILERSEND_API_KEY is not set. Skipping email to %s.", to_email
        )
        return False

    try:
        ms = MailerSendClient(api_key=_API_KEY)
        email = (EmailBuilder()
            .from_email(_FROM_EMAIL, _FROM_NAME)
            .to_many([{"email": to_email, "name": to_email}])
            .subject(subject)
            .html(html_body)
            .build())
        
        response = ms.emails.send(email)
        logger.info(
            "[Email] ✅ Email '%s' sent to %s | response=%s",
            subject, to_email, response,
        )
        return True
    except Exception as exc:
        logger.exception("[Email] Error while sending to %s: %s", to_email, exc)
        return False


# ─── Public API ───────────────────────────────────────────────────────────────

def send_welcome_email(to_email: str, client_name: str) -> bool:
    """
    Send a welcome email to a newly onboarded client.

    Args:
        to_email: Client's email address.
        client_name: Client's full name.

    Returns:
        True if the email was accepted by SendGrid.
    """
    if not to_email:
        logger.warning("[Email] Skipping welcome email — no email address for %s", client_name)
        return False
    subject = f"Welcome to WealthKraft, {client_name.split()[0]}! 🎉"
    return _send_email(to_email, subject, _welcome_html(client_name))


def send_birthday_email(to_email: str, client_name: str) -> bool:
    """
    Send a birthday email to a client on their birthday.

    Args:
        to_email: Client's email address.
        client_name: Client's full name.

    Returns:
        True if the email was accepted by SendGrid.
    """
    if not to_email:
        logger.warning("[Email] Skipping birthday email — no email address for %s", client_name)
        return False
    subject = f"Happy Birthday, {client_name.split()[0]}! 🎂 From WealthKraft"
    return _send_email(to_email, subject, _birthday_html(client_name))
