# api/routes/partner_events.py
import uuid
from datetime import datetime
from select import select

from fastapi import APIRouter, HTTPException, Query
from typing import Any, Optional, List

from app.models.partnerEvent import PartnerEventResponse, PartnerEventCreate, PartnerEvent, EventScheduleResponse, EventScheduleCreate
from app.api.deps import CurrentUser, SessionDep

from app.models import EventSchedule
from sqlalchemy.sql.functions import func

from app.models.partnerEvent import PartnerEventsResponse

from app.models.partnerEvent import PartnerEventUpdate, EventScheduleUpdate

router = APIRouter(prefix="/partner-events", tags=["partner events"])

@router.post("/", response_model=PartnerEventResponse)
def create_partner_event(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        event_in: PartnerEventCreate
) -> Any:
    db_event = PartnerEvent(**event_in.model_dump())
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@router.post("/{event_id}/schedules", response_model=EventScheduleResponse)
def add_event_schedule(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        event_id: uuid.UUID,
        schedule_in: EventScheduleCreate
) -> Any:
    event = session.get(PartnerEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db_schedule = EventSchedule(**schedule_in.model_dump(), event_id=event_id)
    session.add(db_schedule)
    session.commit()
    session.refresh(db_schedule)
    return db_schedule


@router.get("/", response_model=PartnerEventsResponse)
def list_partner_events(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
) -> Any:
    query = select(PartnerEvent)

    if status:
        query = query.where(PartnerEvent.status == status)
    if start_date:
        query = query.where(PartnerEvent.start_time >= start_date)
    if end_date:
        query = query.where(PartnerEvent.end_time <= end_date)

    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    events = session.exec(query.offset(skip).limit(limit)).all()
    return PartnerEventsResponse(data=events, total=total)


@router.get("/{event_id}/schedules", response_model=List[EventScheduleResponse])
def list_event_schedules(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        event_id: uuid.UUID,
) -> Any:
    event = session.get(PartnerEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    query = select(EventSchedule).where(EventSchedule.event_id == event_id)
    schedules = session.exec(query).all()
    return schedules

# api/routes/partner_events.py
@router.put("/{event_id}", response_model=PartnerEventResponse)
def update_partner_event(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event_id: uuid.UUID,
    event_in: PartnerEventUpdate
) -> Any:
    """Update a partner event"""
    event = session.get(PartnerEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Partner event not found")

    update_data = event_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.delete("/{event_id}")
def delete_partner_event(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event_id: uuid.UUID
) -> Any:
    """Delete a partner event"""
    event = session.get(PartnerEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Partner event not found")

    session.delete(event)
    session.commit()
    return {"message": "Partner event deleted successfully"}

@router.put("/{event_id}/schedules/{schedule_id}", response_model=EventScheduleResponse)
def update_event_schedule(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event_id: uuid.UUID,
    schedule_id: uuid.UUID,
    schedule_in: EventScheduleUpdate
) -> Any:
    """Update an event schedule"""
    schedule = session.get(EventSchedule, schedule_id)
    if not schedule or schedule.event_id != event_id:
        raise HTTPException(status_code=404, detail="Schedule not found")

    update_data = schedule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)

    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule

@router.delete("/{event_id}/schedules/{schedule_id}")
def delete_event_schedule(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event_id: uuid.UUID,
    schedule_id: uuid.UUID
) -> Any:
    """Delete an event schedule"""
    schedule = session.get(EventSchedule, schedule_id)
    if not schedule or schedule.event_id != event_id:
        raise HTTPException(status_code=404, detail="Schedule not found")

    session.delete(schedule)
    session.commit()
    return {"message": "Schedule deleted successfully"}
