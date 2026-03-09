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
from app.models.mess.mealDayPolicy import MessDayPolicy

router = APIRouter(
    prefix="/messes",
    tags=["Mess Admin"]
)


@router.post("/{mess_id}/day-policy/{menu_week}")
def upsert_day_policy(
    mess_id: UUID,
    menu_week: MenuWeek,
    payload: List[CreateDayPolicy],
    current_admin: User = Depends(get_current_role(UserRole.mess_admin)),
    db: Session = Depends(get_db),
):

    existing = db.query(MessDayPolicy).filter(
        MessDayPolicy.college_id == current_admin.college_id,
        MessDayPolicy.mess_id == mess_id,
        MessDayPolicy.menu_week == menu_week
    ).all()

    existing_map = {
        policy.day: policy
        for policy in existing
    }

    for item in payload:

        existing_policy = existing_map.get(item.day)

        if existing_policy:
            existing_policy.is_compulsory = item.is_compulsory

        else:
            new_policy = MessDayPolicy(
                mess_id=mess_id,
                college_id=current_admin.college_id,
                day=item.day,
                menu_week=menu_week,
                is_compulsory=item.is_compulsory
            )

            db.add(new_policy)

    db.commit()

    return HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Mess Day Policy created successfully",
    )