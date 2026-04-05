from datetime import date

from sqlalchemy import text
from app.schemas.collegeAdmin import messBillConfigSchema

from app.utils.billRangeNormalizer import normalize_billing_range
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.messBillSQL import ALL_STUDENTS_BILL, STUDENT_DETAILED_BILL_HISTORY
from app.schemas.collegeAdmin.messBillConfigSchema import BillResponse, MealDetail, StudentMealDay


async def calculate_all_students_mess_bill(
    db: AsyncSession,
    mess_id,
    college_id,
    range_type,
    n_days=None,
    start_date=None,
    end_date=None,
    mess_start_date=None
) -> list[BillResponse]:
    start_date, end_date = normalize_billing_range(
        range_type=range_type,
        n_days=n_days,
        start_date=start_date,
        end_date=end_date,
        mess_start_date=mess_start_date
    )

    result = await db.execute(
        text(ALL_STUDENTS_BILL),
        {
            "mess_id": mess_id,
            "college_id": college_id,
            "start_date": start_date,
            "end_date": end_date,
        }
    )

    rows = result.fetchall()

    return [
        BillResponse(
                name =row.name,
                email= row.email,
                roll_no =row.roll_number,
                branch=row.branch,
                batch =row.batch,
                total_billing_periods= row.total_days,
                billing_start_date=  start_date,
                billing_end_date= end_date,
                total_bill = row.total_bill
    )
        for row in rows
    ]

async def get_student_detailed_bill_history(
    db:AsyncSession,
    student_id,
    mess_id,
    college_id,
    range_type,
    n_days = None,
    start_date = None,
    end_date = None,
    mess_start_date = None
):
    start_date, end_date = normalize_billing_range(
        range_type=range_type,
        n_days=n_days,
        start_date=start_date,
        end_date=end_date,
        mess_start_date=mess_start_date
    )

    result = await db.execute(
        text(STUDENT_DETAILED_BILL_HISTORY),
        {
            "student_id": student_id,
            "mess_id": mess_id,
            "college_id": college_id,
            "start_date": start_date,
            "end_date": end_date,
        }
    )

    rows = result.fetchall()

    return [
        StudentMealDay(
            date=row.date,
            breakfast=MealDetail(
                meal_type=row.breakfast_type,
                consumed=(row.breakfast_status == "consumed"),
                selected=(row.breakfast_type is not None),
            ),
            lunch=MealDetail(
                meal_type=row.lunch_type,
                consumed=(row.lunch_status == "consumed"),
                selected=(row.lunch_type is not None),
            ),
            dinner=MealDetail(
                meal_type=row.dinner_type,
                consumed=(row.dinner_status == "consumed"),
                selected=(row.dinner_type is not None),
            ),
        )
        for row in rows
    ]