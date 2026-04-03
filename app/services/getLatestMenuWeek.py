from sqlalchemy import text

async def get_latest_menu_week(db, mess_id, current_week_start):
    result = await db.execute(
        text("""
            SELECT mw.id
            FROM mess_menu m
            JOIN mess_weeks mw ON mw.id = m.week_id
            WHERE m.mess_id = :mess_id
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