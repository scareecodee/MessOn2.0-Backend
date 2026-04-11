from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.student.studentModel import Student
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.db.session import get_db
from app.schemas.student.deleteStudents import DeleteStudents
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/delete",
    tags=["College Admins Mess Deletion Operations"]
)


@router.delete("/students")
async def delete_mess_admin(
    student_id: DeleteStudents,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_role([UserRole.college_admin]))
):
    students = await db.execute(
        select(Student).filter(
            Student.user_id == student_id.students_id,
            Student.college_id == current_user.college_id
        )
    )
    students = students.fetchall()

    if not students:
        raise HTTPException(404, "Students not found")

    await db.delete(students)
    await db.commit()

    return {
        "message": "All Students deleted successfully",
    }

@router.delete("/student/{student_id}")
async def delete_mess_admin(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_role([UserRole.college_admin]))
):
    students = await db.execute(
        select(Student).filter(
            Student.user_id == student_id,
            Student.college_id == current_user.college_id
        )
    )
    student = students.scalar_one_or_none()

    if not student:
        raise HTTPException(404, "Student not found")

    await db.delete(student)
    await db.commit()

    return {
        "message": "Student deleted successfully",
    }