import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from app.models import User

class Unit(SQLModel, table=True):
    __tablename__ = "unit"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(min_length=3, max_length=255, unique=True)
    description: Optional[str] = Field(default=None, max_length=255)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    members: list["UnitUser"] = Relationship(back_populates="unit")
    creator: Optional["User"] = Relationship(
        back_populates="created_units",
        sa_relationship_kwargs={
            "foreign_keys": "Unit.created_by",
            "primaryjoin": "Unit.created_by == User.id"
        }
    )

class UnitUser(SQLModel, table=True):
    __tablename__ = "unit_user"
    __table_args__ = (UniqueConstraint("unit_id", "user_id", name="uq_unit_user"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    unit_id: uuid.UUID = Field(foreign_key="unit.id", nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    is_leader: bool = Field(default=False)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    unit: Optional["Unit"] = Relationship(back_populates="members")
    user: Optional["User"] = Relationship(
        back_populates="units",
        sa_relationship_kwargs={
            "foreign_keys": "UnitUser.user_id",
            "primaryjoin": "UnitUser.user_id == User.id"
        }
    )
    updater: Optional["User"] = Relationship(
        back_populates="updated_unit_users",
        sa_relationship_kwargs={
            "foreign_keys": "UnitUser.updated_by",
            "primaryjoin": "UnitUser.updated_by == User.id"
        }
    )

class UnitCreate(SQLModel):
    name: str
    description: Optional[str] = None
    leader_id: uuid.UUID
    member_ids: list[uuid.UUID] = []

class UnitRead(SQLModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime
    leader: Optional["User"] = None
    member_count: int = 0

class UnitUpdate(SQLModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    user_ids: Optional[list[uuid.UUID]] = None
    leader_id: Optional[uuid.UUID] = None

class UnitUserCreate(SQLModel):
    unit_id: uuid.UUID
    user_id: uuid.UUID
    is_leader: Optional[bool] = False

class UnitFilterRequest(SQLModel):
    name: Optional[str] = None
    created_by: Optional[list[uuid.UUID]] = None
    leader_id: Optional[list[uuid.UUID]] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 20