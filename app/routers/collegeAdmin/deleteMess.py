from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.db.session import get_db
from uuid import UUID
from app.models.mess.messModel import Mess
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/delete",
    tags=["Mess Admin Management"]
)

@router.delete("/mess/{mess_id}")
async def delete_mess(
    mess_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_role(UserRole.college_admin))
):
    result = await db.execute(
        select(Mess).filter(
            Mess.id == mess_id,
            Mess.college_id == current_user.college_id
        )
    )
    mess = result.scalar_one_or_none()

    if not mess:
        raise HTTPException(404, "Mess not found")

    await db.delete(mess)
    await db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )