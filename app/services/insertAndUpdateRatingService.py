from sqlalchemy import text

async def insert_rating(
    db,
    student_id,
    date,
    meal_slot,
    rating
):

    stmt = text("""
        INSERT INTO ratings (
            student_id,
            date,
            meal_slot,
            meal_type,
            rating,
            mess_id,
            college_id,
            created_at,
            updated_at
        )
        SELECT
            c.student_id,
            c.date,
            c.meal_slot,
            c.meal_type,
            :rating,
            c.mess_id,
            c.college_id,
            NOW(),
            NOW()
        FROM coupons c
        WHERE c.student_id = :student_id
        AND c.date = :date
        AND c.meal_slot = :meal_slot
        AND c.scanned_at IS NULL
        LIMIT 1

        ON CONFLICT (student_id, date, meal_slot, meal_type)
        DO NOTHING

        RETURNING
            id,
            mess_id,
            college_id,
            meal_type
    """)

    result = await db.execute(stmt, {
        "student_id": student_id,
        "date": date,
        "meal_slot": meal_slot,
        "rating": rating
    })

    row = result.first()

    if not row:
        return None
    

    return {
        "rating_id": row.id,
        "mess_id": row.mess_id,
        "college_id": row.college_id,
        "meal_type": row.meal_type
    }


async def update_summary_logic(
    db,
    mess_id,
    college_id,
    date,
    meal_slot,
    meal_type,
    rating
):

    stmt = text("""
        INSERT INTO rating_analytics (
            mess_id,
            college_id,
            date,
            meal_slot,
            veg_sum,
            veg_count,
            non_veg_sum,
            non_veg_count,
            total_sum,
            total_count,
            created_at,
            updated_at
        )
        VALUES (
            :mess_id,
            :college_id,
            :date,
            :meal_slot,

            CASE WHEN :meal_type = 'veg' THEN :rating ELSE 0 END,
            CASE WHEN :meal_type = 'veg' THEN 1 ELSE 0 END,

            CASE WHEN :meal_type = 'non_veg' THEN :rating ELSE 0 END,
            CASE WHEN :meal_type = 'non_veg' THEN 1 ELSE 0 END,

            :rating,
            1,
            NOW(),
            NOW()
        )

        ON CONFLICT (mess_id, date, meal_slot)
        DO UPDATE SET

            veg_sum = rating_analytics.veg_sum + EXCLUDED.veg_sum,
            veg_count = rating_analytics.veg_count + EXCLUDED.veg_count,

            non_veg_sum = rating_analytics.non_veg_sum + EXCLUDED.non_veg_sum,
            non_veg_count = rating_analytics.non_veg_count + EXCLUDED.non_veg_count,

            total_sum = rating_analytics.total_sum + EXCLUDED.total_sum,
            total_count = rating_analytics.total_count + EXCLUDED.total_count,

            updated_at = NOW()
    """)

    result = await db.execute(stmt, {
        "mess_id": mess_id,
        "college_id": college_id,
        "date": date,
        "meal_slot": meal_slot,
        "meal_type": meal_type,
        "rating": rating
    })
