from datetime import timezone, datetime
from fastapi import APIRouter, Depends, HTTPException
from zoneinfo import ZoneInfo
from app.schemas.mess.submissionWindowSchema import SubmissionWindowResponse
from app.utils.menuWeek import MenuWeek
from app.services.weekResolverService import resolve_week
from app.services.submissionWindowCreationService import get_or_create_submission_window

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.submissionWindowTemplateModel import SubmissionWindowTemplate

from app.schemas.mess.submissionWindowTemplateSchema import (
    SubmissionWindowTemplateResponse
)

from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.db.session import get_db


IST = ZoneInfo("Asia/Kolkata")

router = APIRouter(
    prefix="/fetch/mess",
    tags=["Submission Window"]
)

@router.get("/submission-window/template", response_model=SubmissionWindowTemplateResponse)
async def get_submission_window_template(
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MessAdmin).filter(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        )
    )
    mess_admin = result.scalar_one_or_none()

    if not mess_admin:
        raise HTTPException(status_code=404, detail="Mess admin not found")

    result = await db.execute(
        select(SubmissionWindowTemplate).where(
            SubmissionWindowTemplate.mess_id == mess_admin.mess_id,
            SubmissionWindowTemplate.college_id == current_user.college_id
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        return HTTPException(status_code=404, detail="Template admin not found")

    return template


@router.get("/submission-window/{menu_week}", response_model=SubmissionWindowResponse)
async def get_submission_window(
    menu_week: MenuWeek,
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(MessAdmin).filter(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        )
    )
    mess_admin = result.scalar_one_or_none()

    if not mess_admin:
        raise HTTPException(404, "Mess admin profile not found")

    week = await resolve_week(
        db,
        menu_week,
        mess_admin.mess_id,
        current_user.college_id
    )

    window = await get_or_create_submission_window(
        db,
        mess_admin.mess_id,
        current_user.college_id,
        week
    )

    # result = await db.execute(
    #     select(MealSubmissionWindow).filter(
    #         MealSubmissionWindow.mess_id == mess_admin.mess_id,
    #         MealSubmissionWindow.week_id == week.id
    #     )
    # )
    # window = result.scalar_one_or_none()

    if not window:
        return SubmissionWindowResponse(
            start_time=None,
            end_time=None,
            is_active=False
        )

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


