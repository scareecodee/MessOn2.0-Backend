# import time
# from datetime import datetime
# from zoneinfo import ZoneInfo
# from sqlalchemy.orm import Session
#
# from app.models.mess.couponModel import Coupon
# from app.models.student.studentModel import Student
# from app.services.couponPayloadService import build_coupon_payload
# from app.utils.mealSlot import MealSlot
#
#
# def fetch_coupon_by_meal(
#         db: Session,
#         user: Student,
#         mealSlot: MealSlot,
# ):
#     IST = ZoneInfo("Asia/Kolkata")
#
#     today = datetime.now(IST).date()
#
#     coupon = (
#         db.query(Coupon)
#         .filter(
#             Coupon.userId == user.id,
#             Coupon.date == today,
#             Coupon.mealSlot == mealSlot,
#         )
#         .first()
#     )
#
#     if coupon is None:
#         return None
#
#     return build_coupon_payload(
#         couponId=str(coupon.id),
#         couponDate=coupon.date,
#         mealSlot=coupon.mealSlot,  # ✅ correct
#         mealType=coupon.mealType,  # ✅ correct
#         userId=str(user.id),  # safer
#         usedAt=coupon.usedAt,
#         expiresAt=coupon.expiresAt
#     )
