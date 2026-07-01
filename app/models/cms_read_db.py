
from sqlalchemy import null
import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, DateTime, Date, ForeignKey,
    Float, Text, Boolean, JSON, Index, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.database import Base


# ==========================
# HELPERS
# ==========================

def generate_uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


# ==========================
# ENUMS
# ==========================

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    SUPERADMIN = "superadmin"
    EDITOR = "editor"


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
    ENGINEER = "engineer"
    DOCTOR = "doctor"
    ADVOCATE = "advocate"
    CA = "chartered_accountant"
    ARCHITECT = "architect"
    TEACHER = "teacher"
    CONSULTANT = "consultant"
    IT_PROFESSIONAL = "it_professional"
    DEFENCE = "defence"
    BANKER = "banker"
    SELF_EMPLOYED = "self_employed"
    MINOR = "minor"
    OTHER = "other"


# ==========================
# USERS
# ==========================

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)

    role = Column(SAEnum(UserRole, native_enum=False), default=UserRole.USER)
    is_active = Column(Boolean, default=True)

    # FCM push token — updated by the mobile app
    fcm_token = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)
    last_login = Column(DateTime(timezone=True))

    # relationships
    clients = relationship(
        "Client",
        back_populates="owner",
        foreign_keys="Client.owner_id"
    )


# ==========================
# CLIENT
# ==========================

class Client(Base):
    __tablename__ = "clients"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    full_name = Column(String(100), nullable=False, index=True)
    client_code = Column(String(20), nullable=True, index=True)
    pancard_number = Column(String(20), unique=True, nullable=True)
    mobile_number = Column(String(20), index=True)

    # Contact / nurturing fields
    email = Column(String(255), nullable=True, index=True)
    date_of_birth = Column(Date, nullable=True)

    profile = Column(SAEnum(ClientProfile, native_enum=False))
    designation = Column(String(100), nullable=True)
    is_hni = Column(Boolean, default=False)

    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)

    # ownership
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    agent_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))

    owner = relationship("User", foreign_keys=[owner_id], back_populates="clients")
    agent = relationship("User", foreign_keys=[agent_id])

    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    @property
    def owner_username(self):
        return self.owner.username if self.owner else None

    @property
    def agent_username(self):
        return self.agent.username if self.agent else None
