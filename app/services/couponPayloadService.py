from datetime import date, datetime
from typing import Optional
from uuid import UUID
from zoneinfo import ZoneInfo
from app.security.couponSignature import sign_payload
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.schemas.mess.couponPayloadSchema import CouponPayload
from app.models.mess.couponModel import Coupon
from app.utils.computeCouponExpiry import compute_expiry
from app.utils.unsignedCouponPayload import build_unsigned_from_coupon

IST = ZoneInfo("Asia/Kolkata")

async def build_coupon_payload(
    db,
    *,
    coupon,
) -> CouponPayload:
    expires_at = await compute_expiry(
        db=db,
        mess_id=coupon.mess_id,
        meal_slot=coupon.meal_slot,
        coupon_date=coupon.date
    )
    #
    # unsigned = (
    #     f"{coupon.id}|{coupon.student_id}|{coupon.mess_id}|{coupon.college_id}|{coupon.date}"
    #     f"|{coupon.meal_type.value}||{coupon.meal_slot.value}"
    # )

    unsigned = build_unsigned_from_coupon(coupon)

    signature = sign_payload(unsigned)

    return CouponPayload(
        coupon_id=coupon.id,
        student_id=coupon.student_id,
        mess_id=coupon.mess_id,
        college_id=coupon.college_id,
        date=coupon.date,
        meal_slot=coupon.meal_slot.value,
        meal_type=coupon.meal_type.value,
        scanned_at= None,
        signature=signature
    )