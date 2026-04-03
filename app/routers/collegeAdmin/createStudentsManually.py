from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List
from app.db.session import get_db
from app.models.user.userModel import User
from app.models.college.collegeModel import College
from app.models.mess.messModel import Mess
from app.models.student.studentModel import Student
from app.schemas.student.createStudents import StudentCreate, AddStudentManuallyResponse, AddManuallyConflictResponse
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole


router = APIRouter(
    prefix="/messes",
    tags=["Manage Mess"]
)

@router.post("/{mess_id}/students/manually", response_model=AddStudentManuallyResponse)
async def create_students(
    mess_id: UUID,
    payload: List[StudentCreate],
    response: Response,
    current_user: User = Depends(get_current_role(UserRole.college_admin)),
    db: AsyncSession = Depends(get_db),
):
    conflicts: List[AddManuallyConflictResponse] = []

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
        select(College).filter(College.id == current_user.college_id)
    )
    college = result.scalar_one_or_none()

    allowed_domain = str(college.domain)

    for student in payload:

        # -------- DOMAIN CHECK --------
        # if not student.email.endswith(allowed_domain):
        #     conflicts.append(
        #         AddManuallyConflictResponse(
        #             email=student.email,
        #             roll_number=student.roll_number,
        #             message=f"Email must end with {allowed_domain}"
        #         )
        #     )
        #     continue

        result = await db.execute(
            select(User).filter(User.email == student.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            conflicts.append(
                AddManuallyConflictResponse(
                    email=student.email,
                    roll_number=student.roll_number,
                    message="Email already exists"
                )
            )
            continue

        result = await db.execute(
            select(Student).filter(
                Student.roll_number == student.roll_number,
                Student.mess_id == mess_id
            )
        )
        existing_roll = result.scalar_one_or_none()

        if existing_roll:
            conflicts.append(
                AddManuallyConflictResponse(
                    email=student.email,
                    roll_number=student.roll_number,
                    message="Roll number already exists in this mess"
                )
            )
            continue

        user = User(
            college_id=current_user.college_id,
            name=student.name,
            email=student.email,
            role=UserRole.student,
            is_active=True
        )

        db.add(user)
        await db.flush()

        new_student = Student(
            user_id=user.id,
            college_id=current_user.college_id,
            mess_id=mess_id,
            roll_number=student.roll_number,
            branch=student.branch,
            batch=student.batch
        )

        db.add(new_student)

    await db.commit()

    if conflicts:
        return AddStudentManuallyResponse(
            status=False,
            conflicts=conflicts
        )

    return AddStudentManuallyResponse(
        status=True,
        conflicts=conflicts
    )