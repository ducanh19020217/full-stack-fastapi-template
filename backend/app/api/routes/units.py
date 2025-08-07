import uuid
from typing import Any
import i18n

from fastapi import HTTPException, APIRouter
from sqlalchemy.exc import IntegrityError
from psycopg import errors as pg_errors

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app.i18n.utils import translate

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    UserUpdateThemes,
    UnitCreate,
    UnitUser,
    UnitRead,
    UnitFilterRequest,
    Unit,
    LogResult,
    AuditLogCreate,
    UnitUpdate
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/units", tags=["units"])
i18n.set("locale", "vi")  # Thiết lập ngôn ngữ mặc định
i18n.set("fallback", "en")


@router.get("/test-translation")
async def test_translation():
    return {
        "vi": i18n.t("unit.created"),
        "en": i18n.t("unit.created")
    }


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def create_unit(session: SessionDep, unit_in: UnitCreate, current_user: CurrentUser) -> Any:
    """
    Create new unit and assign leader/member to unit_user.
    """
    try:
        # Check leader_id tồn tại
        if unit_in.leader_id:
            leader = session.get(User, unit_in.leader_id)
            if not leader:
                raise ValueError(f"User với id {unit_in.leader_id} (leader_id) không tồn tại.")

        # Check các member_ids tồn tại
        if unit_in.member_ids:
            existing_users = session.exec(
                select(User.id).where(User.id.in_(unit_in.member_ids))
            ).all()

            missing_ids = set(unit_in.member_ids) - set(existing_users)
            if missing_ids:
                raise ValueError(f"Các user_id sau không tồn tại: {', '.join(str(i) for i in missing_ids)}")

        # 1. Tạo unit
        unit = crud.create_unit(
            session=session,
            unit_create=unit_in,
            creator=current_user.id
        )

        # 2. Tạo UnitUser cho leader
        unit_user_leader = UnitUser(
            unit_id=unit.id,
            user_id=unit_in.leader_id,
            is_leader=True,
            updated_by=current_user.id,
        )
        session.add(unit_user_leader)

        # 3. Tạo UnitUser cho các member khác
        for member_id in unit_in.member_ids:
            if member_id != unit_in.leader_id:
                unit_user = UnitUser(
                    unit_id=unit.id,
                    user_id=member_id,
                    is_leader=False,
                    updated_by=current_user.id,
                )
                session.add(unit_user)

        # Nếu đến đây là thành công
        log_create = AuditLogCreate(
            created_by=current_user.id,
            status=LogResult.success,
            content='Tạo unit',
        )
        crud.create_log(session=session, log_create=log_create)

        session.commit()
        return {"message": translate("unit.created")}

    except Exception as e:
        session.rollback()

        # Ghi log thất bại kèm lý do
        log_create = AuditLogCreate(
            created_by=current_user.id,
            status=LogResult.failed,
            content=f"Tạo unit thất bại: {str(e)}"
        )
        crud.create_log(session=session, log_create=log_create)

        # Có thể raise lại lỗi phù hợp với FastAPI
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/filter", response_model=list[UnitRead])
def post_filter_units(
        filters: UnitFilterRequest,
        session: SessionDep,
        current_user: CurrentUser
):
    """
    Filter units by criteria like name, creator, or leader.
    """
    units = crud.filter_units(session=session, filters=filters)
    return units

@router.delete("/delete", response_model=Message)
def delete_unit(
    unit_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
):
    try:
        # 1. Kiểm tra Unit tồn tại
        unit = session.get(Unit, unit_id)
        if not unit:
            log_create = AuditLogCreate(
                created_by=current_user.id,
                status=LogResult.failed,
                content=f"Xóa Unit {unit_id} thất bại do không tồn tại {unit_id} ",
            )
            crud.create_log(session=session, log_create=log_create)
            raise HTTPException(status_code=404, detail="Unit không tồn tại")

        # 2. Xóa các bản ghi liên quan trong bảng UnitUser
        stmt = delete(UnitUser).where(UnitUser.unit_id == unit_id)
        session.exec(stmt)

        # 3. Xóa Unit
        session.delete(unit)
        session.commit()

        # Nếu đến đây là thành công
        log_create = AuditLogCreate(
            created_by=current_user.id,
            status=LogResult.success,
            content=f"Xóa Unit {unit_id} thành công",
        )
        crud.create_log(session=session, log_create=log_create)

        return {"message": f"Unit {unit_id} đã được xóa thành công"}

    except IntegrityError as e:
        session.rollback()
        content = ""
        # Nếu đến đây là thành công
        if isinstance(e.orig, pg_errors.ForeignKeyViolation):
            content = "Xóa Unit thất bại vì đang được tham chiếu ở nơi khác."
            raise HTTPException(
                status_code=400,
                detail="Xóa Unit thất bại vì đang được tham chiếu ở nơi khác."
            )
        log_create = AuditLogCreate(
            created_by=current_user.id,
            status=LogResult.failed,
            content=f"Xóa Unit {unit_id} thất bại do Lỗi cơ sở dữ liệu.",
        )
        crud.create_log(session=session, log_create=log_create)
        raise HTTPException(status_code=500, detail="Lỗi cơ sở dữ liệu.")

    except Exception as e:
        # Nếu đến đây là thành công
        log_create = AuditLogCreate(
            created_by=current_user.id,
            status=LogResult.failed,
            content=f"Xóa Unit {unit_id} không thành công",
        )
        crud.create_log(session=session, log_create=log_create)
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update", response_model=Message)
def update_unit(
    unit_id: uuid.UUID,
    body: UnitUpdate,
    session: SessionDep,
    current_user: CurrentUser
):
    # 1. Lấy unit
    unit = session.get(Unit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit không tồn tại")

    # 2. Cập nhật thông tin cơ bản
    if body.name is not None:
        unit.name = body.name
    if body.description is not None:
        unit.description = body.description
    session.add(unit)

    # 3. Cập nhật thành viên nếu có
    if body.user_ids is not None:
        # Xóa tất cả thành viên cũ
        stmt = delete(UnitUser).where(UnitUser.unit_id == unit_id)
        session.exec(stmt)

        # Thêm mới danh sách user
        for user_id in body.user_ids:
            is_leader = body.leader_id == user_id
            session.add(UnitUser(
                unit_id=unit_id,
                user_id=user_id,
                is_leader=is_leader,
                updated_by=current_user.id
            ))

    # 4. Nếu chỉ đổi leader
    elif body.leader_id is not None:
        # Đảm bảo leader phải là thành viên
        member_stmt = select(UnitUser).where(UnitUser.unit_id == unit_id)
        members = session.exec(member_stmt).all()
        member_ids = [m.user_id for m in members]
        if body.leader_id not in member_ids:
            raise HTTPException(status_code=400, detail="Leader phải là thành viên của Unit")

        # Reset tất cả leader
        for member in members:
            member.is_leader = member.user_id == body.leader_id
            member.updated_by = current_user.id
            session.add(member)

    session.commit()
    return {"message": "Cập nhật Unit thành công"}
