import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Enum as SAEnum, String, Text, DateTime, func


# Enum để xác định loại đề xuất áp dụng cho đối tượng nào
class RecommendationTargetType(enum.Enum):
    EVENT = "event"
    PARTNER = "partner"
    PARTNER_EVENT = "partner_event"


class Recommendation(SQLModel, table=True):
    __tablename__ = "recommendations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    target_type: RecommendationTargetType = Field(
        sa_column=Column(SAEnum(RecommendationTargetType), nullable=False)
    )

    target_id: int = Field(nullable=False)

    title: str = Field(max_length=255, nullable=False)
    content: str = Field(nullable=False)

    status: str = Field(default="active", max_length=50)

    created_by: str = Field(max_length=100, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    approved_by: Optional[str] = Field(default=None, max_length=100)
    approved_at: Optional[datetime] = Field(default=None)

    def get_target(self, session):
        if self.target_type == RecommendationTargetType.EVENT:
            return session.get(Event, self.target_id)
        elif self.target_type == RecommendationTargetType.PARTNER:
            return session.get(Partner, self.target_id)
        elif self.target_type == RecommendationTargetType.PARTNER_EVENT:
            return session.get(PartnerEvent, self.target_id)
        return None
