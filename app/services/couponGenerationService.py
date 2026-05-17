# from datetime import datetime
# from typing import Optional
# from zoneinfo import ZoneInfo
#
# from sqlalchemy import select, update, text
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.models.mess.messWeekModel import MessWeek
# from app.services.getLatestDayPolicy import get_latest_policy_week
# from app.services.getLatestMenuWeek import get_latest_menu_week
# from app.services.weekResolverService import resolve_week
# from app.utils.menuWeek import MenuWeek
#
# IST = ZoneInfo("Asia/Kolkata")
#
# VALID_START_STATES = ["pending", "failed"]
#
# SQL_GENERATE_COUPONS = """
# INSERT INTO coupons (
#     id,
#     student_id,
#     college_id,
#     mess_id,
#     week_id,
#     date,
#     meal_slot,
#     meal_type
# )
# SELECT
#     gen_random_uuid(),
#     s.user_id,
#     :college_id,
#     :mess_id,
#     :week_id,
#     d.date,
#     m.meal_slot,
#     COALESCE(
#         mp.meal_type,
#         CASE
#             WHEN COALESCE(mdp.is_compulsory, false) THEN 'veg'::meal_type_enum
#             ELSE NULL
#         END
#     ) AS meal_type
# FROM students s
#
# JOIN users u
#     ON u.id = s.user_id
#     AND u.is_active = true
#
# CROSS JOIN generate_series(
#     :week_start,
#     :week_end,
#     INTERVAL '1 day'
# ) AS d(date)
#
# JOIN mess_menu m
#     ON m.mess_id = :mess_id
#     AND m.week_id = :menu_week_id
#     AND m.day = TRIM(LOWER(TO_CHAR(d.date, 'day')))::weekday_enum
#
# LEFT JOIN meal_preferences mp
#     ON mp.student_id = s.user_id
#     AND mp.date = d.date
#     AND mp.meal_slot = m.meal_slot
#
# LEFT JOIN mess_day_policies mdp
#     ON mdp.mess_id = :mess_id
#     AND mdp.week_id = :policy_week_id
#     AND mdp.day = m.day
#
# LEFT JOIN mess_closures mc
#     ON mc.mess_id = :mess_id
#     AND mc.college_id = :college_id
#     AND d.date BETWEEN mc.start_date AND mc.end_date
#
# WHERE
#     s.mess_id = :mess_id
#     AND s.college_id = :college_id
#     AND mc.mess_id IS NULL
#     AND (
#         mp.meal_type IS NOT NULL
#         OR COALESCE(mdp.is_compulsory, false) = true
#     )
#
#
# ON CONFLICT (student_id, date, meal_slot)
# DO UPDATE SET
#     meal_type = EXCLUDED.meal_type,
#     week_id   = EXCLUDED.week_id,
#     mess_id   = EXCLUDED.mess_id,
#     college_id = EXCLUDED.college_id
# WHERE
#     coupons.date >= CURRENT_DATE
#     AND coupons.is_scanned = false;
# """
#
#
# async def generate_coupons_for_week(db: AsyncSession, mess_id, college_id):
#     today = datetime.now(IST).date()
#
#     weeks = (
#         await db.execute(
#             select(MessWeek).where(
#                 MessWeek.mess_id == mess_id,
#                 MessWeek.start_date <= today,
#                 MessWeek.end_date >= today
#             ).order_by(MessWeek.start_date.asc())
#             .limit(1)
#         )
#     )
#
#     week: Optional[MessWeek] = weeks.scalar_one_or_none()
#
#     if week is None:
#         week = await resolve_week(
#             db=db,
#             menu_week=MenuWeek.currentWeek,
#             mess_id=mess_id,
#             college_id=college_id,
#         )
#
#     week_id = week.id
#     week_start = week.start_date
#     week_end = week.end_date
#
#     claim_stmt = (
#         update(MessWeek)
#         .where(
#             MessWeek.id == week_id,
#             MessWeek.coupon_generation_status.in_(VALID_START_STATES)
#         )
#         .values(
#             coupon_generation_status="generating",
#             coupon_generation_started_at=datetime.now(IST)
#         )
#         .returning(MessWeek.id)
#     )
#
#     result = await db.execute(claim_stmt)
#
#     if not result.first():
#         await db.rollback()
#         return
#
#     try:
#         menu_week_id = await get_latest_menu_week(db, mess_id, week_start)
#         policy_week_id = await get_latest_policy_week(db, mess_id, week_start)
#
#         print(menu_week_id)
#
#         if not menu_week_id:
#             raise Exception("No valid menu found for fallback")
#
#
#         await db.execute(
#             text(SQL_GENERATE_COUPONS),
#             {
#                 "mess_id": mess_id,
#                 "college_id": college_id,
#                 "week_id": week_id,
#                 "menu_week_id": menu_week_id,
#                 "policy_week_id": policy_week_id,
#                 "week_start": week_start,
#                 "week_end": week_end,
#             }
#         )
#
#         await db.execute(
#             update(MessWeek)
#             .where(MessWeek.id == week_id)
#             .values(coupon_generation_status="generated")
#         )
#
#         await db.commit()
#
#     except Exception as e:
#         await db.rollback()
#
#         await db.execute(
#             update(MessWeek)
#             .where(MessWeek.id == week_id)
#             .values(coupon_generation_status="failed")
#         )
#
#         await db.commit()
#
#         raise e


