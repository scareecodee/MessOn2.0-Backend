from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin

from app.schemas.student.ratingSchema import RatingAnalyticsResponse
from app.services.computeRatingAnalyticsService import get_rating_stats

from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/mess",
    tags=["Rating Stats"]
)


@router.get("/rating-analytics", response_model=list[RatingAnalyticsResponse])
async def fetch_rating_stats(
    mess_id:UUID | None = None,
    days: int = Query(1, ge=1, le=30),
    current_user: User = Depends(get_current_role([UserRole.mess_admin,UserRole.college_admin])),
    db: AsyncSession = Depends(get_db)
):

    if current_user.role == UserRole.mess_admin:
        mess_admins = await db.execute(
            select(MessAdmin).where(
                MessAdmin.user_id == current_user.id,
                MessAdmin.college_id == current_user.college_id
            )
        )

        mess_admin: Optional[MessAdmin] = mess_admins.scalar_one_or_none()

        if not mess_admin:
            raise HTTPException(404, "Mess admin not found")

        return await get_rating_stats(
            db=db,
            mess_id=mess_admin.mess_id,
            college_id=current_user.college_id,
            days=days
        )
    else:
        return await get_rating_stats(
            db=db,
            mess_id=mess_id,
            college_id=current_user.college_id,
            days=days
        )