import os
import json
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import LMSBase, CMSBase, lms_engine, cms_engine
from app.jobs.scheduler import create_scheduler
from app.routes.nourish_routes import router as nourish_router

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Lifespan: DB tables + scheduler
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create LMS tables (CMS tables are owned by CMS — never auto-create there)
    LMSBase.metadata.create_all(bind=lms_engine)

    scheduler = create_scheduler()
    scheduler.start()
    logger.info("[App] Scheduler started with %d job(s).", len(scheduler.get_jobs()))

    yield  # app is running

    scheduler.shutdown(wait=False)
    logger.info("[App] Scheduler stopped.")

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────

_raw_origins = os.getenv("ALLOWED_ORIGIN")
if _raw_origins:
    try:
        ALLOWED_ORIGINS = json.loads(_raw_origins)
    except (json.JSONDecodeError, TypeError):
        ALLOWED_ORIGINS = []
else:
    ALLOWED_ORIGINS = []

# ─────────────────────────────────────────────
# App
# ─────────────────────────────────────────────

app = FastAPI(
    title="WealthKraft Client Nurturing Engine",
    description=(
        "Microservice that reads CMS & LMS data and proactively nurtures clients "
        "via WhatsApp (Meta Cloud API) and Email (mailer send).\n\n"
        "**Automated flows:**\n"
        "- 🎉 **Welcome** — Sent when a new client is onboarded in CMS\n"
        "- 🎂 **Birthday** — Sent on the client's birthday every year\n\n"
        "**Manual triggers** available under `/nourish/trigger/*` for testing."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────

app.include_router(nourish_router)

# ─────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────

@app.get("/", tags=["Health"], summary="Health check")
def health_check():
    return {
        "status": "ok",
        "service": "WealthKraft Client Nourishing Engine",
        "version": "1.0.0",
    }