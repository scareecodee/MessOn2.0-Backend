from typing import Optional

from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy import select
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.db.session import get_db
from app.models.student.studentModel import Student
from app.models.user.userModel import User
from app.schemas.collegeAdmin.messBillConfigSchema import BillRequest
from app.security.dependencies.getCurrentRole import get_current_role
from app.services.generateCSVService import generate_all_students_bill_csv, generate_students_bill_history_csv
from app.services.messBillService import calculate_students_mess_bill, get_student_detailed_bill_history
from app.utils.userRole import UserRole
from app.models.mess.messWeekModel import MessWeek

router = APIRouter( tags =["Per Student Mess Bill"])

@router.post("/student/bill")
async def generate_mess_bill(
    payload: BillRequest,
    student_id: UUID | None = None,
    current_user: User = Depends(get_current_role([UserRole.college_admin,UserRole.student])),
    db: AsyncSession = Depends(get_db)
):

    if current_user.role == UserRole.college_admin:

        students = await db.execute(
            select(Student).filter(
                Student.college_id == current_user.college_id,
                Student.user_id == student_id
            )
        )
        student : Optional[Student] = students.scalar_one_or_none()

        print(student.user_id)

        mess_weeks = await db.execute(
            select(MessWeek).filter(
                MessWeek.college_id == current_user.college_id,
                MessWeek.mess_id == student.mess_id
            ).order_by(MessWeek.start_date.asc()).limit(1)
        )

        mess_week = mess_weeks.scalar_one_or_none()

        if not mess_week:
            raise HTTPException(404, "Mess week not found")

        students_bill = await calculate_students_mess_bill(
            db=db,
            mess_id= student.mess_id,
            college_id=current_user.college_id,
            range_type=payload.range_type,
            student_id=student.user_id,
            n_days=payload.n_days,
            start_date=payload.start_date,
            end_date=payload.end_date,
            mess_start_date=mess_week.start_date
        )

        return students_bill

    else:

        students = await db.execute(
            select(Student).filter(
                Student.college_id == current_user.college_id,
                Student.user_id == current_user.id
            )
        )
        student: Optional[Student] = students.scalar_one_or_none()

        print(student.user_id)

        mess_weeks = await db.execute(
            select(MessWeek).filter(
                MessWeek.college_id == current_user.college_id,
                MessWeek.mess_id == student.mess_id
            ).order_by(MessWeek.start_date.asc()).limit(1)
        )

        mess_week = mess_weeks.scalar_one_or_none()

        if not mess_week:
            raise HTTPException(404, "Mess week not found")


    students_bill = await calculate_students_mess_bill(
        db=db,
        mess_id=student.mess_id,
        college_id=current_user.college_id,
        range_type=payload.range_type,
        student_id=student.user_id,
        n_days=payload.n_days,
        start_date=payload.start_date,
        end_date=payload.end_date,
        mess_start_date=mess_week.start_date
    )

    return students_bill








