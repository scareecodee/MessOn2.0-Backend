from sqlalchemy import text


async def get_latest_preference_week(
    db,
    mess_id,
    current_week_start
):
    result = await db.execute(
        text("""
            SELECT mw.id
            FROM mess_weeks mw
            WHERE EXISTS (
                SELECT 1
                FROM meal_preferences mp
                WHERE mp.week_id = mw.id
                  AND mp.mess_id = :mess_id
            )
              AND mw.start_date <= :current_week_start
            ORDER BY mw.start_date DESC
            LIMIT 1
        """),
        {
            "mess_id": mess_id,
            "current_week_start": current_week_start
        }
    )

    return result.scalar()