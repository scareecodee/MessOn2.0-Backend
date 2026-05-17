
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db

from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.mealSlotExpiryModel import MealSlotExpiry

from app.schemas.mess.mealSlotExpirySchema import (
    MealSlotExpiryResponse
)

from app.security.dependencies.getCurrentRole import (
    get_current_role
)

from app.utils.userRole import UserRole
from app.utils.mealSlot import MealSlot

router = APIRouter(
    prefix="/fetch/mess",
    tags=["Meal Slot Expiry"]
)

ALL_SLOTS = list(MealSlot)


@router.get(
    "/meal-slot-expiry",
    response_model=List[MealSlotExpiryResponse]
)
async def get_meal_slot_expiry(
    current_user: User = Depends(
        get_current_role([UserRole.mess_admin])
    ),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(MessAdmin).where(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        )
    )

    mess_admin = result.scalar_one_or_none()

    if not mess_admin:
        raise HTTPException(
            status_code=404,
            detail="Mess admin not found"
        )

    result = await db.execute(
        select(MealSlotExpiry).where(
            MealSlotExpiry.mess_id == mess_admin.mess_id,
            MealSlotExpiry.college_id == current_user.college_id
        )
    )

    meal_slots = result.scalars().all()

    slot_map = {
        slot.meal_slot: slot
        for slot in meal_slots
    }

    response = []

    for slot in ALL_SLOTS:

        expiry = slot_map.get(slot)

        response.append(
            MealSlotExpiryResponse(
                meal_slot=slot,
                start_time=expiry.start_time if expiry else None,
                end_time=expiry.end_time if expiry else None
            )
        )

    return response