#
#
#
# from datetime import datetime
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
#             WHEN COALESCE(mdp.is_compulsory, false)
#             THEN 'veg'::meal_type_enum
#             ELSE NULL
#         END
#     ) AS meal_type
#
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
#     AND mc.id IS NULL
#     AND (
#         mp.meal_type IS NOT NULL
#         OR COALESCE(mdp.is_compulsory, false) = true
#     )
#
# ON CONFLICT (student_id, date, meal_slot)
#
# DO UPDATE SET
#     meal_type = EXCLUDED.meal_type,
#     week_id = EXCLUDED.week_id,
#     mess_id = EXCLUDED.mess_id,
#     college_id = EXCLUDED.college_id
#
# WHERE
#     coupons.date >= CURRENT_DATE
#     AND coupons.is_scanned = false;
# """
#
#
# async def generate_coupons_for_week(
#     db: AsyncSession,
#     mess_id,
#     college_id
# ):
#
#     today = datetime.now(IST).date()
#
#     week = await resolve_week(
#         db=db,
#         menu_week=MenuWeek.currentWeek,
#         mess_id=mess_id,
#         college_id=college_id,
#     )
#
#     week_id = week.id
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
#
#         menu_week_id = await get_latest_menu_week(
#             db,
#             mess_id,
#             week.start_date
#         )
#
#         policy_week_id = await get_latest_policy_week(
#             db,
#             mess_id,
#             week.start_date
#         )
#
#         if not menu_week_id:
#             raise Exception("No valid menu week found")
#
#         await db.execute(
#             text(SQL_GENERATE_COUPONS),
#             {
#                 "mess_id": mess_id,
#                 "college_id": college_id,
#                 "week_id": week.id,
#                 "menu_week_id": menu_week_id,
#                 "policy_week_id": policy_week_id,
#                 "week_start": week.start_date,
#                 "week_end": week.end_date,
#             }
#         )
#
#         await db.execute(
#             update(MessWeek)
#             .where(MessWeek.id == week.id)
#             .values(
#                 coupon_generation_status="generated"
#             )
#         )
#
#         await db.commit()
#
#     except Exception as e:
#
#         await db.rollback()
#
#         await db.execute(
#             update(MessWeek)
#             .where(MessWeek.id == week.id)
#             .values(
#                 coupon_generation_status="failed"
#             )
#         )
#
#         await db.commit()
#
#         raise e

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import (update,text,select,func)

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.mess.messWeekModel import MessWeek
from app.models.mess.couponModel import Coupon
from app.services.getLatestDayPolicy import  get_latest_policy_week
from app.services.getLatestMenuWeek import get_latest_menu_week
from app.services.getLatestPreferenceWeek import get_latest_preference_week
from app.services.weekResolverService import resolve_week
from app.utils.menuWeek import MenuWeek
from app.utils.couponGenerationStatus import CouponGenerationStatus
from app.schemas.mess.couponResponseSchema import CouponGenerationResponse
from fastapi import HTTPException,status

IST = ZoneInfo("Asia/Kolkata")

VALID_START_STATES = [
    CouponGenerationStatus.pending.value,
    CouponGenerationStatus.failed.value
]

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
    AND m.day = TRIM(
        LOWER(TO_CHAR(d.date, 'day'))
    )::weekday_enum

LEFT JOIN meal_preferences mp
    ON mp.student_id = s.user_id
    AND mp.week_id = :preference_week_id
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

    AND m.meal_type =
        COALESCE(
            mp.meal_type,
            CASE
                WHEN COALESCE(mdp.is_compulsory, false)
                THEN 'veg'::meal_type_enum
                ELSE NULL
            END
        )

ON CONFLICT (student_id, date, meal_slot)

DO UPDATE SET
    meal_type = EXCLUDED.meal_type,
    week_id = EXCLUDED.week_id,
    mess_id = EXCLUDED.mess_id,
    college_id = EXCLUDED.college_id

WHERE
    coupons.date >= CURRENT_DATE
    AND coupons.scanned_at IS NULL;
