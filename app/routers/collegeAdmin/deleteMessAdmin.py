from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.db.session import get_db
from uuid import UUID
# from app.models.mess.messModel import Mess
from app.models.mess.messAdmin import MessAdmin
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/delete",
    tags=["College Admins Mess Deletion Operations"]
)

@router.delete("/mess-admin/{mess_admin_id}")
async def delete_mess_admin(
    mess_admin_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_role([UserRole.college_admin]))
):
    result = await db.execute(
        select(MessAdmin).filter(
            MessAdmin.user_id == mess_admin_id,
            MessAdmin.college_id == current_user.college_id
        )
    )
    mess_admin = result.scalar_one_or_none()

    if not mess_admin:
        raise HTTPException(404, "Mess Admin not found")

    await db.delete(mess_admin)
    await db.commit()

    return {
        "message": "Mess Admin deleted successfully",
    }