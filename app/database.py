from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# LMS DATABASE  (leads - Read only)
# ─────────────────────────────────────────────
LMS_DATABASE_URL = os.getenv("LMS_DATABASE_URL")
if not LMS_DATABASE_URL:
    raise RuntimeError("LMS_DATABASE_URL is not set in environment")

lms_engine = create_engine(LMS_DATABASE_URL, pool_pre_ping=True)
LMSSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=lms_engine)
LMSBase = declarative_base()

# ─────────────────────────────────────────────
# CMS DATABASE  (clients - Read Only)
# ─────────────────────────────────────────────
CMS_DATABASE_URL = os.getenv("CMS_DATABASE_URL") 
if not CMS_DATABASE_URL:
    raise RuntimeError("CMS_DATABASE_URL is not set in environment")

cms_engine = create_engine(CMS_DATABASE_URL, pool_pre_ping=True)
CMSSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cms_engine)
CMSBase = declarative_base()

# Alias used by model_cms.py (full CMS model set)
Base = CMSBase

# ─────────────────────────────────────────────
# FastAPI dependency helpers
# ─────────────────────────────────────────────

def get_lms_db():
    db = LMSSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_cms_db():
    db = CMSSessionLocal()
    try:
        yield db
    finally:
        db.close()


print(f"[DB] LMS -> {LMS_DATABASE_URL}")
print(f"[DB] CMS -> {CMS_DATABASE_URL}")