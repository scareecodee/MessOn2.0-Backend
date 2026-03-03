from datetime import timedelta
from sqlalchemy.orm import Session
from app.models.student.studentModel import Student
from app.models.mess.couponModel import Coupon
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.weekDays import WeekDays
from app.models.student.mealPreferenceModel import MealPreference

import os
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

# Load expiry times from .env
BREAKFAST_EXPIRE = os.getenv("BREAKFAST_EXPIRE")
LUNCH_EXPIRE = os.getenv("LUNCH_EXPIRE")
DINNER_EXPIRE = os.getenv("DINNER_EXPIRE")


def get_expiry_timestamp(today, time_str):
    hour, minute = map(int, time_str.split(":"))

    expiry_datetime = datetime(
        today.year,
        today.month,
        today.day,
        hour,
        minute,
        tzinfo=IST
    )

    return int(expiry_datetime.timestamp())


def get_today_weekday_enum(today):
    weekday_str = today.strftime("%A").lower()
    return WeekDays(weekday_str)


def generate_today_coupons(db: Session, today):

    # 🔴 Delete only today's coupons (safer)
    db.query(Coupon).filter(Coupon.date == today).delete()
    db.commit()

    # 🧠 WEEK START (Monday)
    week_start = today - timedelta(days=today.weekday())
    today_weekday = get_today_weekday_enum(today)

    active_students = (
        db.query(Student)
        .filter(Student.is_active == True)
        .all()
    )

    meal_slots = [
        MealSlot.breakfast,
        MealSlot.lunch,
        MealSlot.dinner
    ]

    for student in active_students:
        for slot in meal_slots:

            pref = (
                db.query(MealPreference)
                .filter(
                    MealPreference.userId == student.id,
                    MealPreference.weekStart == week_start,
                    MealPreference.day == today_weekday,
                    MealPreference.mealSlot == slot
                )
                .first()
            )

            meal_type = pref.preference if pref else MealType.veg

            # ⭐ Determine expiry based on meal slot
            if slot == MealSlot.breakfast:
                expires_at = get_expiry_timestamp(today, BREAKFAST_EXPIRE)

            elif slot == MealSlot.lunch:
                expires_at = get_expiry_timestamp(today, LUNCH_EXPIRE)

            else:
                expires_at = get_expiry_timestamp(today, DINNER_EXPIRE)

            coupon = Coupon(
                userId=student.id,
                date=today,
                mealSlot=slot,
                mealType=meal_type,
                expiresAt=expires_at
            )

            db.add(coupon)

    db.commit()
