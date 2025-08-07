import uuid
from typing import Any

from sqlmodel import Session, select, func
from sqlalchemy.orm import joinedload

from app.core.security import get_password_hash, verify_password
from app.models.user import UserBase, User, UserCreate, UserUpdate
from app.models.unit import UnitRead, UnitUser, UnitCreate, Unit, UnitFilterRequest
from app.models.item import Item, ItemCreate
from app.models.audit import AuditLogCreate, AuditLog

from app.utils import strip_accents

def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def create_unit(*, session: Session, unit_create: UnitCreate, creator: uuid.UUID) -> Item:
    db_unit = Unit.model_validate(unit_create, update={"created_by": creator})
    session.add(db_unit)
    session.commit()
    session.refresh(db_unit)
    return db_unit

def filter_units(session: Session, filters: UnitFilterRequest):
    stmt = select(Unit).options(joinedload(Unit.members))

    # Tìm kiếm theo tên không phân biệt chữ hoa + dấu
    if filters.name:
        keyword = strip_accents(filters.name).lower()
        stmt = stmt.where(
            func.unaccent(func.lower(Unit.name)).ilike(f"%{keyword}%")
        )

    # Lọc theo danh sách created_by (nếu có)
    if filters.created_by:
        stmt = stmt.where(Unit.created_by.in_(filters.created_by))

    # Lọc theo leader (trong bảng phụ UnitUser, phải join)
    if filters.leader_id:
        stmt = stmt.join(Unit.members).where(
            UnitUser.user_id.in_(filters.leader_id),
            UnitUser.is_leader == True
        )

    # Phân trang
    page = max(filters.page or 1, 1)
    page_size = min(filters.page_size or 20, 100)
    offset = (page - 1) * page_size

    stmt = stmt.offset(offset).limit(page_size)
    results = session.exec(stmt).unique().all()

    enriched_units = []

    for unit in results:
        unit_read = UnitRead.from_orm(unit)

        # Đếm số member
        unit_read.member_count = len(unit.members)

        # Tìm leader
        leader_link = next((m for m in unit.members if m.is_leader), None)
        if leader_link and leader_link.user:
            unit_read.leader = UserBase.from_orm(leader_link.user)

        enriched_units.append(unit_read)
    return enriched_units

def create_log(*, session: Session, log_create: AuditLogCreate) -> Item:
    db_log = AuditLog.model_validate(log_create)
    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log