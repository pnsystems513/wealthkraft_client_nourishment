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
import threading
from datetime import datetime, date, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import extract, func

from app.database import LMSSessionLocal, CMSSessionLocal
from app.models.lms_read_db import Lead, LeadStage
from app.models.cms_read_db import Client, SipHistory
from app.services.whatsapp_welcome import send_welcome_whatsapp
from app.services.whatsapp_birthday import send_birthday_whatsapp
from app.services.whatsapp_sip import send_sip_anniversary_whatsapp
from app.services.email import send_welcome_email, send_birthday_email

logger = logging.getLogger(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────

_WELCOME_INTERVAL_SECONDS = 2  # Fixed 2-second interval for welcome job
_BIRTHDAY_INTERVAL = 1440  # 1 day
_SIP_ANNIVERSARY_INTERVAL = 1440  # 1 day
_SCHEDULER_TIMEZONE = "UTC"

# Watermark file — persists the last processed created_at timestamp
_WATERMARK_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_WATERMARK_FILE = _WATERMARK_DIR / "watermark.json"
_STATE_LOCK = threading.Lock()

# ─── State management helpers ───────────────────────────────────────────────────

def _load_state() -> dict:
    """Load the persisted state (watermarks, sent lists) from the JSON file."""
    try:
        if _WATERMARK_FILE.exists():
            return json.loads(_WATERMARK_FILE.read_text())
    except Exception as exc:
        logger.warning("[Scheduler] Could not load state: %s", exc)
    return {}


def _save_state(data: dict) -> bool:
    """Merge and persist state to the JSON file."""
    try:
        with _STATE_LOCK:
            _WATERMARK_DIR.mkdir(parents=True, exist_ok=True)
            existing = _load_state()
            existing.update(data)
            temporary_file = _WATERMARK_FILE.with_suffix(".tmp")
            temporary_file.write_text(json.dumps(existing), encoding="utf-8")
            temporary_file.replace(_WATERMARK_FILE)
        return True
    except Exception as exc:
        logger.warning("[Scheduler] Could not save state: %s", exc)
        return False

# ─── Helper: run async from sync context ─────────────────────────────────────

def _run_async(coro):
    """Run an async coroutine from a synchronous APScheduler job."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in an event loop (e.g., some test setups), schedule it
            asyncio.ensure_future(coro)
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop in this thread — create one
        return asyncio.run(coro)


# ─── welcome_job ─────────────────────────────────────────────────────────────────────
# ───  ─────────────────────────────────────────────────────────────────────

def welcome_job() -> None:
    """
    Poll LMS for leads that moved into the CONVERTED stage since the last run.
    For each newly converted lead, fire both the WhatsApp welcome message and
    the welcome email. Uses last_stage_changed_at as the watermark so the same
    lead is never processed twice.
    """
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
                _run_async(send_welcome_whatsapp(phone, name, lead.assigned_name or ""))
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

# ─── birthday_job ─────────────────────────────────────────────────────────────────────
# ─── ─────────────────────────────────────────────────────────────────────

def birthday_job() -> None:
    """
    Query LMS leads whose date_of_birth matches today's month and day.
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
            if stored_date != (date.fromisoformat(stored_date_str) if stored_date_str else None):
                _save_state({
                    "birthday_sent_date": stored_date.isoformat(),
                    "birthday_sent_ids": list(sent_ids)
                })
            return

        logger.info("[BirthdayJob] Found %d birthday client(s).", len(birthday_clients))

        new_sent = False
        for client in birthday_clients:
            client_id_str = str(client.id)
            name = client.full_name or "Valued Client"
            if client_id_str in sent_ids:
                logger.info(
                    "[BirthdayJob] Already sent to %s today — skipping.", name
                )
                continue

            phone = client.mobile_number or ""
            email = client.email or ""

            logger.info(
                "[BirthdayJob] 🎂 Birthday: %s | phone=%s | email=%s", name, phone, email
            )

            # WhatsApp
            if phone:
                agent_name = client.agent_username or client.owner_username or ""
                _run_async(send_birthday_whatsapp(phone, name, agent_name))
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

    except Exception as exc:
        logger.exception("[BirthdayJob] Unexpected error: %s", exc)
    finally:
        db.close()

def _today_in_scheduler_timezone() -> date:
    """Return today's date in the scheduler's configured UTC timezone."""
    return datetime.now(timezone.utc).date()


def sip_anniversary_job() -> None:
    """Send the first-anniversary message for each client's earliest SIP."""
    today = _today_in_scheduler_timezone()
    state = _load_state()
    stored_date = state.get("sip_anniversary_sent_date")
    sent_ids = (
        set(state.get("sip_anniversary_sent_ids", []))
        if stored_date == today.isoformat()
        else set()
    )

    db = CMSSessionLocal()
    try:
        oldest_sip_dates = (
            db.query(
                SipHistory.client_id.label("client_id"),
                func.min(SipHistory.created_at).label("oldest_sip_start_date"),
            )
            .filter(
                SipHistory.created_at.isnot(None)
            )
            .group_by(SipHistory.client_id)
            .subquery()
        )
        anniversaries = (
            db.query(Client, oldest_sip_dates.c.oldest_sip_start_date)
            .join(oldest_sip_dates, oldest_sip_dates.c.client_id == Client.id)
            .filter(
                extract("month", oldest_sip_dates.c.oldest_sip_start_date) == today.month,
                extract("day", oldest_sip_dates.c.oldest_sip_start_date) == today.day,
                extract("year", oldest_sip_dates.c.oldest_sip_start_date) == today.year - 1,
            )
            .all()
        )

        for client, oldest_sip_start_date in anniversaries:
            sent_key = f"{client.id}:{today.year}"
            if sent_key in sent_ids:
                continue

            phone = client.mobile_number or ""
            if not phone:
                logger.warning(
                    "[SipAnniversaryJob] No phone for client %s — skipping.",
                    client.full_name,
                )
                continue

            agent_name = client.agent_username or client.owner_username or ""
            was_sent = _run_async(
                send_sip_anniversary_whatsapp(
                    phone, client.full_name or "Valued Client", agent_name
                )
            )
            if was_sent is not True:
                logger.warning(
                    "[SipAnniversaryJob] Message to %s was not confirmed; "
                    "leaving it eligible for retry.",
                    client.full_name,
                )
                continue

            sent_ids.add(sent_key)
            if not _save_state({
                "sip_anniversary_sent_date": today.isoformat(),
                "sip_anniversary_sent_ids": sorted(sent_ids),
            }):
                raise RuntimeError(
                    "Could not persist SIP anniversary notification state"
                )

            logger.info(
                "[SipAnniversaryJob] First SIP anniversary (%s) message sent to %s.",
                oldest_sip_start_date,
                client.full_name,
            )
    except Exception as exc:
        logger.exception("[SipAnniversaryJob] Unexpected error: %s", exc)
    finally:
        db.close()


# ─── Scheduler factory ────────────────────────────────────────────────────────

def create_scheduler() -> BackgroundScheduler:
    """
    Create and configure the APScheduler BackgroundScheduler with nurturing jobs.

    Returns:
        A configured (but not yet started) BackgroundScheduler instance.
    """
    scheduler = BackgroundScheduler(timezone=_SCHEDULER_TIMEZONE)

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

    # SIP anniversary job — check for anniversary dates every day
    scheduler.add_job(
        sip_anniversary_job,
        trigger="interval",
        minutes=_SIP_ANNIVERSARY_INTERVAL,
        id="sip_anniversary_job",
        name="SIP Anniversary WhatsApp Sender",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=120,
        next_run_time=datetime.now(timezone.utc),
    )

    logger.info(
        "[Scheduler] Registered 3 jobs | welcome every %d sec | "
        "birthday every %d min | SIP anniversary every %d min",
        _WELCOME_INTERVAL_SECONDS,
        _BIRTHDAY_INTERVAL,
        _SIP_ANNIVERSARY_INTERVAL,
    )
    return scheduler
