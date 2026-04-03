from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.mess.messModel import Mess
from app.models.user.userModel import User
from app.schemas.mess.messResponse import MessResponse
from typing import List
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/admin/college",
    tags=["Manage Mess"]
)

@router.get("/messes", response_model=List[MessResponse])
async def list_messes(
    current_user: User = Depends(get_current_role([UserRole.college_admin])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Mess).filter(
            Mess.college_id == current_user.college_id
            # Mess.is_active == True
        )
    )
    messes = result.scalars().all()

    return messes