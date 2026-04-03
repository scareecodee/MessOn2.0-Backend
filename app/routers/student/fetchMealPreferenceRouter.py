from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import asyncio
from app.db.session import get_db
from app.models.user.userModel import User
from app.models.student.studentModel import Student
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.messMenuModel import Menu
from app.models.mess.mealDayPolicy import MessDayPolicy
from app.schemas.student.mealPreferenceResponse import MealPreferenceResponse
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek
from app.utils.mealType import MealType
from app.services.weekResolverService import resolve_week
from app.services.getLatestDayPolicy import get_latest_policy_week
from app.services.getLatestMenuWeek import get_latest_menu_week

router = APIRouter(
    prefix="/fetch",
    tags=["Meal Preference"]
)


@router.get("/meal-preference/{menu_week}", response_model=List[MealPreferenceResponse])
async def get_meal_preference(
    menu_week: MenuWeek,
    current_user: User = Depends(get_current_role([UserRole.student,UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == UserRole.mess_admin:

        result = await db.execute(
            select(MessAdmin).filter(
                MessAdmin.user_id == current_user.id,
                MessAdmin.college_id == current_user.college_id
            )
        )
        mess_admin = result.scalar_one_or_none()

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

    menu_week_id = await get_latest_menu_week(db, mess_id, week.start_date)
    policy_week_id = await get_latest_policy_week(db, mess_id, week.start_date)

    menu_result, policy_result = await asyncio.gather(
        db.execute(
            select(Menu).filter(
                Menu.mess_id == mess_id,
                Menu.college_id == current_user.college_id,
                Menu.week_id == menu_week_id
            )
        ),
        db.execute(
            select(MessDayPolicy).filter(
                MessDayPolicy.mess_id == mess_id,
                MessDayPolicy.college_id == current_user.college_id,
                MessDayPolicy.week_id == policy_week_id
            )
        )
    )

    all_menus = menu_result.scalars().all()
    all_policies = policy_result.scalars().all()

    policy_map = {p.day: p.is_compulsory for p in all_policies}

    menu_map = {
        (m.day, m.meal_slot, m.meal_type): m.dishes
        for m in all_menus
    }

    slots = sorted(
        set((m.day, m.meal_slot) for m in all_menus),
        key=lambda x: (x[0].value, x[1].value)
    )

    response = [
        MealPreferenceResponse(
            day=day,
            meal_slot=meal_slot,
            veg_dishes=menu_map.get((day, meal_slot, MealType.veg)),
            nonVeg_dishes=menu_map.get((day, meal_slot, MealType.nonVeg)),
            is_compulsory=policy_map.get(day, False),
            veg_available=bool(menu_map.get((day, meal_slot, MealType.veg))),
            nonVeg_available=bool(menu_map.get((day, meal_slot, MealType.nonVeg)))
        )
        for day, meal_slot in slots
    ]

    return response