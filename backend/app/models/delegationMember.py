from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship
from uuid import UUID, uuid4
from typing import Optional
from app.models import SQLModel

class DelegationMember(SQLModel, table=True):
    __tablename__ = "delegation_member"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    event_id: UUID = Field(foreign_key="partner_event.id", nullable=False)

    full_name: str
    position: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    is_representative: bool = Field(default=False)

    status: str = Field(default="active")

    # Relationship
    event: Optional["PartnerEvent"] = Relationship(back_populates="delegation_members")