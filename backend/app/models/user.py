import uuid
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

class ThemeMode(str, Enum):
    default = "default"
    light = "light"
    dark = "dark"

class Lang(str, Enum):
    en = "en"
    vi = "vi"

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)

class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)

class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)

class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)

class UserUpdateThemes(SQLModel):
    themes_mode: Optional[ThemeMode] = Field(default=None)
    lang: Optional[Lang] = Field(default=None)

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

class User(UserBase, UserUpdateThemes, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    units: list["UnitUser"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "foreign_keys": "UnitUser.user_id",
            "primaryjoin": "User.id == UnitUser.user_id"
        }
    )
    created_units: list["Unit"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={
            "foreign_keys": "Unit.created_by",
            "primaryjoin": "User.id == Unit.created_by"
        }
    )
    updated_unit_users: list["UnitUser"] = Relationship(
        back_populates="updater",
        sa_relationship_kwargs={
            "foreign_keys": "UnitUser.updated_by",
            "primaryjoin": "User.id == UnitUser.updated_by"
        }
    )
    audit_logs: list["AuditLog"] = Relationship(back_populates="creator")

class UserPublic(UserBase, UserUpdateThemes):
    id: uuid.UUID

class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int