from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.submissionWindowTemplateModel import SubmissionWindowTemplate

from app.schemas.mess.submissionWindowTemplateSchema import (
    SubmissionWindowTemplateRequest,
    SubmissionWindowTemplateResponse
)

from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.weekDayOrder import WEEKDAY_ORDER

router = APIRouter(
    prefix="/create/mess",
    tags=["Submission Window Template"]
)

@router.patch("/submission-window/template", response_model=SubmissionWindowTemplateResponse)
async def update_submission_window_template(
    payload: SubmissionWindowTemplateRequest,
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

    start_idx = WEEKDAY_ORDER[payload.start_day.value]
    end_idx = WEEKDAY_ORDER[payload.end_day.value]

    if start_idx > end_idx:
        raise HTTPException(status_code=400, detail="start_day must be before or same as end_day")

    if start_idx == end_idx and payload.start_time >= payload.end_time:
        raise HTTPException(status_code=400, detail="Invalid time range for same day")

    result = await db.execute(
        select(SubmissionWindowTemplate).filter(
            SubmissionWindowTemplate.mess_id == mess_admin.mess_id,
            SubmissionWindowTemplate.college_id == current_user.college_id
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Submission window template does not exist. Use POST to create."
        )

    template.start_day = payload.start_day
    template.start_time = payload.start_time
    template.end_day = payload.end_day
    template.end_time = payload.end_time

    await db.commit()
    await db.refresh(template)

    return template