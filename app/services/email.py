"""
Zoho ZeptoMail email service.

Sends transactional welcome and birthday emails using the Zoho ZeptoMail API.
Required .env keys:
    ZEPTOMAIL_API_KEY — your ZeptoMail Send Mail Token
    ZEPTOMAIL_URL      — your ZeptoMail API URL (defaults to https://api.zeptomail.in/v1.1/email)
    EMAIL_FROM         — sender email address (must be verified in ZeptoMail)
    EMAIL_FROM_NAME    — sender display name
"""

import os
import logging
import base64
import requests
from app.template.email_template import (
    _welcome_html, _birthday_html,
    WELCOME_IMG_B64, BIRTHDAY_IMG_B64,
    WELCOME_IMG_CID, BIRTHDAY_IMG_CID,
)

logger = logging.getLogger(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────

_API_KEY       = os.getenv("ZEPTOMAIL_API_KEY", "")
_API_URL       = os.getenv("ZEPTOMAIL_URL", "https://api.zeptomail.in/v1.1/email")
_FROM_EMAIL    = os.getenv("EMAIL_FROM", "noreply@yourdomain.com")
_FROM_NAME     = os.getenv("EMAIL_FROM_NAME", "WealthKraft")


# ─── Internal helper ──────────────────────────────────────────────────────────

def _send_email(
    to_email: str,
    subject: str,
    html_body: str,
    inline_attachments: list | None = None,
) -> bool:
    """
    Low-level function to send an email via Zoho ZeptoMail.

    Args:
        to_email:            Recipient email address.
        subject:             Email subject line.
        html_body:           HTML content for the email body.
        inline_attachments:  Optional list of dicts:
                             [{"filename": ..., "content": <b64>, "disposition": "inline", "id": ...}]

    Returns:
        True if ZeptoMail accepted the message, False otherwise.
    """
    if not _API_KEY:
        logger.warning(
            "[Email] ZEPTOMAIL_API_KEY is not set. Skipping email to %s.", to_email
        )
        return False

    headers = {
        "Authorization": f"Zoho-enczapikey {_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "from": {
            "address": _FROM_EMAIL,
            "name": _FROM_NAME
        },
        "to": [
            {
                "email_address": {
                    "address": to_email,
                    "name": to_email
                }
            }
        ],
        "subject": subject,
        "htmlbody": html_body,
    }

    if inline_attachments:
        inline_images = []
        for item in inline_attachments:
            mime_type = "image/jpeg"
            if item["filename"].endswith(".png"):
                mime_type = "image/png"
            
            inline_images.append({
                "mime_type": mime_type,
                "name": item["filename"],
                "content": item["content"],
                "cid": item.get("id") or item.get("content_id")
            })
        payload["inline_images"] = inline_images

    try:
        response = requests.post(_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(
            "[Email] ✅ Email '%s' sent to %s | response=%s",
            subject, to_email, response.text,
        )
        return True
    except Exception as exc:
        logger.exception("[Email] Error while sending to %s: %s", to_email, exc)
        if isinstance(exc, requests.exceptions.HTTPError):
            logger.error("[Email] Response body: %s", exc.response.text)
        return False


# ─── Public API ───────────────────────────────────────────────────────────────

def send_welcome_email(to_email: str, client_name: str) -> bool:
    """
    Send a welcome email to a newly onboarded client.

    Args:
        to_email:    Client's email address.
        client_name: Client's full name.

    Returns:
        True if the email was accepted by ZeptoMail.
    """
    if not to_email:
        logger.warning("[Email] Skipping welcome email — no email address for %s", client_name)
        return False

    subject = f"Welcome to WealthKraft, {client_name.split()[0]}! 🎉"

    inline_attachments = [
        {
            "filename": "welcome.jpeg",
            "content": WELCOME_IMG_B64,
            "disposition": "inline",
            "id": WELCOME_IMG_CID,
        }
    ]

    return _send_email(to_email, subject, _welcome_html(client_name), inline_attachments)


def send_birthday_email(to_email: str, client_name: str) -> bool:
    """
    Send a birthday email to a client on their birthday.

    Args:
        to_email:    Client's email address.
        client_name: Client's full name.

    Returns:
        True if the email was accepted by ZeptoMail.
    """
    if not to_email:
        logger.warning("[Email] Skipping birthday email — no email address for %s", client_name)
        return False

    subject = f"Happy Birthday, {client_name.split()[0]}! 🎂 From WealthKraft"

    inline_attachments = [
        {
            "filename": "birthday.jpeg",
            "content": BIRTHDAY_IMG_B64,
            "disposition": "inline",
            "id": BIRTHDAY_IMG_CID,
        }
    ]

    return _send_email(to_email, subject, _birthday_html(client_name), inline_attachments)
