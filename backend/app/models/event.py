from sqlmodel import SQLModel, Field
import uuid
from typing import Optional
from datetime import datetime
from enum import Enum


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
