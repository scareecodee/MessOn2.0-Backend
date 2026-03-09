from fastapi import APIRouter, Depends,HTTPException,status
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user.userModel import User
from typing import List
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from uuid import UUID
from app.models.mess.messMenuModel import Menu
from app.schemas.mess.menuResponse import DayWiseMenuResponse, MenuResponse
from app.utils.menuWeek import MenuWeek
from app.utils.weekDay import WeekDay

router = APIRouter(
    prefix="/fetch",
    tags=["Fetch Day-wise Menu"]
)

@router.get(
    "/{mess_id}/menus/{menu_week}/{day}",
    response_model=DayWiseMenuResponse
)
def get_day_menu(
    mess_id: UUID,
    menu_week: MenuWeek,
    day: WeekDay,
    current_role: User = Depends(get_current_role(UserRole.mess_admin)),
    db: Session = Depends(get_db)
):

    menus = db.query(Menu).filter(
        Menu.college_id==current_role.college_id,
        Menu.mess_id == mess_id,
        Menu.menu_week == menu_week,
        Menu.day == day
    ).all()

    response = DayWiseMenuResponse()

    for menu in menus:
        slot_dict = getattr(response, menu.meal_slot.value)
        slot_dict[menu.meal_type.value] = MenuResponse(
            menu_id=menu.id,
            day=menu.day,
            meal_slot=menu.meal_slot,
            meal_type=menu.meal_type,
            dishes=menu.dishes,
            menu_week=menu.menu_week
        )

    return response