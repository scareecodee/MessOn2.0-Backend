from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Optional

from app.models.mess.couponModel import Coupon
from app.services.couponPayloadService import build_coupon_payload
from app.schemas.mess.couponPayloadSchema import CouponPayload
from app.utils.mealSlot import MealSlot

IST = ZoneInfo("Asia/Kolkata")

async def fetch_coupon_by_meal(
    db: AsyncSession,
    student_id: UUID,
    mess_id: UUID,
    college_id : UUID,
    meal_slot: MealSlot,
) -> Optional[CouponPayload]:

    today = datetime.now(IST).date()

    result = await db.execute(
        select(Coupon).filter(
            Coupon.student_id == student_id,
            Coupon.mess_id == mess_id,
            Coupon.college_id == college_id,
            Coupon.date == today,
            Coupon.meal_slot == meal_slot,
        )
    )

    coupon = result.scalar_one_or_none()

    if not coupon:
        return None

    return await build_coupon_payload(
        db=db,
        coupon=coupon
    )