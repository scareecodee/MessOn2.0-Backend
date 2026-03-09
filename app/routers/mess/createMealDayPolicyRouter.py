from fastapi import APIRouter, Depends, HTTPException, status,responses
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db.session import get_db
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek
from app.schemas.mess.createDayPolicy import CreateDayPolicy
from app.schemas.mess.dayPolicyResponse import DayPolicyResponse
from app.models.mess.mealDayPolicy import MessDayPolicy
from app.models.mess.messAdmin import MessAdmin

router = APIRouter(
    prefix="/messes",
    tags=["Mess Admin"]
)

@router.patch(
    "/day-policy/{menu_week}",
    response_model=List[DayPolicyResponse]
)
def upsert_day_policy(
    menu_week: MenuWeek,
    payload: List[CreateDayPolicy],
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: Session = Depends(get_db),
):

    mess_admin = db.query(MessAdmin).filter(
        MessAdmin.user_id == current_user.id,
        MessAdmin.college_id == current_user.college_id
    ).first()

    existing = db.query(MessDayPolicy).filter(
        MessDayPolicy.college_id == current_user.college_id,
        MessDayPolicy.mess_id == mess_admin.mess_id,
        MessDayPolicy.menu_week == menu_week
    ).all()

    existing_map = {policy.day: policy for policy in existing}

    result = []

    for item in payload:

        existing_policy = existing_map.get(item.day)

        if existing_policy:
            existing_policy.is_compulsory = item.is_compulsory
            policy = existing_policy

        else:
            policy = MessDayPolicy(
                mess_id=mess_admin.mess_id,
                college_id=current_user.college_id,
                day=item.day,
                menu_week=menu_week,
                is_compulsory=item.is_compulsory
            )
            db.add(policy)
            db.flush()

        result.append(policy)

    db.commit()

    return result