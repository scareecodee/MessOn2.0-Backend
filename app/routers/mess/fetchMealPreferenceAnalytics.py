# app/routes/mealPreferenceRoutes.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek
from app.services.weekResolverService import resolve_week
from app.services.mealPreferenceCountService import get_meal_preference_counts
from app.schemas.mess.mealCountResponse import MealCountResponse

router = APIRouter(
    prefix="/fetch",
    tags=["Meal Preference Analytics"]
)

@router.get("/meal-preference-analytics/{menu_week}",response_model=List[MealCountResponse])
async def meal_count(
    menu_week: MenuWeek,
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db)
):
    admins = (
        await db.execute(
            select(MessAdmin).where(
                MessAdmin.user_id == current_user.id,
                MessAdmin.college_id == current_user.college_id
            )
        )
    )
    admin: Optional[MessAdmin] = admins.scalar_one_or_none()

    if not admin:
        raise HTTPException(404, "Mess admin not found")

    week = await resolve_week(
        db,
        menu_week,
        admin.mess_id,
        current_user.college_id
    )

    return await get_meal_preference_counts(
        db=db,
        mess_id=admin.mess_id,
        college_id=current_user.college_id,
        week=week
    )