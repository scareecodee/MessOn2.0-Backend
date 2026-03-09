from fastapi import APIRouter, Depends,HTTPException,status
from typing import List
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.student.studentModel import Student
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.models.mess.messMenuModel import Menu
from app.schemas.mess.menuResponse import WeeklyMenuResponse,SlotMenu,DayMenu,MenuResponse
from app.utils.menuWeek import MenuWeek
from app.utils.weekDay import WeekDay

router = APIRouter(
    prefix="/fetch",
    tags=["Fetch Day-wise Menu"]
)

@router.get(
    "/menus/{menu_week}",
    response_model=List[MenuResponse]
)
def get_week_menu(
    menu_week: MenuWeek,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_role([
            UserRole.mess_admin,
            UserRole.student
        ])
    ),
):

    # resolve mess_id
    if current_user.role == UserRole.mess_admin:

        mess_admin = db.query(MessAdmin).filter(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        ).first()

        mess_id = mess_admin.mess_id

    else:  # student

        student = db.query(Student).filter(
            Student.user_id == current_user.id,
            Student.college_id == current_user.college_id
        ).first()

        mess_id = student.mess_id


    # fetch menus
    menus = db.query(Menu).filter(
        Menu.college_id == current_user.college_id,
        Menu.mess_id == mess_id,
        Menu.menu_week == menu_week
    ).order_by(
        Menu.day,
        Menu.meal_slot,
        Menu.meal_type
    ).all()


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