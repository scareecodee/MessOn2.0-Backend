# app/api/routes/meal_slot_expiry.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.schemas.mess.mealSlotExpirySchema import (
    MealSlotExpiryRequest,
    MealSlotExpiryResponse
)
from app.services.mealSlotExpiryService import upsert_meal_slot_expiry
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.models.mess.messAdmin import MessAdmin

router = APIRouter(
    prefix="/create/mess",
    tags=["Meal Slot Expiry"]
)


@router.patch("/meal-slot-expiry", response_model=list[MealSlotExpiryResponse])
async def set_meal_slot_expiry(
    payload: list[MealSlotExpiryRequest],
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_role([UserRole.mess_admin]))
):
    user = await db.execute(
        select(MessAdmin).filter(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        )
    )
    mess_admin = user.scalar_one_or_none()

    mess_id=mess_admin.mess_id

    await upsert_meal_slot_expiry(
        db=db,
        data=payload,
        mess_id=mess_id,
        college_id=current_user.college_id
    )

    return payload