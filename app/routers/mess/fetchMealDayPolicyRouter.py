# from fastapi import APIRouter, Depends, HTTPException, status, responses
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from typing import List
# from app.db.session import get_db
# from app.models.user.userModel import User
# from app.security.dependencies.getCurrentRole import get_current_role
# from app.utils.userRole import UserRole
# from app.utils.menuWeek import MenuWeek
# from app.models.mess.mealDayPolicy import MessDayPolicy
# from app.models.mess.messAdmin import MessAdmin
# from app.schemas.mess.dayPolicyResponse import DayPolicyResponse
# from app.services.weekResolverService import resolve_week
# from app.models.mess.messWeekModel import MessWeek
#
# router = APIRouter(
#     prefix="/fetch/messes",
#     tags=["Manage Mess Day Policy"]
# )
#
# @router.get(
#     "/day-policy/{menu_week}",
#     response_model=List[DayPolicyResponse]
# )
# async def get_day_policy(
#     menu_week: MenuWeek,
#     current_user: User = Depends(get_current_role([UserRole.mess_admin])),
#     db: AsyncSession = Depends(get_db),
# ):
#     result = await db.execute(
#         select(MessAdmin).filter(
#             MessAdmin.user_id == current_user.id,
#             MessAdmin.college_id == current_user.college_id,
#         )
#     )
#     mess_admin = result.scalar_one_or_none()
#
#     if not mess_admin:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Mess admin not assigned to any mess"
#         )
#
#     week = await resolve_week(
#         db,
#         menu_week,
#         mess_admin.mess_id,
#         current_user.college_id
#     )
#
#     target_date = week.start_date
#
#     effective_week_subq = (
#         select(MessWeek.id)
#         .join(MessDayPolicy, MessDayPolicy.week_id == MessWeek.id)
#         .where(
#             MessDayPolicy.college_id == current_user.college_id,
#             MessDayPolicy.mess_id == mess_admin.mess_id,
#             MessWeek.start_date <= target_date
#         )
#         .order_by(MessWeek.start_date.desc())
#         .limit(1)
#         .scalar_subquery()
#     )
#
#     result = await db.execute(
#         select(MessDayPolicy).filter(
#             MessDayPolicy.college_id == current_user.college_id,
#             MessDayPolicy.mess_id == mess_admin.mess_id,
#             MessDayPolicy.week_id == effective_week_subq
#         ).order_by(MessDayPolicy.day)
#     )
#
#     policies = result.scalars().all()
#
#     if not policies:
#         raise HTTPException(status_code=404, detail="No day policy found")
#
#     return policies



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.session import get_db

from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.mealDayPolicy import MessDayPolicy

from app.schemas.mess.dayPolicyResponse import DayPolicyResponse

from app.security.dependencies.getCurrentRole import get_current_role

from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek
from app.utils.weekDays import WeekDays

from app.services.weekResolverService import resolve_week
from app.services.getLatestDayPolicy import get_latest_policy_week

router = APIRouter(
    prefix="/fetch/messes",
    tags=["Manage Mess Day Policy"]
)

ALL_DAYS = list(WeekDays)


@router.get(
    "/day-policy/{menu_week}",
    response_model=List[DayPolicyResponse]
)
async def get_day_policy(
    menu_week: MenuWeek,
    current_user: User = Depends(
        get_current_role([UserRole.mess_admin])
    ),
    db: AsyncSession = Depends(get_db),
):


    result = await db.execute(
        select(MessAdmin).where(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id,
        )
    )

    mess_admin = result.scalar_one_or_none()

    if not mess_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mess admin not assigned to any mess"
        )

    week = await resolve_week(
        db=db,
        menu_week=menu_week,
        mess_id=mess_admin.mess_id,
        college_id=current_user.college_id
    )



    policy_week_id = await get_latest_policy_week(
        db,
        mess_admin.mess_id,
        week.start_date
    )

    policies = []

    if policy_week_id:

        result = await db.execute(
            select(MessDayPolicy).where(
                MessDayPolicy.college_id == current_user.college_id,
                MessDayPolicy.mess_id == mess_admin.mess_id,
                MessDayPolicy.week_id == policy_week_id
            )
        )

        policies = result.scalars().all()


    policy_map = {
        p.day: p.is_compulsory
        for p in policies
    }



    response = []

    for day in ALL_DAYS:

        response.append(
            DayPolicyResponse(
                day=day,
                is_compulsory=policy_map.get(day, False)
            )
        )

    return response