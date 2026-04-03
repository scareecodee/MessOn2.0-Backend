from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.user.userModel import User
from app.models.student.studentModel import Student
from app.models.college.collegeModel import College
from app.utils.userRole import UserRole
from app.security.dependencies.getCurrentRole import get_current_role
from app.schemas.student.updateStudentDetails import StudentUpdateRequest, StudentUpdateResponse, StudentUpdateConflictResponse, StudentDetailResponse
from app.schemas.student.fetchStudentsSchema import StudentResponse
from uuid import UUID


router = APIRouter(
    prefix="/admin/students",
    tags=["Student Details Update"]
)

@router.patch("/update/{user_id}", response_model=StudentUpdateResponse)
async def update_student(
    user_id: UUID,
    student_update: StudentUpdateRequest,
    # response: Response,
    current_admin: User = Depends(get_current_role([UserRole.college_admin])),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User, Student)
        .join(Student, Student.user_id == User.id)
        .where(
            User.id == user_id,
            User.college_id == current_admin.college_id
        )
    )

    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Student not found")

    user, student = row

    result = await db.execute(
        select(College).filter(College.id == current_admin.college_id)
    )
    college = result.scalar_one_or_none()

    allowed_domain = str(college.domain).lower()

    update_data = student_update.model_dump(exclude_unset=True)

    if "email" in update_data:
        email = update_data["email"].lower()

        if not email.endswith(allowed_domain):
            raise HTTPException(status_code=400, detail="Invalid institute email")

        result = await db.execute(
            select(User)
            .where(
                User.email == email,
                User.college_id == current_admin.college_id,
                User.id != user_id
            )
        )
        existing_email = result.scalar_one_or_none()

        if existing_email:
            return StudentUpdateResponse(
                status=False,
                student_details=None,
                conflicts=StudentUpdateConflictResponse(
                    email=email,
                    roll_number=update_data.get("roll_number"),
                    message="Email already exists"
                )
            )

    if "roll_number" in update_data:
        roll = update_data["roll_number"].lower()

        result = await db.execute(
            select(Student)
            .where(
                Student.roll_number == roll,
                Student.college_id == current_admin.college_id,
                Student.user_id != user_id
            )
        )
        existing_roll = result.scalar_one_or_none()

        if existing_roll:
            return StudentUpdateResponse(
                status=False,
                student_details=None,
                conflicts=StudentUpdateConflictResponse(
                    email=update_data.get("email"),
                    roll_number=roll,
                    message="Roll number already exists"
                )
            )

    for field, value in update_data.items():
        if field == "email":
            setattr(user, "email", value.lower())

        elif field in ["roll_number", "branch", "batch"]:
            setattr(student, field, value)

        elif hasattr(user, field):
            setattr(user, field, value)

    await db.commit()

    await db.refresh(user)
    await db.refresh(student)

    return StudentUpdateResponse(
        status=True,
        student_details=StudentDetailResponse(
            student_uuid=user_id,
            name=user.name,
            roll_number=student.roll_number,
            email=user.email,
            branch=student.branch,
            batch=student.batch,
            is_active=user.is_active,
        ),
        conflicts=None
    )