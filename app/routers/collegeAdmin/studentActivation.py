from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.student.studentModel import Student
from app.models.user.userModel import User
from app.utils.userRole import UserRole
from app.schemas.student.Activation import Toggle
from app.security.dependencies.getCurrentRole import get_current_role
from uuid import UUID

router = APIRouter(
    prefix="/admin",
    tags=["Toggle Activation"]
)
@router.patch("/{user_id}/toggle-activation")
async def toggle_student_activation(
    response: Response,
    user_id: UUID,
    current_admin: User = Depends(get_current_role([UserRole.college_admin])),
    db: AsyncSession = Depends(get_db)
):
    # student_id = student_id.strip().lower()
    # print(student_uuid)
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.college_id==current_admin.college_id
    ))
    user = result.scalar_one_or_none()

    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return Toggle(
            is_active=False,
        )

    user.is_active = not user.is_active

    await db.commit()
    await db.refresh(user)

    response.status_code = status.HTTP_200_OK
    return Toggle(
        is_active=bool(user.is_active)
    )