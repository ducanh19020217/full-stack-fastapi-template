import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, JSON

from sqlmodel import Field, Relationship
from app.models import SQLModel


class EventSchedule(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    event_id: uuid.UUID = Field(foreign_key="partner_event.id", nullable=False)

    time: datetime
    location: Optional[str] = None
    detail: Optional[str] = None
    attachment: Optional[Dict[str, str]] = Field(
        default=None,
        sa_column=Column(JSON)
    )

    status: str = Field(default="active")

    # Relationship
    event: Optional["PartnerEvent"] = Relationship(back_populates="schedules")
