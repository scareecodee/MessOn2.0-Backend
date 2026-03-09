from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.student.studentModel import Student
from app.models.user.userModel import User
from app.utils.userRole import UserRole
from app.schemas.student.Activation import Toggle
from app.security.dependencies.getCurrentRole import get_current_role
from uuid import UUID

router = APIRouter(
    prefix="/admin/students",
    tags=["Student Details Update"]
)

@router.patch("/{user_id}/toggle-activation")
def toggle_student_activation(
    response: Response,
    user_id: UUID,
    current_admin:User=Depends(get_current_role(UserRole.college_admin)),
    db: Session = Depends(get_db)
):
    # student_id = student_id.strip().lower()
    # print(student_uuid)
    student = db.query(User).filter(User.id == user_id).first()

    if not student:
        response.status_code=status.HTTP_404_NOT_FOUND
        return Toggle(
            is_active=False,
        )


    student.is_active = not student.is_active

    db.commit()
    db.refresh(student)

    response.status_code=status.HTTP_200_OK
    return Toggle(
        is_active= bool(student.is_active)
    )