from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mess.messWeekModel import MessWeek
from app.services.getLatestDayPolicy import get_latest_policy_week
from app.services.getLatestMenuWeek import get_latest_menu_week
from app.services.weekResolverService import resolve_week
from app.utils.menuWeek import MenuWeek

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
            WHEN COALESCE(mdp.is_compulsory, false)
            THEN 'veg'::meal_type_enum
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
    AND mc.id IS NULL
    AND (
        mp.meal_type IS NOT NULL
        OR COALESCE(mdp.is_compulsory, false) = true
    )

ON CONFLICT (student_id, date, meal_slot)

DO UPDATE SET
    meal_type = EXCLUDED.meal_type,
    week_id = EXCLUDED.week_id,
    mess_id = EXCLUDED.mess_id,
    college_id = EXCLUDED.college_id

WHERE
    coupons.date >= CURRENT_DATE
    AND coupons.is_scanned = false;
"""


async def generate_coupons_for_week(
    db: AsyncSession,
    mess_id,
    college_id
):

    today = datetime.now(IST).date()

    week = await resolve_week(
        db=db,
        menu_week=MenuWeek.currentWeek,
        mess_id=mess_id,
        college_id=college_id,
    )

    week_id = week.id

    claim_stmt = (
        update(MessWeek)
        .where(
            MessWeek.id == week_id,
            MessWeek.coupon_generation_status.in_(VALID_START_STATES)
        )
        .values(
            coupon_generation_status="generating",
            coupon_generation_started_at=datetime.now(IST)
        )
        .returning(MessWeek.id)
    )

    result = await db.execute(claim_stmt)

    if not result.first():
        await db.rollback()
        return

    try:

        menu_week_id = await get_latest_menu_week(
            db,
            mess_id,
            week.start_date
        )

        policy_week_id = await get_latest_policy_week(
            db,
            mess_id,
            week.start_date
        )

        if not menu_week_id:
            raise Exception("No valid menu week found")

        await db.execute(
            text(SQL_GENERATE_COUPONS),
            {
                "mess_id": mess_id,
                "college_id": college_id,
                "week_id": week.id,
                "menu_week_id": menu_week_id,
                "policy_week_id": policy_week_id,
                "week_start": week.start_date,
                "week_end": week.end_date,
            }
        )

        await db.execute(
            update(MessWeek)
            .where(MessWeek.id == week.id)
            .values(
                coupon_generation_status="generated"
            )
        )

        await db.commit()

    except Exception as e:

        await db.rollback()

        await db.execute(
            update(MessWeek)
            .where(MessWeek.id == week.id)
            .values(
                coupon_generation_status="failed"
            )
        )

        await db.commit()

        raise e