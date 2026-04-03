from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.db.session import get_db
from app.schemas.mess.createMess import MessCreate
from app.schemas.mess.messResponse import MessResponse
from app.models.mess.messModel import Mess
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/admin/create",
    tags=["Manage Mess"]
)

@router.post("/mess", response_model=MessResponse)
async def create_mess(
    mess_details: MessCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_role([UserRole.college_admin]))
):
    mess = Mess(
        college_id=current_user.college_id,  # stop over-converting UUID like this
        name=mess_details.name,
        location=mess_details.location,
        is_active=mess_details.is_active
    )

    db.add(mess)

    await db.flush()


    # print(mess.id)

    await db.commit()
    await db.refresh(mess)

    return mess