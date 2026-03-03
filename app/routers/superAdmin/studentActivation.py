from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.student.studentModel import Student
from app.schemas.student.Activation import Toggle
from uuid import UUID

router = APIRouter(
    prefix="/admin/students",
    tags=["Student Details Update"]
)

@router.patch("/{student_id}/toggle-activation")
def toggle_student_activation(
    response: Response,
    student_id: str,
    db: Session = Depends(get_db)
):
    student_id = student_id.lower()
    student = db.query(Student).filter(Student.roll_number == student_id).first()

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
