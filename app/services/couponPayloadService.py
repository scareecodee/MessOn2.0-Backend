# from datetime import date
# from typing import Optional
#
# from app.schemas.mess.couponPayloadSchema import CouponPayload
# from app.security.couponSignature import sign_payload
# from app.models.mess.couponModel import MealType
# from app.utils.mealSlot import MealSlot
#
#
# def build_coupon_payload(
#     *,
#     couponId: str,
#     userId: str,
#     couponDate: date,
#     mealType: MealType,
#     expiresAt: int,
#     usedAt: Optional[int],
#     mealSlot:MealSlot
# ) -> CouponPayload:
#
#
#     unsigned = f"{couponId}|{userId}|{couponDate}|{mealType.value}|{expiresAt}|{mealSlot.value}"
#     signature = sign_payload(unsigned)
#
#     return CouponPayload(
#         couponId=couponId,
#         userId=userId,
#         date=couponDate,
#         mealSlot=mealSlot.value,
#         mealType=mealType.value,
#         expiresAt=expiresAt,
#         usedAt=usedAt,
#         signature=signature,
#     )