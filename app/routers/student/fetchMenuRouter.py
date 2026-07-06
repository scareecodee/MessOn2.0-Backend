# from fastapi import APIRouter, Depends, HTTPException, status
# from typing import List
# from app.db.session import get_db
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from app.models.user.userModel import User
# from app.models.mess.messAdmin import MessAdmin
# from app.models.student.studentModel import Student
# from app.security.dependencies.getCurrentRole import get_current_role
# from app.utils.userRole import UserRole
# from app.models.mess.messMenuModel import Menu
# from app.schemas.mess.menuResponse import WeeklyMenuResponse, SlotMenu, DayMenu, MenuResponse
# from app.utils.menuWeek import MenuWeek
# from app.utils.weekDays import WeekDays
# from app.services.weekResolverService import resolve_week
# from app.models.mess.messWeekModel import MessWeek
#
# router = APIRouter(
#     prefix="/fetch",
#     tags=["Manage Mess Menu"]
# )
#
# @router.get(
#     "/menus/{menu_week}",
#     response_model=List[MenuResponse]
# )
# async def get_week_menu(
#     menu_week: MenuWeek,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(
#         get_current_role([
#             UserRole.mess_admin,
#             UserRole.student
#         ])
#     ),
# ):
#     if current_user.role == UserRole.mess_admin:
#
#         result = await db.execute(
#             select(MessAdmin).filter(
#                 MessAdmin.user_id == current_user.id,
#                 MessAdmin.college_id == current_user.college_id
#             )
#         )
#         mess_admin = result.scalar_one_or_none()
#
#         if not mess_admin:
#             raise HTTPException(status_code=404, detail="Mess admin profile not found")
#
#         mess_id = mess_admin.mess_id
#
#     else:
#
#         result = await db.execute(
#             select(Student).filter(
#                 Student.user_id == current_user.id,
#                 Student.college_id == current_user.college_id
#             )
#         )
#         student = result.scalar_one_or_none()
#
#         if not student:
#             raise HTTPException(status_code=404, detail="Student profile not found")
#
#         mess_id = student.mess_id
#
#     week = await resolve_week(
#         db,
#         menu_week,
#         mess_id,
#         current_user.college_id
#     )
#
#     target_date = week.start_date
#
#     effective_week_subq = (
#         select(MessWeek.id)
#         .join(Menu, Menu.week_id == MessWeek.id)
#         .where(
#             Menu.college_id == current_user.college_id,
#             Menu.mess_id == mess_id,
#             MessWeek.start_date <= target_date
#         )
#         .order_by(MessWeek.start_date.desc())
#         .limit(1)
#         .scalar_subquery()
#     )
#
#     result = await db.execute(
#         select(Menu).filter(
#             Menu.college_id == current_user.college_id,
#             Menu.mess_id == mess_id,
#             Menu.week_id == effective_week_subq   # 🔥 FIXED
#         ).order_by(
#             Menu.day,
#             Menu.meal_slot,
#             Menu.meal_type
#         )
#     )
#
#     menus = result.scalars().all()
#
#     if not menus:
#         raise HTTPException(status_code=404, detail="No menu found")
#
#     response = [
#         MenuResponse(
#             # menu_id=menu.id,
#             day=menu.day,
#             meal_slot=menu.meal_slot,
#             meal_type=menu.meal_type,
#             dishes=menu.dishes,
#             # menu_week=menu.menu_week
#         )
#         for menu in menus
#     ]
#
#     return response

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db

from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.student.studentModel import Student
from app.models.mess.messMenuModel import Menu
from app.models.mess.messWeekModel import MessWeek

from app.schemas.mess.menuResponse import MenuResponse

from app.security.dependencies.getCurrentRole import get_current_role

from app.services.weekResolverService import resolve_week

from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek
from app.utils.weekDays import WeekDays
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType

router = APIRouter(
    prefix="/fetch",
    tags=["Manage Mess Menu"]
)


ALL_DAYS = list(WeekDays)
ALL_SLOTS = list(MealSlot)
ALL_TYPES = list(MealType)


@router.get(
    "/menus/{menu_week}",
    response_model=List[MenuResponse]
)
async def get_week_menu(
    menu_week: MenuWeek,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_role([
            UserRole.mess_admin,
            UserRole.student
        ])
    ),
):



    if current_user.role == UserRole.mess_admin:

        result = await db.execute(
            select(MessAdmin).where(
                MessAdmin.user_id == current_user.id,
                MessAdmin.college_id == current_user.college_id
            )
        )

        mess_admin = result.scalar_one_or_none()

        if not mess_admin:
            raise HTTPException(
                status_code=404,
                detail="Mess admin profile not found"
            )

        mess_id = mess_admin.mess_id

    else:

        result = await db.execute(
            select(Student).where(
                Student.user_id == current_user.id,
                Student.college_id == current_user.college_id
            )
        )

        student = result.scalar_one_or_none()

        if not student:
            raise HTTPException(
                status_code=404,
                detail="Student profile not found"
            )

        mess_id = student.mess_id


    week = await resolve_week(
        db=db,
        menu_week=menu_week,
        mess_id=mess_id,
        college_id=current_user.college_id
    )

    target_date = week.start_date


    effective_week_subq = (
        select(MessWeek.id)
        .join(Menu, Menu.week_id == MessWeek.id)
        .where(
            MessWeek.mess_id == mess_id,
            MessWeek.college_id == current_user.college_id,
            MessWeek.start_date <= target_date,
            Menu.mess_id == mess_id,
            Menu.college_id == current_user.college_id
        )
        .order_by(MessWeek.start_date.desc())
        .limit(1)
        .scalar_subquery()
    )

    # ---------------------------------------------------
    # Fetch menu rows
    # ---------------------------------------------------

    result = await db.execute(
        select(Menu).where(
            Menu.college_id == current_user.college_id,
            Menu.mess_id == mess_id,
            Menu.week_id == effective_week_subq
        )
    )

    menus = result.scalars().all()


    menu_lookup = {
        (menu.day, menu.meal_slot, menu.meal_type): menu
        for menu in menus
    }


    response = []

    for day in ALL_DAYS:
        for slot in ALL_SLOTS:
            for meal_type in ALL_TYPES:

                menu = menu_lookup.get(
                    (day, slot, meal_type)
                )

                dishes = menu.dishes if menu is not None else None

                response.append(
                    MenuResponse(
                        day=day,
                        meal_slot=slot,
                        meal_type=meal_type,
                        dishes=dishes
                    )
                )

    return response