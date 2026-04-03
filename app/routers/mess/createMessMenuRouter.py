from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.db.session import get_db
from app.utils.mealSlot import MealSlot
from app.schemas.mess.createMenu import CreateMenu
from app.schemas.mess.menuResponse import MenuResponse
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.models.mess.messMenuModel import Menu
from app.utils.menuWeek import MenuWeek
from app.utils.weekDays import WeekDays
from app.services.weekResolverService import resolve_week

from app.models.mess.messModel import Mess

router = APIRouter(
    prefix="/messes",
    tags=["Manage Mess Menu"]
)
@router.patch("/menus/{menu_week}", response_model=List[MenuResponse])
async def upsert_menus(
    menu_week: MenuWeek,
    payload: List[CreateMenu],
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MessAdmin).filter(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        )
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(404, "Mess admin not found")

    week = await resolve_week(
        db,
        menu_week,
        admin.mess_id,
        current_user.college_id
    )

    result = await db.execute(
        select(Menu).filter(
            Menu.mess_id == admin.mess_id,
            Menu.college_id == current_user.college_id,
            Menu.week_id == week.id   # ✅ FIXED
        )
    )
    existing_menus = result.scalars().all()

    existing_map = {
        (m.day, m.meal_slot, m.meal_type): m
        for m in existing_menus
    }

    response = []

    for item in payload:
        key = (item.day, item.meal_slot, item.meal_type)

        menu_obj = existing_map.get(key)

        if menu_obj:
            menu_obj.dishes = item.dishes
        else:
            menu_obj = Menu(
                mess_id=admin.mess_id,
                college_id=current_user.college_id,
                week_id=week.id,
                day=item.day,
                meal_slot=item.meal_slot,
                meal_type=item.meal_type,
                dishes=item.dishes,
            )
            db.add(menu_obj)

    await db.commit()

    result = await db.execute(
        select(Menu).filter(
            Menu.mess_id == admin.mess_id,
            Menu.college_id == current_user.college_id,
            Menu.week_id == week.id
        ).order_by(
            Menu.day,
            Menu.meal_slot,
            Menu.meal_type
        )
    )

    menus = result.scalars().all()

    response = [
        MenuResponse(
            # menu_id=menu.id,
            day=WeekDays(menu.day),
            meal_slot=MealSlot(menu.meal_slot),
            meal_type=menu.meal_type,
            dishes=menu.dishes,
            # menu_week=menu.menu_week
        )
        for menu in menus
    ]

    return response