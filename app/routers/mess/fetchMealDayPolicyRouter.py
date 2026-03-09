from fastapi import APIRouter, Depends, HTTPException, status,responses
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek
from app.models.mess.mealDayPolicy import MessDayPolicy
from app.models.mess.messAdmin import MessAdmin
from app.schemas.mess.dayPolicyResponse import DayPolicyResponse

router = APIRouter(
    prefix="/fetch/messes",
    tags=["Mess Admin"]
)

@router.get(
    "/day-policy/{menu_week}",
    response_model=List[DayPolicyResponse]
)
def get_day_policy(
    menu_week: MenuWeek,
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: Session = Depends(get_db),
):

    mess_admin = db.query(MessAdmin).filter(
        MessAdmin.user_id == current_user.id,
        MessAdmin.college_id == current_user.college_id
    ).first()

    if not mess_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mess admin not assigned to any mess"
        )

    policies = db.query(MessDayPolicy).filter(
        MessDayPolicy.college_id == current_user.college_id,
        MessDayPolicy.mess_id == mess_admin.mess_id,
        MessDayPolicy.menu_week == menu_week
    ).order_by(MessDayPolicy.day).all()

    return policies