### models/audit.py
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

class LogResult(str, Enum):
    success = "success"
    failed = "failed"

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    content: str
    status: Optional[LogResult] = Field(default=None)

    creator: Optional["User"] = Relationship(back_populates="audit_logs")

class AuditLogCreate(SQLModel):
    content: str
    status: Optional[LogResult]
    created_by: uuid.UUID