"""


async def generate_coupons_for_week(
    db: AsyncSession,
    mess_id,
    college_id
):
    week = await resolve_week(
        db=db,
        menu_week=MenuWeek.currentWeek,
        mess_id=mess_id,
        college_id=college_id,
    )
    week_id = week.id
    week_start = week.start_date
    week_end = week.end_date

    # coupon_exists_stmt = (
    #     select(Coupon.id)
    #     .where(
    #         Coupon.week_id == week_id
    #     )
    #     .limit(1)
    # )

    # coupon_exists_result = await db.execute( coupon_exists_stmt)

    # existing_coupon = (
    #     coupon_exists_result.scalar_one_or_none()
    # )
    # print("coupon exists",existing_coupon)

    # if existing_coupon:

    #     print(f"Coupons already exist for week {week_id}")

    #     return CouponGenerationResponse(
    #         coupon_generation_status= CouponGenerationStatus.generated,
    #         detail = "Coupon has already generated"
    #     )
    
    claim_stmt = (
        update(MessWeek)
        .where(
            MessWeek.id == week_id,
            MessWeek.coupon_generation_status.in_(
                VALID_START_STATES
            )
        )
        .values(
            coupon_generation_status=CouponGenerationStatus.generating.value,
            coupon_generation_started_at=datetime.now(IST)
        )
        .returning(MessWeek.id)
    )

    claim_result = await db.execute(
        claim_stmt
    )

    claimed = claim_result.first()

    if not claimed:
        await db.rollback()
        print(
            f"Coupon generation lock denied for week {week_id}"
        )
        return CouponGenerationResponse(
            coupon_generation_status = CouponGenerationStatus.generated,
            detail = "Coupon is already generated"
        )

    try:
        menu_week_id = await get_latest_menu_week(
            db,
            mess_id,
            week_start
        )

        policy_week_id = await get_latest_policy_week(
            db,
            mess_id,
            week_start
        )

        preference_week_id = await get_latest_preference_week(
            db,
            mess_id,
            week_start
        )


        if not menu_week_id:

            await db.execute(
                update(MessWeek)
                .where(MessWeek.id == week_id)
                .values(
                    coupon_generation_status=CouponGenerationStatus.failed.value
                )
            )

            await db.commit()

            print(
                f"No valid menu found for week {week_id}"
            )
            # return {
            #     "status": "menu_not_configured"
            # }
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Menu is not configured")

        before_count_stmt = (
            select(func.count(Coupon.id))
            .where(
                Coupon.week_id == week_id
            )
        )

        before_count_result = await db.execute(
            before_count_stmt
        )

        before_count = (
                before_count_result.scalar() or 0
        )

        print(
            f"Coupons before generation: {before_count}"
        )

        print("week_id", week_id)
        print("policy_week_id", policy_week_id)
        print("menu_week_id", menu_week_id)
        print("prefernce_week_id", preference_week_id)
        print("mess_id", mess_id)
        print("college_id", college_id)
        print("week_start", week_start)
        print("week_end", week_end)

        print(SQL_GENERATE_COUPONS[:500])
        
        generation_result = await db.execute(
            text(SQL_GENERATE_COUPONS),
            {
                "mess_id": mess_id,
                "college_id": college_id,
                "week_id": week_id,
                "menu_week_id": menu_week_id,
                "policy_week_id": policy_week_id,
                "preference_week_id": preference_week_id,
                "week_start": week_start,
                "week_end": week_end,
            }
        )
        
        print(
            "Rows affected during generation:",
            generation_result.rowcount
        )
        after_count_stmt = (
            select(func.count(Coupon.id))
            .where(
                Coupon.week_id == week_id
            )
        )

        after_count_result = await db.execute(
            after_count_stmt
        )
        after_count = (
                after_count_result.scalar() or 0
        )
        generated_now = after_count - before_count
        print(f"New coupons generated: {generated_now}")
        if generated_now <= 0:
            raise Exception(
                "Coupon generation failed. No new coupons inserted."
            )
        
        await db.execute(
            update(MessWeek)
            .where(MessWeek.id == week_id)
            .values(
                coupon_generation_status=CouponGenerationStatus.generated.value
            )
        )

        await db.commit()
        print("going to gen couponsssss..")

        return CouponGenerationResponse(
            coupon_generation_status= CouponGenerationStatus.generated,
            detail = "Coupon has already generated",
            generated_coupon_count= generated_now
        )


    except Exception as e:

        print("COUPON GENERATION FAILED:",str(e))

        await db.rollback()
        await db.execute(
            update(MessWeek)
            .where(MessWeek.id == week_id)
            .values(coupon_generation_status=CouponGenerationStatus.failed.value)
        )
        await db.commit()

        raise e