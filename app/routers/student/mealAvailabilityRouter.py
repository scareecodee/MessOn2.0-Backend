from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.mess.mealAvailability import MealAvailability
from app.models.user.userModel import User
from app.db.session import get_db
from app.models.student.studentModel import Student

from app.models.mess.messMenuModel import Menu
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.mealType import MealType
from app.utils.menuWeek import MenuWeek
from app.utils.userRole import UserRole
from app.models.mess.messAdmin import MessAdmin
from app.services.weekResolverService import resolve_week

router=APIRouter(
    prefix="/fetch",
    tags=["Meal Availability"],
)

@router.get(
"/meal-availability/{menu_week}",
response_model=list[MealAvailability]
)
async def get_meal_availability(
    menu_week:MenuWeek,
    current_user:User=Depends(get_current_role(
        [UserRole.student,UserRole.mess_admin])),
    db:AsyncSession=Depends(get_db)
):

    if current_user.role == UserRole.mess_admin:

        mess_admins = await db.execute(
            select(MessAdmin).filter(
                MessAdmin.user_id == current_user.id,
                MessAdmin.college_id == current_user.college_id
            )
        )
        mess_admin = mess_admins.scalar_one_or_none()

        if not mess_admin:
            raise HTTPException(status_code=404, detail="Mess admin profile not found")

        mess_id = mess_admin.mess_id

    else:

        result = await db.execute(
            select(Student).filter(
                Student.user_id == current_user.id,
                Student.college_id == current_user.college_id
            )
        )
        student = result.scalar_one_or_none()

        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        mess_id = student.mess_id

    week = await resolve_week(
        db,
        menu_week,
        mess_id,
        current_user.college_id
    )

    result = await db.execute(
        select(Menu)
        .where(
            Menu.mess_id ==mess_id,
            Menu.menu_week == menu_week
        )
    )

    menus = result.scalars().all()

    availability_map = {}

    for menu in menus:

        if not menu.dishes:
            continue

        key = (menu.day, menu.meal_slot)

        if key not in availability_map:
            availability_map[key] = {
                "day": menu.day,
                "meal_slot": menu.meal_slot,
                "veg_available": False,
                "nonVeg_available": False
            }

        if menu.meal_type == MealType.veg:
            availability_map[key]["veg_available"] = True

        if menu.meal_type == MealType.nonVeg:
            availability_map[key]["nonVeg_available"] = True

    return list(availability_map.values())