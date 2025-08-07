import enum
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm.session import Session
from sqlmodel import Field
from sqlalchemy import Column, Enum as SAEnum, String, Text, DateTime, func
from app.models import SQLModel

from app.models import Event, Partner, PartnerEvent


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

    target_id: uuid.UUID = Field(default_factory=uuid.uuid4, )

    title: str = Field(max_length=255, nullable=False)
    content: str = Field(nullable=False)

    status: str = Field(default="active", max_length=50)

    created_by: str = Field(max_length=100, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    approved_by: Optional[str] = Field(default=None, max_length=100)
    approved_at: Optional[datetime] = Field(default=None)

    def get_target(self, session: Session):
        model_map = {
            RecommendationTargetType.EVENT: Event,
            RecommendationTargetType.PARTNER: Partner,
            RecommendationTargetType.PARTNER_EVENT: PartnerEvent,
        }
        model_cls = model_map.get(self.target_type)
        if model_cls:
            return session.get(model_cls, self.target_id)
        return None

class RecommendationCreate(SQLModel):
    target_type: RecommendationTargetType
    target_id: uuid.UUID
    title: str
    content: str
    status: str = "active"

class RecommendationUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class RecommendationResponse(SQLModel):
    id: uuid.UUID
    target_type: RecommendationTargetType
    target_id: uuid.UUID
    title: str
    content: str
    status: str
    created_by: str
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class RecommendationsResponse(SQLModel):
    data: List[RecommendationResponse]
    total: int
