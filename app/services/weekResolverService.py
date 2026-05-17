# from fastapi import HTTPException
# from sqlalchemy import UUID
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from app.models.mess.messWeekModel import MessWeek
# from app.utils.menuWeek import MenuWeek
# from datetime import datetime
# from zoneinfo import ZoneInfo
#
# from app.services.messWeekGenerationService import generate_weeks_for_mess
#
# IST = ZoneInfo("Asia/Kolkata")
#
# async def resolve_week(
#     db: AsyncSession,
#     menu_week: MenuWeek,
#     mess_id: UUID,
#     college_id: UUID,
# ):
#     today = datetime.now(IST).date()
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
#         if not week:
#             await generate_weeks_for_mess(
#                 db=db,
#                 menu_week=menu_week,
#                 mess_id=mess_id,
#                 college_id=college_id,
#             )
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
#         if not week:
#             await generate_weeks_for_mess(
#                 db=db,
#                 menu_week=menu_week,
#                 mess_id=mess_id,
#                 college_id=college_id,
#             )
#
#     return week
#
# async def get_week_by_id(
#     db: AsyncSession,
#     week_id: UUID
# ) -> MessWeek:
#     result = await db.execute(
#         select(MessWeek).filter(MessWeek.id == week_id)
#     )
#     week = result.scalar_one_or_none()
#
#     if not week:
#         raise HTTPException(404, "Mess week not found")
#
#     return week

# app/services/weekResolverService.py

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mess.messWeekModel import MessWeek
from app.services.messWeekGenerationService import generate_weeks_for_mess
from app.utils.menuWeek import MenuWeek

IST = ZoneInfo("Asia/Kolkata")


async def resolve_week(
    db: AsyncSession,
    menu_week: MenuWeek,
    mess_id,
    college_id,
):

    today = datetime.now(IST).date()

    if menu_week == MenuWeek.currentWeek:

        stmt = (
            select(MessWeek)
            .where(
                MessWeek.mess_id == mess_id,
                MessWeek.college_id == college_id,
                MessWeek.start_date <= today,
                MessWeek.end_date >= today
            )
            .order_by(MessWeek.start_date.asc())
            .limit(1)
        )

    else:

        stmt = (
            select(MessWeek)
            .where(
                MessWeek.mess_id == mess_id,
                MessWeek.college_id == college_id,
                MessWeek.start_date > today
            )
            .order_by(MessWeek.start_date.asc())
            .limit(1)
        )

    result = await db.execute(stmt)

    week = result.scalar_one_or_none()

    if week is None:

        await generate_weeks_for_mess(
            db=db,
            mess_id=mess_id,
            college_id=college_id,
        )

        result = await db.execute(stmt)

        week = result.scalar_one_or_none()

    if week is None:
        raise HTTPException(
            status_code=500,
            detail="Unable to resolve or generate mess week"
        )

    return week