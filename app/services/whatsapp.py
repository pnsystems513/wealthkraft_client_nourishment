"""
WhatsApp Cloud API service.

Sends pre-approved template messages via the Meta WhatsApp Business Cloud API.
Required .env keys:
    WHATSAPP_PHONE_NUMBER_ID  — your Meta Phone Number ID
    WHATSAPP_ACCESS_TOKEN     — your Meta System User / Page Access Token
"""

import os
import logging
import httpx

logger = logging.getLogger(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────

_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
_WELCOME_TEMPLATE = "welcome_client"
_BIRTHDAY_TEMPLATE = "birthday_client"
_LANG = "en_US"

_API_URL = f"https://graph.facebook.com/v19.0/{_PHONE_NUMBER_ID}/messages"

_HEADERS = {
    "Authorization": f"Bearer {_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


# ─── Internal helper ──────────────────────────────────────────────────────────

async def _send_template(
    to: str,
    template_name: str,
    components: list | None = None,
) -> bool:
    """
    Low-level function that calls the WhatsApp Cloud API to send a template message.

    Args:
        to: Recipient phone number in E.164 format (e.g. "919876543210").
        template_name: Meta-approved template name.
        components: Optional list of template component overrides (headers, body params, etc.).

    Returns:
        True if the API accepted the message, False otherwise.
    """
    if not _PHONE_NUMBER_ID or not _ACCESS_TOKEN:
        logger.warning(
            "[WhatsApp] WHATSAPP_PHONE_NUMBER_ID or WHATSAPP_ACCESS_TOKEN is not set. "
            "Skipping message to %s.", to
        )
        return False

    payload: dict = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": _LANG},
        },
    }
    if components:
        payload["template"]["components"] = components

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(_API_URL, headers=_HEADERS, json=payload)
            if resp.status_code in (200, 201):
                logger.info(
                    "[WhatsApp] ✅ Template '%s' sent to %s | response: %s",
                    template_name, to, resp.json(),
                )
                return True
            else:
                logger.error(
                    "[WhatsApp] ❌ Failed to send '%s' to %s | status=%s | body=%s",
                    template_name, to, resp.status_code, resp.text,
                )
                return False
    except httpx.HTTPError as exc:
        logger.exception("[WhatsApp] HTTP error while sending to %s: %s", to, exc)
        return False


# ─── Public API ───────────────────────────────────────────────────────────────

async def send_welcome_whatsapp(to: str, client_name: str) -> bool:
    """
    Send the welcome template to a newly onboarded client.

    The template is expected to accept one body parameter: {{1}} = client first name.
    Adjust the components list below to match your approved template structure.

    Args:
        to: Phone number in E.164 format (e.g. "919876543210").
        client_name: Full name of the client (first name used in the greeting).

    Returns:
        True if sent successfully.
    """
    first_name = client_name.split()[0] if client_name else "there"
    components = [
        {
            "type": "body",
            "parameters": [
                {"type": "text", "text": first_name},
            ],
        }
    ]
    logger.info("[WhatsApp] Sending welcome message to %s (%s)", to, client_name)
    return await _send_template(to, _WELCOME_TEMPLATE, components)


async def send_birthday_whatsapp(to: str, client_name: str) -> bool:
    """
    Send the birthday template to a client on their birthday.

    The template is expected to accept one body parameter: {{1}} = client first name.
    Adjust the components list below to match your approved template structure.

    Args:
        to: Phone number in E.164 format (e.g. "919876543210").
        client_name: Full name of the client.

    Returns:
        True if sent successfully.
    """
    first_name = client_name.split()[0] if client_name else "there"
    components = [
        {
            "type": "body",
            "parameters": [
                {"type": "text", "text": first_name},
            ],
        }
    ]
    logger.info("[WhatsApp] Sending birthday message to %s (%s)", to, client_name)
    return await _send_template(to, _BIRTHDAY_TEMPLATE, components)
