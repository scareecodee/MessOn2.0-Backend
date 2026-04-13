from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.db.session import get_db
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.mealSubmissionWindowModel import MealSubmissionWindow

from app.schemas.mess.submissionWindowSchema import (
    SubmissionWindowRequest,
    SubmissionWindowResponse
)

from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek

from app.services.weekResolverService import resolve_week

IST = ZoneInfo("Asia/Kolkata")

router = APIRouter(prefix="/mess/create", tags=["Submission Window"])


@router.patch("/submission-window/{menu_week}", response_model=SubmissionWindowResponse)
async def upsert_submission_window(
    menu_week: MenuWeek,
    payload: SubmissionWindowRequest,
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

    week = await resolve_week(
        db,
        menu_week,
        admin.mess_id,
        current_user.college_id
    )

    start_time = payload.start_time
    end_time = payload.end_time

    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=IST)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=IST)

    start_utc = start_time.astimezone(timezone.utc)
    end_utc = end_time.astimezone(timezone.utc)

    if start_utc >= end_utc:
        raise HTTPException(400, "start_time must be before end_time")

    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(MealSubmissionWindow).filter(
            MealSubmissionWindow.mess_id == admin.mess_id,
            MealSubmissionWindow.week_id == week.id
        )
    )
    window = result.scalar_one_or_none()

    # if window and now > window.end_time:
    #     raise HTTPException(
    #         400,
    #         "Cannot modify window after it has ended"
    #     )

    if window:
        window.start_time = start_utc
        window.end_time = end_utc
    else:
        window = MealSubmissionWindow(
            mess_id=admin.mess_id,
            college_id=current_user.college_id,
            week_id=week.id,
            start_time=start_utc,
            end_time=end_utc
        )
        db.add(window)

    await db.commit()
    await db.refresh(window)


    now_utc = datetime.now(timezone.utc)

    if window.start_time < now_utc < window.end_time:
        return SubmissionWindowResponse(
            start_time=window.start_time.astimezone(IST),
            end_time=window.end_time.astimezone(IST),
            is_active=True
        )

    return SubmissionWindowResponse(
        start_time=window.start_time.astimezone(IST),
        end_time=window.end_time.astimezone(IST),
        is_active=False
    )