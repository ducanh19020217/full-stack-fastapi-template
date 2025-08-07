import uuid
from typing import List, Optional, Dict
from datetime import datetime
from sqlmodel import Field, Relationship
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import relationship
from app.models import SQLModel


class PartnerEvent(SQLModel, table=True):
    __tablename__ = "partner_event"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    partner_id: uuid.UUID = Field(foreign_key="partner.id", nullable=False)
    event_id: uuid.UUID = Field(foreign_key="event.id", nullable=False)

    name: str = Field(sa_column=Column(String, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    start_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    end_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    location: Optional[str] = Field(default=None, sa_column=Column(String))
    status: str = Field(default="active", sa_column=Column(String))

    # Relationships
    partner: Optional["Partner"] = Relationship(
        back_populates="partner_events",
        sa_relationship_kwargs={"lazy": "joined"}
    )
    event: Optional["Event"] = Relationship(
        back_populates="partner_events",
        sa_relationship_kwargs={"lazy": "joined"}
    )
    delegation_members: List["DelegationMember"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    schedules: List["EventSchedule"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class PartnerEventCreate(SQLModel):
    name: str
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    status: str = "active"
    partner_id: uuid.UUID
    event_id: uuid.UUID

class PartnerEventUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    status: Optional[str] = None
    partner_id: uuid.UUID
    event_id: uuid.UUID

class EventScheduleBase(SQLModel):
    time: datetime
    location: Optional[str] = None
    detail: Optional[str] = None
    attachment: Optional[Dict[str, str]] = None
    status: str = "active"

class EventScheduleCreate(EventScheduleBase):
    pass

class EventScheduleUpdate(SQLModel):
    time: Optional[datetime] = None
    location: Optional[str] = None
    detail: Optional[str] = None
    attachment: Optional[Dict[str, str]] = None
    status: Optional[str] = None

class EventScheduleResponse(EventScheduleBase):
    id: uuid.UUID
    event_id: uuid.UUID

class PartnerEventResponse(PartnerEventCreate):
    id: uuid.UUID
    schedules: List[EventScheduleResponse] = []

class PartnerEventsResponse(SQLModel):
    data: List[PartnerEventResponse]
    total: int

