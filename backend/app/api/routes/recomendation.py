# api/routes/recommendations.py
from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, or_, func
from app.api.deps import CurrentUser, SessionDep
from app.models.recommendation import (
    Recommendation,
    RecommendationTargetType,
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    RecommendationsResponse
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/", response_model=RecommendationResponse)
def create_recommendation(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        recommendation_in: RecommendationCreate
) -> Any:
    """Create new recommendation"""
    # Verify target exists
    target = session.get(
        recommendation_in.target_type.get_model(),
        recommendation_in.target_id
    )
    if not target:
        raise HTTPException(
            status_code=404,
            detail=f"{recommendation_in.target_type.value} not found"
        )

    db_recommendation = Recommendation(
        **recommendation_in.model_dump(),
        created_by=current_user.email
    )
    session.add(db_recommendation)
    session.commit()
    session.refresh(db_recommendation)
    return db_recommendation


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        recommendation_id: UUID
) -> Any:
    """Get recommendation by ID"""
    recommendation = session.get(Recommendation, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendation


@router.put("/{recommendation_id}", response_model=RecommendationResponse)
def update_recommendation(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        recommendation_id: UUID,
        recommendation_in: RecommendationUpdate
) -> Any:
    """Update recommendation"""
    recommendation = session.get(Recommendation, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    update_data = recommendation_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recommendation, field, value)

    session.add(recommendation)
    session.commit()
    session.refresh(recommendation)
    return recommendation


@router.delete("/{recommendation_id}")
def delete_recommendation(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        recommendation_id: UUID
) -> Any:
    """Delete recommendation"""
    recommendation = session.get(Recommendation, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    session.delete(recommendation)
    session.commit()
    return {"message": "Recommendation deleted successfully"}


@router.get("/", response_model=RecommendationsResponse)
def list_recommendations(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        skip: int = 0,
        limit: int = 100,
        target_type: Optional[RecommendationTargetType] = None,
        target_id: Optional[UUID] = None,
        status: Optional[str] = None
) -> Any:
    """List recommendations with filters"""
    query = select(Recommendation)

    if target_type:
        query = query.where(Recommendation.target_type == target_type)
    if target_id:
        query = query.where(Recommendation.target_id == target_id)
    if status:
        query = query.where(Recommendation.status == status)

    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    recommendations = session.exec(query.offset(skip).limit(limit)).all()

    return RecommendationsResponse(data=recommendations, total=total)


@router.post("/{recommendation_id}/approve")
def approve_recommendation(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        recommendation_id: UUID
) -> Any:
    """Approve a recommendation"""
    recommendation = session.get(Recommendation, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only superusers can approve recommendations"
        )

    recommendation.status = "approved"
    recommendation.approved_by = current_user.email
    recommendation.approved_at = datetime.utcnow()

    session.add(recommendation)
    session.commit()
    return {"message": "Recommendation approved successfully"}