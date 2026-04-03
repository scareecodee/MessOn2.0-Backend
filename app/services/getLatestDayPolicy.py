from sqlalchemy import text


async def get_latest_policy_week(db, mess_id, current_week_start):
    result = await db.execute(
        text("""
            SELECT mw.id
            FROM mess_day_policies mdp
            JOIN mess_weeks mw ON mw.id = mdp.week_id
            WHERE mdp.mess_id = :mess_id
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