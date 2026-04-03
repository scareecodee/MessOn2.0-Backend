# app/services/mealPreferenceCountService.py

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.schemas.mess.mealCountResponse import MealCountResponse, MealSlotCount
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.db.enums import weekday_enum,meal_type_enum
from app.services.getLatestDayPolicy import get_latest_policy_week
from app.services.getLatestMenuWeek import get_latest_menu_week

# SQL_MEAL_COUNT = """
#  WITH dates AS (
#     SELECT generate_series(
#         :week_start_date,
#         :week_end_date,
#         INTERVAL '1 day'
#     )::date AS date
# ),
#
# base AS (
#     SELECT
#         s.user_id AS student_id,
#         d.date,
#         m.meal_slot,
#         m.day
#     FROM students s
#
#     JOIN users u
#         ON u.id = s.user_id
#         AND u.is_active = true
#
#     CROSS JOIN dates d
#
#     JOIN mess_menu m
#         ON m.mess_id = :mess_id
#         AND m.week_id = :menu_week_id
#         AND m.day = TRIM(LOWER(TO_CHAR(d.date, 'day')))::weekday_enum
#
#     WHERE
#         s.mess_id = :mess_id
#         AND s.college_id = :college_id
# ),
#
# mp_unique AS (
#     SELECT DISTINCT ON (student_id, date, meal_slot)
#         student_id, date, meal_slot, meal_type
#     FROM meal_preferences
# ),
#
# mdp_unique AS (
#     SELECT DISTINCT ON (mess_id,week_id, day)
#         mess_id,week_id, day, is_compulsory
#     FROM mess_day_policies
# ),
#
# final AS (
#     SELECT
#         b.student_id,
#         b.date,
#         b.meal_slot,
#         COALESCE(
#             mp.meal_type,
#             CASE
#                 WHEN mdp.is_compulsory THEN 'veg'::meal_type_enum
#                 ELSE NULL
#             END
#         ) AS meal_type
#     FROM base b
#
#     LEFT JOIN mp_unique mp
#         ON mp.student_id = b.student_id
#         AND mp.date = b.date
#         AND mp.meal_slot = b.meal_slot
#
#     LEFT JOIN mdp_unique mdp
#         ON mdp.mess_id = :mess_id
#         AND mdp.week_id = :policy_week_id
#         AND mdp.day = b.day
# )
#
# SELECT
#     date,
#     meal_slot,
#     meal_type,
#     COUNT(DISTINCT student_id) AS count
# FROM final
# WHERE meal_type IS NOT NULL
# GROUP BY date, meal_slot, meal_type
# ORDER BY date;
# """
SQL_MEAL_COUNT = """
WITH dates AS (
    SELECT generate_series(
        :week_start_date,
        :week_end_date,
        INTERVAL '1 day'
    )::date AS date
),

base AS (
    SELECT
        s.user_id AS student_id,
        d.date,
        m.meal_slot,
        m.day
    FROM students s

    JOIN users u
        ON u.id = s.user_id
        AND u.is_active = true

    CROSS JOIN dates d

    JOIN mess_menu m 
        ON m.mess_id = :mess_id
        AND m.week_id = :menu_week_id
        AND m.day = TRIM(LOWER(TO_CHAR(d.date, 'day')))::weekday_enum

    WHERE
        s.mess_id = :mess_id
        AND s.college_id = :college_id
),

final AS (
    SELECT
        b.student_id,
        b.date,
        b.meal_slot,
        COALESCE(
            mp.meal_type,
            CASE
                WHEN COALESCE(mdp.is_compulsory, false)
                THEN 'veg'::meal_type_enum
                ELSE NULL
            END
        ) AS meal_type
    FROM base b

    LEFT JOIN meal_preferences mp
        ON mp.student_id = b.student_id
        AND mp.date = b.date
        AND mp.meal_slot = b.meal_slot

    LEFT JOIN mess_day_policies mdp
        ON mdp.mess_id = :mess_id
        AND mdp.week_id = :policy_week_id
        AND mdp.day = b.day
)

SELECT
    date,
    meal_slot,
    meal_type,
    COUNT(DISTINCT student_id) AS count
FROM final
WHERE meal_type IS NOT NULL
GROUP BY date, meal_slot, meal_type
ORDER BY date;
"""

async def get_meal_preference_counts(
    db: AsyncSession,
    mess_id,
    college_id,
    week
) -> list[MealCountResponse]:

    menu_week_id = await get_latest_menu_week(db, mess_id, week.start_date)
    policy_week_id = await get_latest_policy_week(db, mess_id, week.start_date)

    result = await db.execute(
        text(SQL_MEAL_COUNT),
        {
            "mess_id": mess_id,
            "college_id": college_id,
            "week_id": week.id,
            "menu_week_id" : menu_week_id,
            "policy_week_id" : policy_week_id,
            "week_start_date": week.start_date,
            "week_end_date": week.end_date,
        }
    )

    rows = result.fetchall()

    data_map: dict[date, dict] = {}

    for row in rows:
        date = row.date
        slot = row.meal_slot
        mtype = row.meal_type
        count = row.count

        if date not in data_map:
            data_map[date] = {
                MealSlot.breakfast: {MealType.veg: 0, MealType.nonVeg: 0},
                MealSlot.lunch: {MealType.veg: 0, MealType.nonVeg: 0},
                MealSlot.dinner: {MealType.veg: 0, MealType.nonVeg: 0},
            }

        data_map[date][slot][mtype] = count

    response: list[MealCountResponse] = []

    for date in sorted(data_map.keys()):
        slot_map = data_map[date]

        def build(slot):
            c = slot_map.get(slot, {})
            return MealSlotCount(
                veg_count= c.get(MealType.veg, 0),
                non_veg_count=c.get(MealType.nonVeg, 0),
            )

        response.append(
            MealCountResponse(
                date=date,
                day=date.strftime("%A").lower(),
                breakfast=build(MealSlot.breakfast),
                lunch=build(MealSlot.lunch),
                dinner=build(MealSlot.dinner),
            )
        )

    return response