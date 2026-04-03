# app/services/couponPayloadService.py

from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.mess.mealSlotExpiryModel import MealSlotExpiry
from sqlalchemy.future import select

IST = ZoneInfo("Asia/Kolkata")


async def compute_expiry(
    db,
    mess_id,
    meal_slot,
    coupon_date
):
    result = await db.execute(
        select(MealSlotExpiry).filter(
            MealSlotExpiry.mess_id == mess_id,
            MealSlotExpiry.meal_slot == meal_slot
        )
    )

    expiry = result.scalar_one_or_none()

    if not expiry:
        raise Exception("Meal slot expiry not configured")

    return datetime.combine(
        coupon_date,
        expiry.end_time,
        tzinfo=IST
    )