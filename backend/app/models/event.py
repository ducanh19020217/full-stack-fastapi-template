import uuid
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlmodel import Field, Relationship
from app.models import SQLModel


class EventStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class ExchangeLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    top = "top"


class Event(SQLModel, table=True):
    __tablename__ = "event"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    start_time: datetime = Field(nullable=False, description="Thời gian diễn ra sự kiện")
    location: str = Field(max_length=255, nullable=False, description="Địa điểm tổ chức")
    exchange_level: ExchangeLevel = Field(default=ExchangeLevel.medium, description="Cấp trao đổi")

    related_documents: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Link/tên file hoặc đường dẫn tài liệu liên quan"
    )

    additional_info: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Thông tin thêm (nếu có)"
    )

    status: EventStatus = Field(default=EventStatus.scheduled)

    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    partner_events: List["PartnerEvent"] = Relationship(back_populates="event")


class EventCreate(SQLModel):
    start_time: datetime
    location: str
    exchange_level: ExchangeLevel = ExchangeLevel.medium
    related_documents: Optional[str] = None
    additional_info: Optional[str] = None
    status: EventStatus = EventStatus.scheduled

class EventUpdate(SQLModel):
    start_time: Optional[datetime] = None
    location: Optional[str] = None
    exchange_level: Optional[ExchangeLevel] = None
    related_documents: Optional[str] = None
    additional_info: Optional[str] = None
    status: Optional[EventStatus] = None

class EventResponse(EventCreate):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime

class EventsResponse(SQLModel):
    data: List[EventResponse]
    total: int

