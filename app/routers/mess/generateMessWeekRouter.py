from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin


from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.models.mess.messModel import Mess

from app.services.messWeekGenerationService import generate_weeks_for_mess

from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.mess.messWeekModel import MessWeek

IST = ZoneInfo("Asia/Kolkata")


today=datetime.now(IST).date()
router = APIRouter(prefix="/admin", tags=["Generate Mess Weeks"])

@router.post("/generate-weeks")
async def generate_weeks_manual(
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MessAdmin).filter(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        )
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(404, "Mess admin not found")

    result = await db.execute(
        select(Mess).filter(Mess.id == admin.mess_id)
    )
    mess = result.scalar_one_or_none()

    weeks = (
        await db.execute(
            select(MessWeek).where(
                MessWeek.mess_id == mess.mess_id,
                MessWeek.start_date <= today,
                MessWeek.end_date >= today
            )
        )
    )
    week: Optional[MessWeek] = weeks.scalar_one_or_none()

    if not week:
        await generate_weeks_for_mess(
            db=db,
            mess_id=mess.id,
            college_id=mess.college_id,
            # mess_open_date=today
        )


    return {"message": "Weeks generated successfully"}