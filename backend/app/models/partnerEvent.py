from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import relationship


class PartnerEvent(SQLModel, table=True):
    __tablename__ = "partner_event"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    name: str = Field(sa_column=Column(String, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    start_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    end_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    location: Optional[str] = Field(default=None, sa_column=Column(String))
    status: str = Field(default="active", sa_column=Column(String))

    # Relationships
    delegation_members: List["DelegationMember"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    schedules: List["EventSchedule"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
