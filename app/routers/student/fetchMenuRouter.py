from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.student.studentModel import Student
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.models.mess.messMenuModel import Menu
from app.schemas.mess.menuResponse import WeeklyMenuResponse, SlotMenu, DayMenu, MenuResponse
from app.utils.menuWeek import MenuWeek
from app.utils.weekDays import WeekDays
from app.services.weekResolverService import resolve_week
from app.models.mess.messWeekModel import MessWeek

router = APIRouter(
    prefix="/fetch",
    tags=["Manage Mess Menu"]
)

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
    # resolve mess_id
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

    target_date = week.start_date   # 🔥 KEY

    effective_week_subq = (
        select(MessWeek.id)
        .join(Menu, Menu.week_id == MessWeek.id)
        .where(
            Menu.college_id == current_user.college_id,
            Menu.mess_id == mess_id,
            MessWeek.start_date <= target_date
        )
        .order_by(MessWeek.start_date.desc())
        .limit(1)
        .scalar_subquery()
    )

    result = await db.execute(
        select(Menu).filter(
            Menu.college_id == current_user.college_id,
            Menu.mess_id == mess_id,
            Menu.week_id == effective_week_subq   # 🔥 FIXED
        ).order_by(
            Menu.day,
            Menu.meal_slot,
            Menu.meal_type
        )
    )

    menus = result.scalars().all()

    if not menus:
        raise HTTPException(status_code=404, detail="No menu found")

    response = [
        MenuResponse(
            # menu_id=menu.id,
            day=menu.day,
            meal_slot=menu.meal_slot,
            meal_type=menu.meal_type,
            dishes=menu.dishes,
            # menu_week=menu.menu_week
        )
        for menu in menus
    ]

    return response