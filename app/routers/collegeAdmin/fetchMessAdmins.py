from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.mess.messModel import Mess
from app.models.mess.messAdmin import MessAdmin
from app.models.user.userModel import User
from app.schemas.user.userResponse import UserResponse
from typing import List
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from uuid import UUID

router = APIRouter(
    prefix="/fetch",
    tags=["Manage Mess"]
)

@router.get("/mess-admins/{mess_id}", response_model=List[UserResponse])
async def list_mess_admins(
    mess_id: UUID,
    current_user: User = Depends(get_current_role([UserRole.college_admin])),
    db: AsyncSession = Depends(get_db)
):
    # -------- VERIFY MESS --------
    result = await db.execute(
        select(Mess).filter(
            Mess.id == mess_id,
            Mess.college_id == current_user.college_id
        )
    )
    mess = result.scalar_one_or_none()
    print("mess")

    if not mess:
        raise HTTPException(404, "Mess not found")
    print("mess out")

    result = await db.execute(
        select(User)
        .join(MessAdmin, MessAdmin.user_id == User.id)
        .filter(
            MessAdmin.mess_id == mess_id,
            User.college_id == current_user.college_id,
            User.role == UserRole.mess_admin
        )
    )
    mess_admins = result.scalars().all()

    return mess_admins