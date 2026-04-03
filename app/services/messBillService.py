from datetime import date

from sqlalchemy import text
from app.schemas.collegeAdmin import messBillConfigSchema

from app.utils.billRangeNormalizer import normalize_billing_range
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.messBillSQL import SQL_BILL
from app.schemas.collegeAdmin.messBillConfigSchema import BillResponse


async def calculate_mess_bill(
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
        text(SQL_BILL),
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
                total_bill_days = row.total_days,
                bill_start_date =  start_date,
                bill_end_date = end_date,
                total_bill = row.total_bill
    )
        for row in rows
    ]