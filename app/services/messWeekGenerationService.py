from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from fastapi import HTTPException
from app.models.mess.messWeekModel import MessWeek
from app.utils.menuWeek import MenuWeek
from uuid import UUID
import uuid

from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def get_sunday_of_week(start_date: date) -> date:
    days_until_sunday = (6 - start_date.weekday()) % 7
    return start_date + timedelta(days=days_until_sunday)


async def generate_weeks_for_mess(
    db: AsyncSession,
    mess_id: UUID,
    college_id: UUID,
    mess_open_date: date,
    years_ahead: int = 1
) -> None:

    end_date_limit = mess_open_date + timedelta(days=365 * years_ahead)

    rows = []
    current_start = mess_open_date

    while current_start < end_date_limit:
        week_end = get_sunday_of_week(current_start)

        rows.append({
            "id": uuid.uuid4(),
            "mess_id": mess_id,
            "college_id": college_id,
            "start_date": current_start,
            "end_date": week_end
        })

        # next week starts day after Sunday
        current_start = week_end + timedelta(days=1)

    if rows:
        insert_weeks = insert(MessWeek).values(rows)
        insert_weeks = insert_weeks.on_conflict_do_nothing(
            index_elements=["mess_id", "start_date"]
        )
        await db.execute(insert_weeks)
        await db.commit()


# async def resolve_week(
#     db: AsyncSession,
#     menu_week: MenuWeek,
#     mess_id: UUID,
#     college_id: UUID,
# ):
#     today = datetime.now(IST).date()   # ✅ FIXED
#
#     if menu_week == MenuWeek.currentWeek:
#         result = await db.execute(
#             select(MessWeek).filter(
#                 MessWeek.mess_id == mess_id,
#                 MessWeek.college_id == college_id,
#                 MessWeek.start_date <= today,
#                 MessWeek.end_date >= today
#             )
#         )
#
#     else:  # nextWeek
#         result = await db.execute(
#             select(MessWeek).filter(
#                 MessWeek.mess_id == mess_id,
#                 MessWeek.college_id == college_id,
#                 MessWeek.start_date > today   # ✅ FIXED (strictly next)
#             )
#             .order_by(MessWeek.start_date.asc())
#             .limit(1)
#         )
#
#     week = result.scalar_one_or_none()
#
#     if not week:
#         raise HTTPException(
#             404,
#             f"No mess week found for {menu_week.value}. Weeks may not be configured yet."
#         )
#
#     return week.id

