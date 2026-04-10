from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ALL_STUDENTS_BILL = """
# WITH valid_coupons AS (
#     SELECT DISTINCT
#         c.student_id,
#         c.date
#     FROM coupons c
#    WHERE c.date BETWEEN :start_date AND :end_date
#    AND c.mess_id = :mess_id
#    AND c.college_id = :college_id
#
#     AND NOT EXISTS (
#         SELECT 1 FROM mess_closures mc
#         WHERE mc.mess_id = c.mess_id
#         AND c.date BETWEEN mc.start_date AND COALESCE(mc.end_date, 'infinity')
#     )
# ),
#
# price_join AS (
#     SELECT
#         vc.student_id,
#         vc.date,
#         mp.per_day_price
#     FROM valid_coupons vc
#
#     JOIN meal_price_config mp
# ON mp.mess_id = :mess_id
# AND mp.college_id = :college_id
# AND mp.start_date = (
#     SELECT COALESCE(
#         (
#             SELECT MAX(start_date)
#             FROM meal_price_config mp2
#             WHERE mp2.mess_id = mp.mess_id
#             AND mp2.college_id = mp.college_id
#             AND mp2.start_date <= vc.date
#         ),
#         (
#             SELECT MIN(start_date)
#             FROM meal_price_config mp3
#             WHERE mp3.mess_id = mp.mess_id
#             AND mp3.college_id = mp.college_id
#         )
#     )
# )
#
#     WHERE mp.mess_id = :mess_id
#     AND mp.college_id = :college_id
# ),
#
# aggregated AS (
#     SELECT
#         student_id,
#         per_day_price,
#         COUNT(*) AS total_days
#     FROM price_join
#     GROUP BY student_id, per_day_price
# )
#
# SELECT
#     s.user_id,
#     u.name,
#     u.email,
#     s.roll_number,
#     s.branch,
#     s.batch,
#     COALESCE(SUM(a.total_days), 0) AS total_days,
#     COALESCE(SUM(a.total_days * a.per_day_price), 0) AS total_bill
#
# FROM students s
#
# JOIN users u ON u.id = s.user_id AND u.is_active = true
#
# LEFT JOIN aggregated a ON a.student_id = s.user_id
#
# WHERE s.mess_id = :mess_id
# AND s.college_id = :college_id
#
# GROUP BY s.user_id, u.name, u.email, s.roll_number, s.branch, s.batch
# ORDER BY s.roll_number;
#
# """


ALL_STUDENTS_BILL = """
WITH valid_coupons AS (
    SELECT DISTINCT
        c.student_id,
        c.date
    FROM coupons c
    WHERE c.date BETWEEN :start_date AND :end_date
    AND c.mess_id = :mess_id
    AND c.college_id = :college_id
    {student_filter}

    AND NOT EXISTS (
        SELECT 1 FROM mess_closures mc
        WHERE mc.mess_id = c.mess_id
        AND c.date BETWEEN mc.start_date AND COALESCE(mc.end_date, 'infinity')
    )
),

price_join AS (
    SELECT
        vc.student_id,
        vc.date,
        mp.per_day_price
    FROM valid_coupons vc

    JOIN LATERAL (
        SELECT mp1.per_day_price
        FROM meal_price_config mp1
        WHERE mp1.mess_id = :mess_id
        AND mp1.college_id = :college_id
        AND mp1.start_date <= vc.date
        ORDER BY mp1.start_date DESC
        LIMIT 1
    ) mp ON TRUE

    UNION ALL

    SELECT
        vc.student_id,
        vc.date,
        mp2.per_day_price
    FROM valid_coupons vc

    JOIN LATERAL (
        SELECT mp2.per_day_price
        FROM meal_price_config mp2
        WHERE mp2.mess_id = :mess_id
        AND mp2.college_id = :college_id
        ORDER BY mp2.start_date ASC
        LIMIT 1
    ) mp2 ON TRUE

    WHERE NOT EXISTS (
        SELECT 1
        FROM meal_price_config mp3
        WHERE mp3.mess_id = :mess_id
        AND mp3.college_id = :college_id
        AND mp3.start_date <= vc.date
    )
),

aggregated AS (
    SELECT
        student_id,
        per_day_price,
        COUNT(*) AS total_days
    FROM price_join
    GROUP BY student_id, per_day_price
)

SELECT
    s.user_id,
    u.name,
    u.email,
    s.roll_number,
    s.branch,
    s.batch,
    COALESCE(SUM(a.total_days), 0) AS total_days,
    COALESCE(SUM(a.total_days * a.per_day_price), 0) AS total_bill

FROM students s

JOIN users u 
    ON u.id = s.user_id 
    AND u.is_active = true

LEFT JOIN aggregated a 
    ON a.student_id = s.user_id

WHERE s.mess_id = :mess_id
AND s.college_id = :college_id
{student_filter_outer}

GROUP BY s.user_id, u.name, u.email, s.roll_number, s.branch, s.batch
ORDER BY s.roll_number
"""


STUDENT_DETAILED_BILL_HISTORY = """

SELECT
    c.student_id,
    c.date,

    MAX(CASE WHEN c.meal_slot = 'breakfast' THEN c.meal_type END) AS breakfast_type,
    MAX(CASE 
        WHEN c.meal_slot = 'breakfast' THEN
            CASE
                WHEN c.scanned_at IS NOT NULL THEN 'consumed'
                ELSE 'not_consumed'
            END
    END) AS breakfast_status,

    MAX(CASE WHEN c.meal_slot = 'lunch' THEN c.meal_type END) AS lunch_type,
    MAX(CASE 
        WHEN c.meal_slot = 'lunch' THEN
            CASE
                WHEN c.scanned_at IS NOT NULL THEN 'consumed'
                ELSE 'not_consumed'
            END
    END) AS lunch_status,

    MAX(CASE WHEN c.meal_slot = 'dinner' THEN c.meal_type END) AS dinner_type,
    MAX(CASE 
        WHEN c.meal_slot = 'dinner' THEN
            CASE
                WHEN c.scanned_at IS NOT NULL THEN 'consumed'
                ELSE 'not_consumed'
            END
    END) AS dinner_status

FROM coupons c

WHERE c.student_id = :student_id
AND c.mess_id = :mess_id
AND c.college_id = :college_id
AND c.date BETWEEN :start_date AND :end_date

AND NOT EXISTS (
    SELECT 1 FROM mess_closures mc
    WHERE mc.mess_id = c.mess_id
    AND c.date BETWEEN mc.start_date AND COALESCE(mc.end_date, 'infinity')
)

GROUP BY c.student_id, c.date
ORDER BY c.date;
"""

