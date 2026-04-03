# # app/services/couponGenerationService.py
#
# import uuid
# from datetime import datetime, timedelta
# from zoneinfo import ZoneInfo
# from sqlalchemy import select, update
# from sqlalchemy.dialects.postgresql import insert
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.models.mess.couponModel import Coupon
# from app.models.mess.messWeekModel import MessWeek
# from app.models.student.mealPreferenceModel import MealPreference
# from app.models.mess.mealSlotExpiryModel import MealSlotExpiry
# from app.models.mess.mealDayPolicy import MessDayPolicy
# from app.models.student.studentModel import Student
# from app.models.user.userModel import User
#
# from app.services.messClosureService import is_mess_closed
# from app.utils.mealSlot import MealSlot
# from app.utils.mealType import MealType
#
# IST = ZoneInfo("Asia/Kolkata")
# ALL_SLOTS = list(MealSlot)
# BATCH_SIZE = 1000
#
#
# async def generate_coupons_for_week(
#     db: AsyncSession,
#     mess_id,
#     college_id
# ):
#
#
#
#     async with db.begin():
#
#         today = datetime.now(IST).date()
#
#         # -------- GET WEEK --------
#         result = await db.execute(
#             select(MessWeek).filter(
#                 MessWeek.mess_id == mess_id,
#                 MessWeek.start_date <= today,
#                 MessWeek.end_date >= today
#             )
#         )
#         week = result.scalar_one_or_none()
#
#         if not week:
#             print("no week found returning")
#             return
#
#         # -------- EARLY STATUS CHECK --------
#         if week.generation_status != "pending":
#             print("no gener status pending")
#             return
#
#         # -------- FULL WEEK CLOSURE CHECK --------
#         current = week.start_date
#         full_closed = True
#
#         while current <= week.end_date:
#             if not await is_mess_closed(db, mess_id, current):
#                 full_closed = False
#                 break
#             current += timedelta(days=1)
#
#         if full_closed:
#             await db.execute(
#                 update(MessWeek)
#                 .where(MessWeek.id == week.id)
#                 .values(generation_status="skipped")
#             )
#             await db.commit()
#             print("Mess closed")
#
#             return
#
#         print(db.in_transaction())
#
#         # -------- CLAIM (LOCK) --------
#         claim_stmt = (
#             update(MessWeek)
#             .where(
#                 MessWeek.id == week.id,
#                 MessWeek.generation_status == "pending"
#             )
#             .values(generation_status="generated")
#             .returning(MessWeek.id)
#         )
#
#         result = await db.execute(claim_stmt)
#
#         # someone else already generating
#         if not result.first():
#             print("race condn")
#             return
#
#         # -------- FETCH CONFIG --------
#         expiry_rows = (
#             await db.execute(
#                 select(MealSlotExpiry).filter(
#                     MealSlotExpiry.mess_id == mess_id
#                 )
#             )
#         ).scalars().all()
#
#         if not expiry_rows:
#             raise Exception("Meal slot expiry not configured")
#
#         expiry_map = {e.meal_slot: e.end_time for e in expiry_rows}
#
#         policy_rows = (
#             await db.execute(
#                 select(MessDayPolicy).filter(
#                     MessDayPolicy.mess_id == mess_id,
#                     MessDayPolicy.week_id == week.id
#                 )
#             )
#         ).scalars().all()
#
#         policy_map = {p.day.value: p.is_compulsory for p in policy_rows}
#
#         # -------- STUDENTS --------
#         students = (
#             await db.execute(
#                 select(Student.user_id)
#                 .join(User, User.id == Student.user_id)
#                 .filter(
#                     Student.mess_id == mess_id,
#                     Student.college_id == college_id,
#                     User.is_active == True
#                 )
#             )
#         ).scalars().all()
#
#         if not students:
#             print("no students found")
#             # nothing to generate but still valid
#             return
#
#         batch = []
#         current_date = week.start_date
#
#         while current_date <= week.end_date:
#
#             if await is_mess_closed(db, mess_id, current_date):
#                 current_date += timedelta(days=1)
#                 continue
#
#             day_name = current_date.strftime("%A").lower()
#             is_compulsory = policy_map.get(day_name, False)
#
#             prefs = (
#                 await db.execute(
#                     select(MealPreference).filter(
#                         MealPreference.date == current_date,
#                         MealPreference.student_id.in_(students)
#                     )
#                 )
#             ).scalars().all()
#
#             pref_map = {
#                 (p.student_id, p.meal_slot): p.meal_type
#                 for p in prefs
#             }
#
#             for student_id in students:
#                 for slot in ALL_SLOTS:
#
#                     if slot not in expiry_map:
#                         continue
#
#                     meal_type = pref_map.get((student_id, slot))
#
#                     if meal_type is None:
#                         if is_compulsory:
#                             meal_type = MealType.veg
#                         else:
#                             continue
#
#                     batch.append({
#                         "id": uuid.uuid4(),
#                         "student_id": student_id,
#                         "college_id": college_id,
#                         "mess_id": mess_id,
#                         "week_id": week.id,
#                         "date": current_date,
#                         "meal_slot": slot,
#                         "meal_type": meal_type,
#                     })
#
#                     # -------- BATCH INSERT --------
#                     if len(batch) >= BATCH_SIZE:
#                         stmt = insert(Coupon).values(batch)
#                         stmt = stmt.on_conflict_do_nothing(
#                             index_elements=["student_id", "date", "meal_slot"]
#                         )
#                         await db.execute(stmt)
#                         batch.clear()
#
#             current_date += timedelta(days=1)
#
#         # -------- FINAL FLUSH --------
#         if batch:
#             stmt = insert(Coupon).values(batch)
#             stmt = stmt.on_conflict_do_nothing(
#                 index_elements=["student_id", "date", "meal_slot"]
#             )
#             await db.execute(stmt)


