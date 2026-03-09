from uuid import UUID
from fastapi import APIRouter, Depends,HTTPException,status
from app.db.session import get_db
from app.models.mess.messModel import Mess
from app.models.user.userModel import User
from sqlalchemy.orm import Session
from app.schemas.mess.messResponse import MessResponse
from typing import List
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/admin/college",
    tags=["Manage Mess"]
)

@router.get("/messes", response_model=List[MessResponse])
def list_messes(
    current_user: User = Depends(get_current_role(UserRole.college_admin)),
    db: Session = Depends(get_db)
):

    messes = (
        db.query(Mess)
        .filter(
            Mess.college_id == current_user.college_id
            # Mess.is_active == True
        )
        .all()
    )

    return messes