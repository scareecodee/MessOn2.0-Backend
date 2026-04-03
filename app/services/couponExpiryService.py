# app/services/couponQueryService.py

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Optional

from app.models.mess.couponModel import Coupon
from app.services.couponGenerationService import generate_coupons_for_week
from app.services.couponPayloadService import build_coupon_payload, CouponPayload
from app.utils.mealSlot import MealSlot

IST = ZoneInfo("Asia/Kolkata")


async def fetch_coupon_by_meal(
    db: AsyncSession,
    student_id: UUID,
    mess_id: UUID,
    college_id: UUID,
    meal_slot: MealSlot,
) -> CouponPayload:

    today = datetime.now(IST).date()

    result = await db.execute(
        select(Coupon).filter(
            Coupon.student_id == student_id,
            Coupon.mess_id == mess_id,
            Coupon.date == today,
            Coupon.meal_slot == meal_slot,
        )
    )

    coupon = result.scalar_one_or_none()

    if not coupon:
        await generate_coupons_for_week(db, mess_id, college_id)

        result = await db.execute(
            select(Coupon).filter(
                Coupon.student_id == student_id,
                Coupon.mess_id == mess_id,
                Coupon.date == today,
                Coupon.meal_slot == meal_slot,
            )
        )
        coupon = result.scalar_one_or_none()

        if not coupon:
            raise HTTPException(404, "Coupon not found")

    return await build_coupon_payload(
       db=db,
       coupon=coupon,
    )