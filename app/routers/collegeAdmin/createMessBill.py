from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID
from datetime import date, timedelta
from app.schemas.collegeAdmin.messBillConfigSchema import PerDayMealPriceResponse, PerDayMealPriceRequest
from app.db.session import get_db
from app.models.college.MessBillConfigModel import PerDayMealPrice
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.models.college.collegeAdmin import CollegeAdmin

router = APIRouter(
    prefix="/mess",
    tags=["Mess Bill"]
)

@router.patch("/bill-config/{mess_id}", response_model=PerDayMealPriceResponse)
async def update_mess_bill_config(
    payload: PerDayMealPriceRequest,
    mess_id: UUID,
    current_user: User = Depends(get_current_role([UserRole.college_admin])),
    db: AsyncSession = Depends(get_db)
):
    today = date.today()

    result = await db.execute(
        select(CollegeAdmin).filter(
            CollegeAdmin.id == current_user.id,
            CollegeAdmin.college_id == current_user.college_id
        )
    )
    college_admin = result.scalar_one_or_none()

    if not college_admin:
        raise HTTPException(404, "College Admin admin not found")

    result = await db.execute(
        select(PerDayMealPrice).where(
            PerDayMealPrice.mess_id == mess_id,
            PerDayMealPrice.college_id == current_user.college_id,
            PerDayMealPrice.end_date.is_(None)
        )
    )
    current_config = result.scalar_one_or_none()

    if current_config:
        if payload.start_date <= current_config.start_date:
            raise HTTPException(
                400,
                "New start_date must be after existing start_date"
            )

        current_config.end_date = payload.start_date - timedelta(days=1)

    new_config = PerDayMealPrice(
        college_id=current_user.college_id,
        mess_id=mess_id,
        per_day_price=payload.per_day_price,
        start_date=payload.start_date,
        end_date=None
    )

    db.add(new_config)

    await db.commit()
    await db.refresh(new_config)


    return (
        PerDayMealPriceResponse(
        per_day_price=payload.per_day_price,
        start_date=payload.start_date,
        end_date=None
    )
    )
