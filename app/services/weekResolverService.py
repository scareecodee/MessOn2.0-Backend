
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.mess.messWeekModel import MessWeek
from app.utils.menuWeek import MenuWeek


# async def resolve_week_id(
#     db: AsyncSession,
#     menu_week: MenuWeek,
#     mess_id,
#     college_id
# ):
#     today = datetime.utcnow().date()
#
#     # get current week's monday
#     start_of_week = today - timedelta(days=today.weekday())
#
#     if menu_week == MenuWeek.nextWeek:
#         start_of_week += timedelta(days=7)
#
#     result = await db.execute(
#         select(MessWeek).filter(
#             MessWeek.mess_id == mess_id,
#             MessWeek.college_id == college_id,
#             MessWeek.start_date == start_of_week
#         )
#     )
#
#     week = result.scalar_one_or_none()
#
#     if not week:
#         raise Exception("Week not found in DB")
#
#     return week.id, week.start_date
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

async def resolve_week(
    db: AsyncSession,
    menu_week: MenuWeek,
    mess_id: UUID,
    college_id: UUID,
):
    today = datetime.now(IST).date()

    if menu_week == MenuWeek.currentWeek:
        result = await db.execute(
            select(MessWeek).filter(
                MessWeek.mess_id == mess_id,
                MessWeek.college_id == college_id,
                MessWeek.start_date <= today,
                MessWeek.end_date >= today
            )
        )

    else:
        result = await db.execute(
            select(MessWeek).filter(
                MessWeek.mess_id == mess_id,
                MessWeek.college_id == college_id,
                MessWeek.start_date > today
            )
            .order_by(MessWeek.start_date.asc())
            .limit(1)
        )

    week = result.scalar_one_or_none()

    if not week:
        raise HTTPException(
            404,
            f"No mess week found for {menu_week.value}. Weeks may not be configured yet."
        )

    return week

async def get_week_by_id(
    db: AsyncSession,
    week_id: UUID
) -> MessWeek:
    result = await db.execute(
        select(MessWeek).filter(MessWeek.id == week_id)
    )
    week = result.scalar_one_or_none()

    if not week:
        raise HTTPException(404, "Mess week not found")

    return week