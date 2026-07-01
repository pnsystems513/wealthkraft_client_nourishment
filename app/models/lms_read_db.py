import enum
import uuid
from datetime import datetime, timezone

def _now():
    return datetime.now(timezone.utc)

def generate_uuid() -> str:
    return str(uuid.uuid4())
from sqlalchemy import (
    Column, Integer, String, Boolean, Float,
    JSON, DECIMAL, DateTime, ForeignKey, Text, Date,
    Enum as SAEnum
)
from sqlalchemy.sql import func

from app.database import LMSBase

# =========================
# ENUMS
# =========================


class ClientProfile(str, enum.Enum):
    BUSINESS = "business"
    CORPORATE = "corporate"
    NRI = "nri"
    RETIRED = "retired"
    RA = "ra"
    SALARIED = "salaried"
    STUDENT = "student"
    HOUSEWIFE = "housewife"
    GOVERNMENT = "government"
    MINOR = "minor"    

class SalaryCategory(str, enum.Enum):
    BELOW_25K = "below 25k"
    SALARY_25K_50K = "25k-50k"
    SALARY_50K_1LAC = "50k-1lac"
    SALARY_1LAC_1_5LAC = "1lac-1.5lac"
    SALARY_1_5LAC_2LAC = "1.5lac-2lac"
    SALARY_2= "SALARY_2+"
    SALARY_3= "SALARY_3+"
    SALARY_4= "SALARY_4+"
    SALARY_5= "SALARY_5+"
    
class LeadStage(str, enum.Enum):
    FRESH_LEAD = "Fresh_Lead"
    TOUCHED = "Touched"
    CALLED = "Called"
    IN_PROGRESS = "In_Progress"
    PROJECTION_REPORT = "Projection_Report"
    DOCUMENTS = "Documents"
    MANDATE = "Mandate"
    ORDER_PLACED = "Order_Placed"
    CONVERTED = "Converted"
    POST_PLAN_SENT = "Post_Plan_Sent"
    REFERENCE = "Reference"
    LOST_CLIENT = "Lost_Client"

class AssignmentStatus(str, enum.Enum):
    ACTIVE = "Active"
    REASSIGNED = "Reassigned"

class NotificationType(str, enum.Enum):
    NEW_LEAD = "new_lead"
    REMINDER = "reminder"
    CONVERSION = "conversion"
    LOST_LEAD = "lost_lead"
     
# =========================
# LMS DATABASE MODELS
# =========================

class Lead(LMSBase):
    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))

    # Contact info
    name = Column(String(255), nullable=False)                              
    mobile_number = Column(String(20), index=True)
    pancard_number = Column(String(20), index=True)
    email = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    pincode = Column(String(6), nullable=True)

    # Professional info
    profile = Column(SAEnum(ClientProfile, native_enum=False))
    designation = Column(String(100), nullable=True)
    is_hni = Column(Boolean, default=False)

    current_stage = Column(
        SAEnum(LeadStage, native_enum=False),
        default=LeadStage.FRESH_LEAD,
        nullable=False
    )

    # Assignment — UUID references CMS users
    assigned_agent_id = Column(String(36), index=True, nullable=True)
    assigned_name = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Track when stage last changed (for 30-day lost timer + reminder)
    last_stage_changed_at = Column(DateTime(timezone=True), nullable=True)


