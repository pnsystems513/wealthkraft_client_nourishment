"""
Nourishing router — manual trigger endpoints and status check.

Endpoints:
    POST /nourish/trigger/welcome  — Immediately run the welcome job
    POST /nourish/trigger/birthday — Immediately run the birthday job
    GET  /nourish/status           — Return watermark info and scheduler state
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks

from app.jobs.scheduler import welcome_job, birthday_job, _WATERMARK_FILE
from app.schemas.nourish_schemas import TriggerResponse, StatusResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nourish", tags=["Nourishing"])

# ─── Routes ──────────────────────────────────────────────────────────────────

@router.post(
    "/trigger/welcome",
    response_model=TriggerResponse,
    summary="Manually trigger the welcome job",
    description=(
        "Runs the new-client welcome job immediately. "
        "Sends WhatsApp + Email to all clients created after the last watermark. "
        "Useful for testing or backfilling messages after a deployment."
    ),
)
def trigger_welcome(background_tasks: BackgroundTasks):
    logger.info("[API] Manual trigger: welcome_job")
    background_tasks.add_task(welcome_job)
    return TriggerResponse(
        triggered=True,
        job="welcome_job",
        message="Welcome job dispatched to background. Check server logs for results.",
    )


@router.post(
    "/trigger/birthday",
    response_model=TriggerResponse,
    summary="Manually trigger the birthday job",
    description=(
        "Runs the birthday check job immediately. "
        "Sends WhatsApp + Email to all clients whose date_of_birth matches today. "
        "Useful for testing birthday messages."
    ),
)
def trigger_birthday(background_tasks: BackgroundTasks):
    logger.info("[API] Manual trigger: birthday_job")
    background_tasks.add_task(birthday_job)
    return TriggerResponse(
        triggered=True,
        job="birthday_job",
        message="Birthday job dispatched to background. Check server logs for results.",
    )


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Get nurturing engine status",
    description="Returns the current watermark timestamp and server UTC time.",
)
def get_status():
    watermark_ts: str | None = None
    try:
        wf = Path(_WATERMARK_FILE)
        if wf.exists():
            data = json.loads(wf.read_text())
            watermark_ts = data.get("last_created_at")
    except Exception as exc:
        logger.warning("[API] Could not read watermark: %s", exc)

    return StatusResponse(
        service="WealthKraft Client Nurturing Engine",
        watermark_last_created_at=watermark_ts,
        current_utc=datetime.now(timezone.utc).isoformat(),
    )
