# from datetime import date, timedelta
#
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy.dialects.postgresql import insert
#
#
# from app.models.mess.messWeekModel import MessWeek
# from app.utils.menuWeek import MenuWeek
# from uuid import UUID
# import uuid
#
# from datetime import datetime
# from zoneinfo import ZoneInfo
#
# IST = ZoneInfo("Asia/Kolkata")
# today=datetime.now(IST).date()
#
#
# def get_sunday_of_week(start_date: date) -> date:
#     days_until_sunday = (6 - start_date.weekday()) % 7
#     return start_date + timedelta(days=days_until_sunday)
#
# async def generate_weeks_for_mess(
#     db: AsyncSession,
#     mess_id: UUID,
#     menu_week: MenuWeek,
#     college_id: UUID,
#     years_ahead: int = 1
# ) -> MessWeek:
#
#     print("No week found so creating new week")
#     end_date_limit = today + timedelta(days=30 * years_ahead)
#
#     rows = []
#     current_start = today
#
#     while current_start < end_date_limit:
#         week_end = get_sunday_of_week(current_start)
#
#         rows.append({
#             "id": uuid.uuid4(),
#             "mess_id": mess_id,
#             "college_id": college_id,
#             "start_date": current_start,
#             "end_date": week_end
#         })
#
#         # next week starts day after Sunday
#         current_start = week_end + timedelta(days=1)
#
#     if rows:
#         insert_weeks = insert(MessWeek).values(rows)
#         insert_weeks = insert_weeks.on_conflict_do_nothing(
#             index_elements=["mess_id", "start_date"]
#         )
#
#         weeks = await db.execute(insert_weeks)
#         db.add_all(weeks)
#         await db.flush([weeks])
#
#         await db.commit()
#
#
#     if menu_week == MenuWeek.currentWeek:
#         result = await db.execute(
#             select(MessWeek).filter(
#                 MessWeek.mess_id == mess_id,
#                 MessWeek.college_id == college_id,
#                 MessWeek.start_date <= today,
#                 MessWeek.end_date >= today
#             ).order_by(MessWeek.start_date.asc())
#             .limit(1)
#         )
#         week = result.scalar_one_or_none()
#
#     else:
#         result = await db.execute(
#             select(MessWeek).filter(
#                 MessWeek.mess_id == mess_id,
#                 MessWeek.college_id == college_id,
#                 MessWeek.start_date > today
#             )
#             .order_by(MessWeek.start_date.asc())
#             .limit(1)
#         )
#
#         week = result.scalar_one_or_none()
#
#     return week


# app/services/messWeekGenerationService.py

import uuid
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.mess.messWeekModel import MessWeek
from app.utils.menuWeek import MenuWeek

IST = ZoneInfo("Asia/Kolkata")


def get_start_of_week(current_date: date) -> date:
    return current_date - timedelta(days=current_date.weekday())


def get_end_of_week(start_date: date) -> date:
    return start_date + timedelta(days=6)


async def generate_weeks_for_mess(
    db: AsyncSession,
    mess_id,
    college_id,
    months_ahead: int = 1
):
    """
    Generates current + future calendar weeks.
    Weeks are ALWAYS Monday → Sunday.
    """

    today = datetime.now(IST).date()

    start_of_week = get_start_of_week(today)

    end_limit = start_of_week + timedelta(days=30 * months_ahead)

    rows = []

    current_start = start_of_week

    while current_start <= end_limit:

        current_end = get_end_of_week(current_start)

        rows.append({
            "id": uuid.uuid4(),
            "mess_id": mess_id,
            "college_id": college_id,
            "start_date": current_start,
            "end_date": current_end,
            "coupon_generation_status": "pending"
        })

        current_start += timedelta(days=7)

    if rows:
        stmt = insert(MessWeek).values(rows)

        stmt = stmt.on_conflict_do_nothing(
            index_elements=["mess_id", "start_date"]
        )

        await db.execute(stmt)
        await db.commit()