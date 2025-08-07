import uuid
from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentUser, SessionDep
from sqlalchemy import select, or_, func
from app.i18n.utils import translate
import i18n
from app.models import Partner, PartnerCreate, PartnerUpdate, PartnerResponse, PartnerFilter,PartnersResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.query import Query

from app.models.partner import PartnerStatus

i18n.set("locale", "vi")  # Thiết lập ngôn ngữ mặc định
i18n.set("fallback", "en")

router = APIRouter(prefix="/partners", tags=["partners"])


@router.post("/", response_model=PartnerResponse)
def create_partner(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        partner_in: PartnerCreate
) -> Any:
    """Create new partner"""
    db_partner = Partner(
        **partner_in.model_dump(),
        created_by=current_user.id
    )
    try:
        session.add(db_partner)
        session.commit()
        session.refresh(db_partner)
        return db_partner
    except Exception as e:
        session.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Partner with this name already exists"
            )
        raise e


@router.get("/{partner_id}", response_model=PartnerResponse)
def get_partner(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        partner_id: uuid.UUID
) -> Any:
    """Get partner by ID"""
    partner = session.get(Partner, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner


@router.put("/{partner_id}", response_model=PartnerResponse)
def update_partner(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        partner_id: uuid.UUID,
        partner_in: PartnerUpdate
) -> Any:
    """Update partner"""
    partner = session.get(Partner, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    update_data = partner_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(partner, field, value)

    try:
        session.add(partner)
        session.commit()
        session.refresh(partner)
        return partner
    except Exception as e:
        session.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Partner with this name already exists"
            )
        raise e


@router.delete("/{partner_id}")
def delete_partner(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        partner_id: uuid.UUID
) -> Any:
    """Delete partner"""
    partner = session.get(Partner, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    session.delete(partner)
    session.commit()
    return {"message": "Partner deleted successfully"}


@router.get("/", response_model=PartnersResponse)
def get_partners(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    status: Optional[PartnerStatus] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None
) -> Any:
    """Get all partners with filtering"""
    # Apply filters if provided
    filters = []
    if name:
        filters.append(Partner.name.ilike(f"%{name}%"))
    if status:
        filters.append(Partner.status == status)
    if email:
        filters.append(or_(
            Partner.contact_email.ilike(f"%{email}%"),
            Partner.contact_personal_email.ilike(f"%{email}%")
        ))
    if phone:
        filters.append(or_(
            Partner.contact_phone.ilike(f"%{phone}%"),
            Partner.contact_personal_phone.ilike(f"%{phone}%")
        ))

    base_query = select(Partner)

    if filters:
        base_query = base_query.where(*filters)

    # Get total count
    total = session.exec(select(func.count()).select_from(base_query.subquery())).scalar_one()

    # Apply pagination
    partners = [row[0] for row in session.exec(base_query.offset(skip).limit(limit)).all()]

    return PartnersResponse(data=partners, total=total)

