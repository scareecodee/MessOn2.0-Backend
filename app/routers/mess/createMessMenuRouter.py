from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db.session import get_db
from app.utils.mealType import MealType
from app.utils.mealSlot import MealSlot
from app.schemas.mess.createMenu import CreateMenu
from app.schemas.mess.menuResponse import MenuResponse
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.models.mess.messMenuModel import Menu
from app.utils.menuWeek import MenuWeek
from app.utils.weekDay import WeekDay
from app.models.mess.messModel import Mess

router = APIRouter(
    prefix="/messes",
    tags=["Mess Admin"]
)

@router.patch("/menus/{menu_week}", response_model=List[MenuResponse])
def upsert_menus(
    menu_week: MenuWeek,
    payload: List[CreateMenu],
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: Session = Depends(get_db),
):

    # print(payload)


    mess_admin = db.query(MessAdmin).filter(
        MessAdmin.user_id==current_user.id,
        MessAdmin.college_id == current_user.college_id
    ).first()

    mess = (
        db.query(Mess)
        .filter(
            Mess.id == mess_admin.mess_id,
            Mess.college_id == current_user.college_id
        )
        .first()
    )

    if not mess:
        raise HTTPException(
            status_code=404,
            detail="Mess not found or not accessible"
        )

    # -------- SINGLE QUERY --------
    existing_menus = db.query(Menu).filter(
        Menu.mess_id == mess_admin.mess_id,
        Menu.college_id == current_user.college_id,
        Menu.menu_week == menu_week
    ).all()

    # -------- BUILD LOOKUP MAP --------
    existing_map = {
        (
            m.day,
            m.meal_slot,
            m.meal_type
        ): m
        for m in existing_menus
    }

    result = []

    for item in payload:

        key = (
            item.day,
            item.meal_slot,
            item.meal_type
        )

        menu_obj = existing_map.get(key)

        if menu_obj:
            # UPDATE
            menu_obj.dishes = item.dishes

        else:
            # INSERT
            menu_obj = Menu(
                mess_id=mess_admin.mess_id,
                college_id=current_user.college_id,
                day=item.day,
                meal_slot=item.meal_slot,
                meal_type=item.meal_type,
                dishes=item.dishes,
                menu_week=menu_week
            )

            db.add(menu_obj)
            db.flush()

        result.append(
            MenuResponse(
                # menu_id=UUID(str(menu_obj.id)),
                day=WeekDay(menu_obj.day),
                meal_slot=MealSlot(menu_obj.meal_slot),
                meal_type=menu_obj.meal_type,
                dishes=menu_obj.dishes,
                # menu_week=menu_week
            )
        )

    db.commit()

    return result
