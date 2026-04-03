from datetime import timezone, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from zoneinfo import ZoneInfo

from app.db.session import get_db
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.mealSubmissionWindowModel import MealSubmissionWindow

from app.schemas.mess.submissionWindowSchema import SubmissionWindowResponse
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek

from app.services.weekResolverService import resolve_week
from app.services.submissionWindowCreationService import get_or_create_submission_window
from app.models.mess.mealSlotExpiryModel import MealSlotExpiry
from app.schemas.mess.mealSlotExpirySchema import MealSlotExpiryResponse

IST = ZoneInfo("Asia/Kolkata")

router = APIRouter(
    prefix="/fetch/mess",
    tags=["Meal Slot Expiry"]
)

@router.get("/meal-slot-expiry", response_model=list[MealSlotExpiryResponse])
async def get_submission_window(
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db)
):
    user = await db.execute(
        select(MessAdmin).filter(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        )
    )
    mess_admin = user.scalar_one_or_none()

    mess_id = mess_admin.mess_id

    meal_slot_result = await db.execute(
        select(MealSlotExpiry).filter(
            MealSlotExpiry.mess_id == mess_id,
            MealSlotExpiry.college_id == current_user.college_id
        )
    )

    meal_slots = meal_slot_result.scalars().all()

    if not meal_slots:
        raise HTTPException(404, "Meal Slot not found")

    return [
        MealSlotExpiryResponse(
            meal_slot=slot.meal_slot,
            start_time=slot.start_time,
            end_time=slot.end_time
        )
        for slot in meal_slots
    ]