# app/services/couponGenerationService.py

from datetime import datetime
from http.client import HTTPException
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException,status

from app.models.mess.messWeekModel import MessWeek
from app.services.getLatestDayPolicy import get_latest_policy_week
from app.services.getLatestMenuWeek import get_latest_menu_week

IST = ZoneInfo("Asia/Kolkata")

VALID_START_STATES = ["pending", "failed"]

SQL_GENERATE_COUPONS = """
INSERT INTO coupons (
    id,
    student_id,
    college_id,
    mess_id,
    week_id,
    date,
    meal_slot,
    meal_type
)
SELECT
    gen_random_uuid(),
    s.user_id,
    :college_id,
    :mess_id,
    :week_id,
    d.date,
    m.meal_slot,
    COALESCE(
        mp.meal_type,
        CASE
            WHEN COALESCE(mdp.is_compulsory, false) THEN 'veg'::meal_type_enum
            ELSE NULL
        END
    ) AS meal_type
FROM students s

JOIN users u
    ON u.id = s.user_id
    AND u.is_active = true

CROSS JOIN generate_series(
    :week_start,
    :week_end,
    INTERVAL '1 day'
) AS d(date)

JOIN mess_menu m
    ON m.mess_id = :mess_id
    AND m.week_id = :menu_week_id
    AND m.day = TRIM(LOWER(TO_CHAR(d.date, 'day')))::weekday_enum

LEFT JOIN meal_preferences mp
    ON mp.student_id = s.user_id
    AND mp.date = d.date
    AND mp.meal_slot = m.meal_slot

LEFT JOIN mess_day_policies mdp
    ON mdp.mess_id = :mess_id
    AND mdp.week_id = :policy_week_id
    AND mdp.day = m.day

LEFT JOIN mess_closures mc
    ON mc.mess_id = :mess_id
    AND mc.college_id = :college_id
    AND d.date BETWEEN mc.start_date AND mc.end_date

WHERE
    s.mess_id = :mess_id
    AND s.college_id = :college_id
    AND mc.mess_id IS NULL
    AND (
        mp.meal_type IS NOT NULL
        OR COALESCE(mdp.is_compulsory, false) = true
    )

ON CONFLICT (student_id, date, meal_slot)
DO NOTHING;
"""


async def generate_coupons_for_week(db: AsyncSession, mess_id, college_id):
    today = datetime.now(IST).date()

    weeks = (
        await db.execute(
            select(MessWeek).where(
                MessWeek.mess_id == mess_id,
                MessWeek.start_date <= today,
                MessWeek.end_date >= today
            )
        )
    )

    week: Optional[MessWeek] = weeks.scalar_one_or_none()

    if week is None:
        raise Exception("No active mess week found")

    week_id = week.id
    week_start = week.start_date
    week_end = week.end_date

    claim_stmt = (
        update(MessWeek)
        .where(
            MessWeek.id == week_id,
            MessWeek.generation_status.in_(VALID_START_STATES)
        )
        .values(
            generation_status="generating",
            generation_started_at=datetime.now(IST)
        )
        .returning(MessWeek.id)
    )

    result = await db.execute(claim_stmt)

    if not result.first():
        await db.rollback()
        return

    try:
        menu_week_id = await get_latest_menu_week(db, mess_id, week_start)
        policy_week_id = await get_latest_policy_week(db, mess_id, week_start)

        print(menu_week_id)

        if not menu_week_id:
            raise Exception("No valid menu found for fallback")


        await db.execute(
            text(SQL_GENERATE_COUPONS),
            {
                "mess_id": mess_id,
                "college_id": college_id,
                "week_id": week_id,
                "menu_week_id": menu_week_id,
                "policy_week_id": policy_week_id,
                "week_start": week_start,
                "week_end": week_end,
            }
        )

        await db.execute(
            update(MessWeek)
            .where(MessWeek.id == week_id)
            .values(generation_status="generated")
        )

        await db.commit()

    except Exception as e:
        await db.rollback()

        await db.execute(
            update(MessWeek)
            .where(MessWeek.id == week_id)
            .values(generation_status="failed")
        )

        await db.commit()

        raise e