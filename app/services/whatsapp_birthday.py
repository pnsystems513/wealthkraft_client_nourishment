"""AiSensy service for sending the birthday WhatsApp campaign template."""

import os
import logging
import httpx

logger = logging.getLogger(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────

_API_KEY          = os.getenv("AISENSY_API_KEY", "")
_API_URL          = os.getenv("ASSIGNMENT_POST_API_URL", "")
_CAMPAIGN_NAME    = os.getenv("AISENSY_CAMPAIGN_NAME", "")
_BIRTHDAY_CAMPAIGN = os.getenv("AISENSY_BIRTHDAY_CAMPAIGN_NAME", _CAMPAIGN_NAME)
_USER_NAME        = os.getenv("AISENSY_USER_NAME", "Wealthkraft")
_BIRTHDAY_MEDIA_URL = os.getenv(
    "AISENSY_BIRTHDAY_MEDIA_URL",
    "https://res.cloudinary.com/scprag8i/image/upload/f_auto,q_auto/WhatsApp_Image_2026-09-17_at_3.58.08_PM",
)
_BIRTHDAY_MEDIA_FILENAME = os.getenv("AISENSY_BIRTHDAY_MEDIA_FILENAME", "birthday_image")

_HEADERS = {"Content-Type": "application/json"}





# ─── Internal sender ──────────────────────────────────────────────────────────

async def _send_template(
    to: str,
    campaign_name: str,
    client_name: str,
    agent_name: str,
    *,
    source: str = "client_nourishiring",
    media: dict | None = None,
    template_var_name: str = "FirstName",
) -> bool:
    """
    Send an AiSensy campaign message.

    Args:
        to: Recipient phone number in E.164 format (e.g. "919876543210").
        campaign_name: AiSensy campaign/template name.
        client_name: Client name used by the approved template.
        agent_name: Assigned agent name sent as the AiSensy user name.
        source: Campaign source value sent to AiSensy.
        media: Optional media payload {"url": ..., "filename": ...}.
        template_var_name: Template variable name used by AiSensy (e.g. "FirstName").

    Returns:
        True if the API accepted the message, False otherwise.
    """
    if not all((_API_KEY, _API_URL, campaign_name)):
        logger.warning(
            "[WhatsApp] AISENSY_API_KEY, ASSIGNMENT_POST_API_URL, or campaign name "
            "is not set. Skipping message to %s.", to
        )
        return False

    first_name = (client_name.split()[0] if client_name else "user").strip() or "user"

    payload: dict = {
        "apiKey": _API_KEY,
        "campaignName": campaign_name,
        "destination": to,
        "userName": agent_name or _USER_NAME,
        "templateParams": [f"${template_var_name}"],
        "source": source or "client_nourishiring",
        "media": media or {},
        "buttons": [],
        "carouselCards": [],
        "location": {},
        "attributes": {},
        "paramsFallbackValue": {template_var_name: first_name},
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(_API_URL, headers=_HEADERS, json=payload)
            if resp.status_code in (200, 201):
                logger.info(
                    "[AiSensy] Template '%s' sent to %s | response: %s",
                    campaign_name, to, resp.json(),
                )
                return True
            else:
                logger.error(
                    "[AiSensy] Failed to send '%s' to %s | status=%s | body=%s",
                    campaign_name, to, resp.status_code, resp.text,
                )
                return False
    except httpx.HTTPError as exc:
        logger.exception("[WhatsApp] HTTP error while sending to %s: %s", to, exc)
        return False


# ─── Public API ───────────────────────────────────────────────────────────────

async def send_birthday_whatsapp(
    to: str,
    client_name: str,
    agent_name: str = "",
    media_url: str | None = None,
) -> bool:
    """
    Send the birthday template to a client on their birthday.

    Args:
        to: Phone number in E.164 format (e.g. "919876543210").
        client_name: Full name of the client.
        agent_name: AiSensy userName (falls back to AISENSY_USER_NAME).
        media_url: Optional HTTPS URL for the media image. If omitted,
                   falls back to AISENSY_BIRTHDAY_MEDIA_URL from .env.

    Returns:
        True if sent successfully.

    Example:
        # With a dynamic CDN URL
        await send_birthday_whatsapp(
            to="919876543210",
            client_name="Parth Gharat",
            media_url="https://cdn.example.com/campaigns/birthday_2026.jpeg",
        )

        # With the default env-configured URL
        await send_birthday_whatsapp(to="919876543210", client_name="Parth Gharat")
    """
    first_name = client_name.split()[0] if client_name else "there"
    logger.info("[WhatsApp] Sending birthday message to %s (%s)", to, client_name)

    # Resolve media URL: use provided value, else fall back to env
    resolved_url = _BIRTHDAY_MEDIA_URL
    if media_url:
        resolved_url = media_url

    media_payload = {
        "url": resolved_url,
        "filename": _BIRTHDAY_MEDIA_FILENAME,
    }

    return await _send_template(
        to,
        _BIRTHDAY_CAMPAIGN,
        first_name,
        agent_name,
        source="new-landing-page form",
        media=media_payload,
        template_var_name="FirstName",
    )
