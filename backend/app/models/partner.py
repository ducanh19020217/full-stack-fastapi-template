import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from app.models import User
from enum import Enum


class PartnerStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"  # (tuỳ bạn muốn mở rộng thêm trạng thái gì)


class Partner(SQLModel, table=True):
    __tablename__ = "partner"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    name: str = Field(min_length=3, max_length=255, unique=True)
    description: Optional[str] = Field(default=None, max_length=255)

    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    contact_address: Optional[str] = Field(default=None, max_length=255)

    contact_personal_name: Optional[str] = Field(default=None, max_length=255)
    contact_personal_phone: Optional[str] = Field(default=None, max_length=50)
    contact_personal_email: Optional[str] = Field(default=None, max_length=255)

    status: PartnerStatus = Field(default=PartnerStatus.active)

    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PartnerCreate(SQLModel):
    name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    contact_personal_name: Optional[str] = None
    contact_personal_phone: Optional[str] = None
    contact_personal_email: Optional[str] = None
    status: PartnerStatus = PartnerStatus.active

class PartnerUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    contact_personal_name: Optional[str] = None
    contact_personal_phone: Optional[str] = None
    contact_personal_email: Optional[str] = None
    status: Optional[PartnerStatus] = None

class PartnerResponse(SQLModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    contact_personal_name: Optional[str] = None
    contact_personal_phone: Optional[str] = None
    contact_personal_email: Optional[str] = None
    status: PartnerStatus
    created_by: uuid.UUID
    created_at: datetime

class PartnerFilter(SQLModel):
    name: Optional[str] = None
    status: Optional[PartnerStatus] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class PartnersResponse(SQLModel):
    data: list[PartnerResponse]
    total: int

