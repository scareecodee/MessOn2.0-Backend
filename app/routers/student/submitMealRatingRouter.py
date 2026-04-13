from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user.userModel import User
from app.schemas.student.ratingSchema import RatingRequest
from app.security.dependencies.getCurrentRole import get_current_role
from app.services.submitRatingService import submit_rating
from app.utils.userRole import UserRole

router = APIRouter(
    tags=["Student Meal Rating"],
)


@router.post("/rate-meal")
async def rate_meal(
    payload: RatingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_role([UserRole.student]))
):

    # if payload.date != date.today():
    #     raise HTTPException(400, "You can only rate today's meal")

    today = date.today()

    result = await submit_rating(
        db=db,
        student_id=current_user.id,
        date=today,
        meal_slot=payload.meal_slot,
        rating=payload.rating
    )

    return result