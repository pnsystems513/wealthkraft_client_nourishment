"""
APScheduler-based job scheduler for the Client Nurturing Engine.

Jobs:
    welcome_job  — Polls LMS every N minutes for newly converted leads.
                   Sends a welcome WhatsApp message + email for each converted lead.

    birthday_job — Runs every N minutes and checks for clients whose date_of_birth
                   matches today's month and day. Sends a birthday WhatsApp + email.

Deduplication:
    • welcome_job  : Uses a watermark file (data/watermark.json) to persist the last
                     processed last_stage_changed_at timestamp across restarts.
    • birthday_job : Uses an in-memory set (reset daily) so the same client doesn't
                     times on the same day.

"""

import os
import json
import asyncio
import logging
from datetime import datetime, date, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import extract

from app.database import CMSSessionLocal, LMSSessionLocal
from app.models.cms_read_db import Client
from app.models.lms_read_db import Lead, LeadStage
from app.services.whatsapp import send_welcome_whatsapp, send_birthday_whatsapp
from app.services.email import send_welcome_email, send_birthday_email

logger = logging.getLogger(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────

_WELCOME_INTERVAL_SECONDS = 2  # Fixed 2-second interval for welcome job
_BIRTHDAY_INTERVAL = 1440  # 1 day

# Watermark file — persists the last processed created_at timestamp
_WATERMARK_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_WATERMARK_FILE = _WATERMARK_DIR / "watermark.json"

# ─── State management helpers ───────────────────────────────────────────────────

def _load_state() -> dict:
    """Load the persisted state (watermarks, sent lists) from the JSON file."""
    try:
        if _WATERMARK_FILE.exists():
            return json.loads(_WATERMARK_FILE.read_text())
    except Exception as exc:
        logger.warning("[Scheduler] Could not load state: %s", exc)
    return {}


def _save_state(data: dict) -> None:
    """Merge and persist state to the JSON file."""
    try:
        _WATERMARK_DIR.mkdir(parents=True, exist_ok=True)
        existing = _load_state()
        existing.update(data)
        _WATERMARK_FILE.write_text(json.dumps(existing))
    except Exception as exc:
        logger.warning("[Scheduler] Could not save state: %s", exc)

# ─── Helper: run async from sync context ─────────────────────────────────────

def _run_async(coro):
    """Run an async coroutine from a synchronous APScheduler job."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in an event loop (e.g., some test setups), schedule it
            asyncio.ensure_future(coro)
        else:
            loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop in this thread — create one
        asyncio.run(coro)


# ─── welcome_job ─────────────────────────────────────────────────────────────────────
# ───  ─────────────────────────────────────────────────────────────────────

def welcome_job() -> None:
    """
    Poll LMS for leads that moved into the CONVERTED stage since the last run.
    For each newly converted lead, fire both the WhatsApp welcome message and
    the welcome email. Uses last_stage_changed_at as the watermark so the same
    lead is never processed twice.
    """
    logger.info("[WelcomeJob] Starting run at %s", datetime.now(timezone.utc).isoformat())

    state = _load_state()
    ts_str = state.get("last_created_at")
    watermark = datetime.fromisoformat(ts_str) if ts_str else None  # datetime | None — last processed last_stage_changed_at
    db = LMSSessionLocal()

    try:
        query = (
            db.query(Lead)
            .filter(
                Lead.current_stage == LeadStage.CONVERTED,
                Lead.last_stage_changed_at.isnot(None),
            )
            .order_by(Lead.last_stage_changed_at.asc())
        )

        if watermark:
            # Only fetch leads converted strictly after the last watermark
            query = query.filter(Lead.last_stage_changed_at > watermark)

        new_leads: list[Lead] = query.all()

        if not new_leads:
            logger.info("[WelcomeJob] No newly converted leads found.")
            return

        logger.info("[WelcomeJob] Found %d newly converted lead(s) to welcome.", len(new_leads))

        latest_ts: datetime | None = watermark

        for lead in new_leads:
            name  = lead.name or "Valued Client"
            phone = lead.mobile_number or ""
            email = lead.email or ""

            logger.info(
                "[WelcomeJob] Processing lead: %s | phone=%s | email=%s",
                name, phone, email,
            )

            # Send WhatsApp welcome (skip if no phone number)
            if phone:
                _run_async(send_welcome_whatsapp(phone, name))
            else:
                logger.warning("[WelcomeJob] No phone for lead %s — skipping WhatsApp.", name)

            # Send email welcome (skip if no email)
            if email:
                send_welcome_email(email, name)
            else:
                logger.warning("[WelcomeJob] No email for lead %s — skipping email.", name)

            # Advance watermark to the most recent last_stage_changed_at processed
            if lead.last_stage_changed_at:
                if latest_ts is None or lead.last_stage_changed_at > latest_ts:
                    latest_ts = lead.last_stage_changed_at

        if latest_ts:
            _save_state({"last_created_at": latest_ts.isoformat()})
            logger.info("[WelcomeJob] Watermark updated to %s", latest_ts.isoformat())

    except Exception as exc:
        logger.exception("[WelcomeJob] Unexpected error: %s", exc)
    finally:
        db.close()

    logger.info("[WelcomeJob] Run complete.")

# ─── birthday_job ─────────────────────────────────────────────────────────────────────
# ─── ─────────────────────────────────────────────────────────────────────

def birthday_job() -> None:
    """
    Query CMS for clients whose date_of_birth matches today's month and day.
    For each birthday client (not already sent today), fire WhatsApp + email.
    Deduplicates via an in-memory set that resets each calendar day.
    """
    state = _load_state()
    stored_date_str = state.get("birthday_sent_date")
    stored_date = date.fromisoformat(stored_date_str) if stored_date_str else None
    
    # Load previously sent IDs for the stored date
    sent_ids = set(state.get("birthday_sent_ids", []))
    
    today = date.today()

    # Reset dedup set at the start of a new calendar day
    if stored_date != today:
        sent_ids = set()
        stored_date = today

    logger.info(
        "[BirthdayJob] Starting run for %s at %s",
        today.isoformat(), datetime.now(timezone.utc).isoformat(),
    )

    db = CMSSessionLocal()
    try:
        birthday_clients: list[Client] = (
            db.query(Client)
            .filter(
                Client.date_of_birth.isnot(None),
                extract("month", Client.date_of_birth) == today.month,
                extract("day", Client.date_of_birth) == today.day,
            )
            .all()
        )

        if not birthday_clients:
            logger.info("[BirthdayJob] No birthdays today.")
            if stored_date != (date.fromisoformat(stored_date_str) if stored_date_str else None):
                _save_state({
                    "birthday_sent_date": stored_date.isoformat(),
                    "birthday_sent_ids": list(sent_ids)
                })
                logger.info("[BirthdayJob] Persisted new date to watermark file.")
            return

        logger.info("[BirthdayJob] Found %d birthday client(s).", len(birthday_clients))

        new_sent = False
        for client in birthday_clients:
            client_id_str = str(client.id)
            if client_id_str in sent_ids:
                logger.info(
                    "[BirthdayJob] Already sent to %s today — skipping.", client.full_name
                )
                continue

            name = client.full_name or "Valued Client"
            phone = client.mobile_number or ""
            email = client.email or ""

            logger.info(
                "[BirthdayJob] 🎂 Birthday: %s | phone=%s | email=%s", name, phone, email
            )

            # WhatsApp
            if phone:
                _run_async(send_birthday_whatsapp(phone, name))
            else:
                logger.warning("[BirthdayJob] No phone for %s — skipping WhatsApp.", name)

            # Email
            if email:
                send_birthday_email(email, name)
            else:
                logger.warning("[BirthdayJob] No email for %s — skipping email.", name)

            sent_ids.add(client_id_str)
            new_sent = True

        # Persist the birthday state if anything changed or it's a new day
        if new_sent or stored_date != (date.fromisoformat(stored_date_str) if stored_date_str else None):
            _save_state({
                "birthday_sent_date": stored_date.isoformat(),
                "birthday_sent_ids": list(sent_ids)
            })
            logger.info("[BirthdayJob] Birthday state persisted to watermark file.")

    except Exception as exc:
        logger.exception("[BirthdayJob] Unexpected error: %s", exc)
    finally:
        db.close()

    logger.info("[BirthdayJob] Run complete.")


# ─── Scheduler factory ────────────────────────────────────────────────────────

def create_scheduler() -> BackgroundScheduler:
    """
    Create and configure the APScheduler BackgroundScheduler with both nurturing jobs.

    Returns:
        A configured (but not yet started) BackgroundScheduler instance.
    """
    scheduler = BackgroundScheduler(timezone="UTC")

    # Welcome job — poll for new clients every 2 seconds
    scheduler.add_job(
        welcome_job,
        trigger="interval",
        seconds=_WELCOME_INTERVAL_SECONDS,
        id="welcome_job",
        name="New Client Welcome Sender",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=120,
        # Also run once immediately at startup so we don't wait a full interval
        next_run_time=datetime.now(timezone.utc),
    )

    # Birthday job — check for birthdays every N minutes
    scheduler.add_job(
        birthday_job,
        trigger="interval",
        minutes=_BIRTHDAY_INTERVAL,
        id="birthday_job",
        name="Client Birthday Sender",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=120,
        next_run_time=datetime.now(timezone.utc),
    )

    logger.info(
        "[Scheduler] Registered 2 jobs | welcome every %d sec | birthday every %d min",
        _WELCOME_INTERVAL_SECONDS,
        _BIRTHDAY_INTERVAL,
    )
    return scheduler
