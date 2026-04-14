from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.college.collegeAdmin import CollegeAdmin
from app.models.college.collegeModel import College
from app.models.user.userModel import User
from app.schemas.user.createUser import UserCreate
from app.schemas.user.userResponse import UserResponse
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole


router = APIRouter(
    prefix="/create",
    tags=["Mess Admin Creation & Deletion Operations"]
)

@router.post("/college-admins", response_model=UserResponse)
async def create_mess_admin(
    payload: UserCreate,
    current_user: User = Depends(get_current_role([UserRole.college_admin])),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).filter(
            User.email == payload.email,
            User.college_id == current_user.college_id)
    )
    user = result.scalar_one_or_none()

    if user :
        return HTTPException(status_code=400, detail="User already exists")

    colleges = await db.execute(
        select(College).filter(
            College.id == current_user.college_id,
        )
    )

    college = colleges.scalar_one_or_none()

    if not college:
        return HTTPException(status_code=400, detail="College does not exist")

    # domain = college.domain
    #
    # if not payload.email.endswith(domain):
    #     return HTTPException(status_code=400, detail="Invalid college domain !")

    user = User(
            college_id=current_user.college_id,
            name=payload.name,
            email=payload.email,
            role=UserRole.college_admin,
            is_active=True
        )

    db.add(user)

    college_admin = CollegeAdmin(
        id=user.college_id,
        college_id=current_user.college_id,
    )
    db.add(college_admin)

    await db.commit()

    return user