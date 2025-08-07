# api/routes/events.py
import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, or_, func
from typing import Optional, Any
from datetime import datetime

from app.models.event import EventResponse, EventCreate, Event, EventsResponse, EventStatus, ExchangeLevel
from app.api.deps import CurrentUser, SessionDep

from app.models.event import EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventResponse)
def create_event(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        event_in: EventCreate
) -> Any:
    db_event = Event(**event_in.model_dump(), created_by=current_user.id)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@router.get("/", response_model=EventsResponse)
def list_events(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        skip: int = 0,
        limit: int = 100,
        status: Optional[EventStatus] = None,
        exchange_level: Optional[ExchangeLevel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
) -> Any:
    query = select(Event)

    if status:
        query = query.where(Event.status == status)
    if exchange_level:
        query = query.where(Event.exchange_level == exchange_level)
    if start_date:
        query = query.where(Event.start_time >= start_date)
    if end_date:
        query = query.where(Event.start_time <= end_date)

    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    events = session.exec(query.offset(skip).limit(limit)).all()
    return EventsResponse(data=events, total=total)

# api/routes/events.py
@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event_id: uuid.UUID,
    event_in: EventUpdate
) -> Any:
    """Update an event"""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = event_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.delete("/{event_id}")
def delete_event(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    event_id: uuid.UUID
) -> Any:
    """Delete an event"""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    session.delete(event)
    session.commit()
    return {"message": "Event deleted successfully"}

