
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


class StockBrokers(str, enum.Enum):
    ANGEL_ONE = "angel one"
    DHAN = "dhan"
    # ANAND_RATHI = "anand rathi"
    LEMON = "lemon"


class MutualFundAMCs(str, enum.Enum):
    PRUDENT = "prudent"
    ANGEL_ONE = "angel one"
    ANAND_RATHI = "anand rathi"
    NJ = "nj"
    LEMON = "lemon"
    DHAN = "dhan"


class InsuranceType(str, enum.Enum):
    TERM = "term"
    MEDICLAIM = "mediclaim"
    VEHICLE = "vehicle"

class WhereInsurance(str, enum.Enum):
    WITH_US = "with us"
    WITH_OTHER = "with other"
    NO = "no"

class SipCategory(str, enum.Enum):
    BELOW_5000 = "below 5000"
    SIP_5000_10000 = "5000-10000"
    SIP_10000_25000 = "10000-25000"
    SIP_25K_50K = "25k-50k"
    SIP_50K_1LAC = "50k-1lac"
    ABOVE_1LAC = "1 lac above"


class lumpsumCategory(str, enum.Enum):
    BELOW_1LAC = "below 1 lac"
    LUMPSUM_1_10LAC = "1-10lac"
    LUMPSUM_20_25LAC = "20-25 lac"
    LUMPSUM_25_50LACS = "25-50 lacs"
    LUMPSUM_50_1CR = "50-1cr"
    ABOVE_1CR = "1 cr above"

class AumCategory(str, enum.Enum):
    BELOW_1LAC = "below 1 lac"
    AUM_1_10LAC = "1-10lac"
    AUM_20_25LAC = "20-25 lac"
    AUM_25_50LACS = "25-50 lacs"
    AUM_50_1CR = "50-1cr"
    ABOVE_1CR = "1 cr above"

class StepUpMode(str, enum.Enum):
    PERCENTAGE = "percentage"
    AMOUNT = "amount"


class StepUpFrequency(str, enum.Enum):
    ANNUAL = "annual"
    SEMI_ANNUAL = "semi-annual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"


class ContactNoteMedium(str, enum.Enum):
    PHONE = "phone"
    WHATSAPP = "whatsapp"
    PORTFOLIO_REVIEW = "portfolio review"
    NOTE = "note"


class RiskAppetite(str, enum.Enum):
    AGGRESSIVE = "aggressive"
    MODERATE = "moderate"
    DEFENSIVE = "defensive"


class MutualFundCategory(str, enum.Enum):
    SWP = "swp"
    STP = "stp"

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

