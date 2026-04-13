from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.college.collegeModel import College
from app.models.user.userModel import User
from app.models.college.collegeAdmin import CollegeAdmin
from app.schemas.rootAdmin.collegeAdminCreate import CollegeAdminCreate
from app.schemas.user.userResponse import UserResponse
from app.utils.userRole import UserRole
from app.security.dependencies.getCurrentRootAdmin import get_current_root_admin

router = APIRouter(
    tags=["Create College Admin By RootAdmin"],
)


@router.post("/root/college-admins", response_model=UserResponse)
async def create_college_admin(
    payload: CollegeAdminCreate,
    root_user = Depends(get_current_root_admin),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(College).filter(College.id == payload.college_id)
    )
    college = result.scalar_one_or_none()

    if not college:
        raise HTTPException(400, "College does not exist")

    if not college.status:
        raise HTTPException(400, "College is inactive")

    if not payload.email.endswith(college.domain):
        raise HTTPException(400, "Invalid college domain")

    admins = await db.execute(
        select(User).filter(
            User.email == payload.email,
            User.college_id == payload.college_id
        )
    )
    existing_admins = admins.scalar_one_or_none()

    if existing_admins:
        raise HTTPException(400, "User already exists")

    user = User(
        name=payload.name,
        email=payload.email,
        college_id=payload.college_id,
        role=UserRole.college_admin,
        is_active=True
    )

    db.add(user)
    await db.flush()

    college_admin = CollegeAdmin(
        id=user.id, 
        college_id=payload.college_id
    )

    db.add(college_admin)

    await db.commit()
    await db.refresh(user)

    return user