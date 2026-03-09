from fastapi import APIRouter, Depends, status, Response,HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user.userModel import User
from app.models.student.studentModel import Student
from app.models.college.collegeModel import College
from app.utils.userRole import UserRole
from app.security.dependencies.getCurrentRole import get_current_role
from app.schemas.student.updateStudentDetails import StudentUpdateRequest, StudentUpdateResponse , StudentUpdateConflictResponse,StudentResponse
from app.schemas.student.fetchStudentsSchema import StudentResponse
from uuid import UUID


router = APIRouter(
    prefix="/admin/students .",
    tags=["Student Details Update"]
)

@router.patch("/update/{user_id}", response_model=StudentUpdateResponse)
def update_student(
    user_id: UUID,
    student_update: StudentUpdateRequest,
    response: Response,
    current_admin: User = Depends(get_current_role(UserRole.college_admin)),
    db: Session = Depends(get_db)
):

    student = (db.query(User).filter(
        User.college_id==current_admin.college_id,
        User.id == user_id).
        first()
    )

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    college=db.query(College).filter(College.id==current_admin.college_id).first()

    allowed_domain = str(college.domain).lower()

    update_data = student_update.model_dump(exclude_unset=True)

    # email validation
    if "email" in update_data:
        if not update_data["email"].lower().endswith("allowed_domain"):
            raise HTTPException(status_code=400, detail="Invalid institute email")

        existing_email = db.query(Student).filter(
            User.email == update_data["email"].lower(),
            User.id != user_id
        ).first()

        if existing_email:
            response.status_code = status.HTTP_409_CONFLICT
            return StudentUpdateResponse(
                status=False,
                conflicts=(
                    StudentUpdateConflictResponse(
                        email=update_data["email"].lower(),
                        roll_number=update_data["roll_number"].lower(),
                        message="Email already exists"
                    )
                )
           )


    # roll number validation
    if "roll_number" in update_data:
        existing_roll = db.query(Student).filter(
            Student.roll_number == update_data["roll_number"].lower(),
            User.id != user_id
        ).first()

        if existing_roll:
            response.status_code = status.HTTP_409_CONFLICT
            return StudentUpdateResponse(
                status=False,
                conflicts=(
                    StudentUpdateConflictResponse(
                        email=update_data["email"].lower(),
                        roll_number=update_data["roll_number"].lower(),
                        message="Roll number already exists"
                    )
                )
            )


    # apply updates
    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return StudentUpdateResponse(
        status=True,
        conflicts=None
    )