class Religion(str, enum.Enum):
    HINDU = "hindu"
    MUSLIM = "muslim"
    CHRISTIAN = "christian"
    SIKH = "sikh"
    BUDDHIST = "buddhist"
    JAIN = "jain"
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

    profile = Column(SAEnum(ClientProfile, native_enum=False))
    email = Column(String(255), nullable=True, index=True)
    date_of_birth = Column(Date, nullable=True)
    religion = Column(SAEnum(Religion, native_enum=False), nullable=True)
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

    # financial / profile
    is_portfolio_reviewed = Column(Boolean, default=False)
    portfolio_review_date = Column(DateTime(timezone=True), nullable=True)
    
    salary_category = Column(SAEnum(SalaryCategory, native_enum=False))

    is_mediclaim = Column(SAEnum(WhereInsurance, native_enum=False))
    ext_mediclaim = Column(String(100))
    mediclaim_renewal_date = Column(String(50))

    is_insurance = Column(SAEnum(WhereInsurance, native_enum=False))
    ext_insurance = Column(String(100))
    insurance_renewal_date = Column(String(50))

    is_vehicle_insurance = Column(SAEnum(WhereInsurance, native_enum=False))
    vehicle_insurance_renewal_date = Column(String(50))
    ext_vehicle_insurance = Column(String(100))

    stock_brokers = Column(JSON(none_as_null=True), nullable=True)
    mutual_fund = Column(JSON(none_as_null=True), nullable=True)

    mf_category = Column(SAEnum(MutualFundCategory, native_enum=False))
    aum_category = Column(SAEnum(AumCategory, native_enum=False))
    risk_appetite = Column(SAEnum(RiskAppetite, native_enum=False))
    sip = Column(Float, default=0)
    sip_category = Column(SAEnum(SipCategory, native_enum=False))
    sip_change_date = Column(String(50))
    active_sip = Column(Boolean, default=False)
    # is_redemption = Column(Boolean, nullable=True)
    redemption_amount = Column(Float, default=0)

    is_step_up_sip = Column(Boolean, default=False)
    step_up_mode = Column(SAEnum(StepUpMode, native_enum=False))
    step_up_value = Column(Float, default=0)
    step_up_frequency = Column(SAEnum(StepUpFrequency, native_enum=False))

    lumpsum = Column(Float, default=0)
    lumpsum_category = Column(SAEnum(lumpsumCategory, native_enum=False))

    stocks = Column(Float, default=0)
    aum = Column(Float, default=0)
    percentage_returns = Column(Float, default=0)

    # reference = Column(String(36), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    # reference_name = Column(String(100), nullable=True)  # cached name — auto-set by CRUD

    # family_id = Column(String(36), ForeignKey("families.id"))=
    last_contacted_date = Column(String(50))
    next_contact_date = Column(String(50))

    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    # relationships
    # notes = relationship("Note", back_populates="client")

    # agent_histories = relationship(
    #     "AgentHistory",
    #     back_populates="client",
    #     order_by="AgentHistory.created_at",
    #     cascade="all, delete-orphan"
    # )

    # family = relationship("Family", back_populates="clients")

    # One client can have MULTIPLE references
    # references = relationship(
    #     "Reference",
    #     foreign_keys="Reference.client_id",
    #     back_populates="client",
    #     cascade="all, delete-orphan",
    # )

    # History relationships
    sip_histories = relationship(
        "SipHistory",
        back_populates="client",
        cascade="all, delete-orphan",
        order_by="SipHistory.created_at",
    )
    # aum_histories = relationship(
    #     "AumHistory",
    #     back_populates="client",
    #     cascade="all, delete-orphan",
    #     order_by="AumHistory.created_at",
    # )
    # redemption_histories = relationship(
    #     "RedemptionHistory",
    #     back_populates="client",
    #     cascade="all, delete-orphan",
    #     order_by="RedemptionHistory.created_at",
    # )
    # lumpsum_histories = relationship(
    #     "LumpsumHistory",
    #     back_populates="client",
    #     cascade="all, delete-orphan",
    #     order_by="LumpsumHistory.created_at",
    # )

    # session_clients = relationship(
    #     "SessionClient",
    #     back_populates="client",
    #     cascade="all, delete-orphan"
    # )

    # ── Convenience properties: most recent history value ─────────────────
    @property
    def latest_sip(self) -> float:
        """Most recent SIP value from history, falls back to client.sip."""
        if self.sip_histories:
            return sorted(self.sip_histories, key=lambda h: h.created_at, reverse=True)[0].sip
        return self.sip or 0.0

    @property
    def latest_aum(self) -> float:
        """Most recent AUM value from history, falls back to client.aum."""
        if self.aum_histories:
            return sorted(self.aum_histories, key=lambda h: h.created_at, reverse=True)[0].aum
        return self.aum or 0.0

    @property
    def latest_redemption_amount(self) -> float:
        """Most recent redemption amount from history, falls back to client.redemption_amount."""
        if self.redemption_histories:
            return sorted(self.redemption_histories, key=lambda h: h.created_at, reverse=True)[0].redemption_amount
        return self.redemption_amount or 0.0

    @property
    def latest_lumpsum(self) -> float:
        """Most recent lumpsum value from history, falls back to client.lumpsum."""
        if self.lumpsum_histories:
            return sorted(self.lumpsum_histories, key=lambda h: h.created_at, reverse=True)[0].lumpsum
        return self.lumpsum or 0.0
    # ──────────────────────────────────────────────────────────────────────

    @property
    def owner_username(self):
        return self.owner.username if self.owner else None

    @property
    def agent_username(self):
        return self.agent.username if self.agent else None


# ===================================================
# HISTORY MANAGEMENT
# ===================================================    

#--------------------------
# SIP HISTORY MANAGEMENT
#--------------------------

class SipHistory(Base):
    __tablename__ = "sip_histories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="CASCADE"))
    sip = Column(Float, default=0)
    sip_start_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    client = relationship("Client", back_populates="sip_histories")        
