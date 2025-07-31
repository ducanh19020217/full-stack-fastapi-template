import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import UniqueConstraint, Column, ForeignKey


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)

class ThemeMode(str, Enum):
    default = "default"
    light = "light"
    dark = "dark"

class Lang(str, Enum):
    en = "en"
    vi = "vi"

class UserUpdateThemes(SQLModel):
    themes_mode: Optional[ThemeMode] = Field(default=None)
    lang: Optional[Lang] = Field(default=None)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase,UserUpdateThemes, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    units: list["UnitUser"] = Relationship(
        back_populates="user",
        # Explicitly define foreign_keys using Column objects
        sa_relationship_kwargs={
            "foreign_keys": "UnitUser.user_id",
            "primaryjoin": "User.id == UnitUser.user_id"  # Add primaryjoin
        }
    )
    created_units: list["Unit"] = Relationship(
        back_populates="creator",
        # Explicitly define foreign_keys using Column objects
        sa_relationship_kwargs={
            "foreign_keys": "Unit.created_by",
            # This refers to the column on the *remote* side for the User's perspective
            "primaryjoin": "User.id == Unit.created_by"  # Add primaryjoin
        }
    )
    updated_unit_users: list["UnitUser"] = Relationship(
        back_populates="updater",
        # Explicitly define foreign_keys using Column objects
        sa_relationship_kwargs={
            "foreign_keys": "UnitUser.updated_by",
            "primaryjoin": "User.id == UnitUser.updated_by"  # Add primaryjoin
        }
    )
    audit_logs: list["AuditLog"] = Relationship(back_populates="creator")


# Properties to return via API, id is always required
class UserPublic(UserBase, UserUpdateThemes):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


#### Xử lý models cho chức năng quản lý đơn vị
class Unit(SQLModel, table=True):
    __tablename__ = "unit"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(min_length=3, max_length=255, unique=True)
    description: Optional[str] = Field(default=None, max_length=255)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False) # Added foreign key for creator

    members: list["UnitUser"] = Relationship(back_populates="unit")
    creator: Optional["User"] = Relationship(
        back_populates="created_units",
        # Explicitly define the join condition
        sa_relationship_kwargs={
            "foreign_keys": "Unit.created_by",  # This is the foreign key *on this (Unit) model*
            "primaryjoin": "Unit.created_by == User.id"  # Explicitly define the join
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
            "foreign_keys": "UnitUser.user_id",  # Foreign key on UnitUser
            "primaryjoin": "UnitUser.user_id == User.id"  # Explicit join condition
        }
    )
    updater: Optional["User"] = Relationship(
        back_populates="updated_unit_users",
        sa_relationship_kwargs={
            "foreign_keys": "UnitUser.updated_by",  # Foreign key on UnitUser
            "primaryjoin": "UnitUser.updated_by == User.id"  # Explicit join condition
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

    leader: Optional[User] = None  # leader là 1 user
    member_count: int = 0              # tổng số thành viên

class UnitUpdate(SQLModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    user_ids: Optional[list[uuid.UUID]] = None  # danh sách thành viên (cập nhật lại toàn bộ)
    leader_id: Optional[uuid.UUID] = None  # user_id của leader

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

# Bảng lưu audit log

class LogResult(str, Enum):
    success = "success"
    failed = "failed"

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"
    __table_args__ = (

    )
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


