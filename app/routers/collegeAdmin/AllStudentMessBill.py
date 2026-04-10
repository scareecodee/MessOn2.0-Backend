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

router = APIRouter(prefix="/mess/{mess_id}", tags=["Mess Bill"])

@router.post("/bill")
async def generate_mess_bill(
    request: Request,
    payload: BillRequest,
    mess_id: UUID,
    current_user: User = Depends(get_current_role([UserRole.college_admin])),
    db: AsyncSession = Depends(get_db)
):

    mess_weeks = await db.execute(
        select(MessWeek).filter(
            MessWeek.college_id == current_user.college_id,
            MessWeek.mess_id == mess_id
        ).order_by(MessWeek.start_date.asc()).limit(1)
    )

    mess_week : MessWeek | None = mess_weeks.scalar_one_or_none()

    if not mess_week:
        raise HTTPException(404, "Mess week not found")

    print(mess_week.start_date)

    all_students_bill = await calculate_students_mess_bill(
        db=db,
        mess_id=mess_id,
        college_id=current_user.college_id,
        range_type=payload.range_type,
        n_days=payload.n_days,
        start_date=payload.start_date,
        end_date=payload.end_date,
        mess_start_date=mess_week.start_date
    )

    accept = request.headers.get("accept", "")


    if "text/csv" in accept:
        csv_file = generate_all_students_bill_csv(all_students_bill)
        return StreamingResponse(
            csv_file,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": "attachment; filename=mess_bill.csv"
            }
        )

    return all_students_bill





