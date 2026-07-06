from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.db.session import get_db
from app.models.mess.messAdmin import MessAdmin
from app.models.user.userModel import User
from app.models.mess.messModel import Mess
from app.schemas.user.createUser import UserCreate
from app.schemas.user.userResponse import UserResponse
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole


router = APIRouter(
    prefix="/mess",
    tags=["Manage Mess"]
)

@router.post("/{mess_id}/admins", response_model=UserResponse)
async def create_mess_admin(
    mess_id: UUID,
    payload: UserCreate,
    current_user: User = Depends(get_current_role([UserRole.college_admin])),
    db: AsyncSession = Depends(get_db)
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

    result = await db.execute(
        select(User).filter(
            User.email == payload.email,
             User.college_id == current_user.college_id)
             )
    
    user = result.scalar_one_or_none()

    if user :
        raise HTTPException(status_code=409, detail="User already exists")

    # if user:
    #     if user.role in [UserRole.student, UserRole.college_admin]:
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Email already belongs to a student or college admin"
    #         )
    #     user.name = payload.name

    else:
        user = User(
            college_id=current_user.college_id,
            name=payload.name,
            email=payload.email,
            role=UserRole.mess_admin,
            is_active=True
        )

        db.add(user)
        await db.flush()

    result = await db.execute(
        select(MessAdmin).filter(
            MessAdmin.user_id == user.id,
            MessAdmin.mess_id == mess_id
        )
    )
    existing_relation = result.scalar_one_or_none()

    if existing_relation:
        raise HTTPException(
            status_code=400,
            detail="User already assigned to this mess"
        )

    mess_admin = MessAdmin(
        user_id=UUID(str(user.id)),
        mess_id=mess_id,
        college_id=current_user.college_id
    )

    db.add(mess_admin)
    await db.commit()

    return user