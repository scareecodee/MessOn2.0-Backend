# app/services/submissionWindowService.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.mess.mealSubmissionWindowModel import MealSubmissionWindow
from app.models.mess.submissionWindowTemplateModel import SubmissionWindowTemplate
from app.services.submissionWindowTemplateService import build_window_from_template
from app.schemas.mess.submissionWindowSchema import SubmissionWindowResponse


async def get_or_create_submission_window(
    db: AsyncSession,
    mess_id,
    college_id,
    week
):

    result = await db.execute(
        select(MealSubmissionWindow).filter(
            MealSubmissionWindow.mess_id == mess_id,
            MealSubmissionWindow.week_id == week.id
        )
    )
    window = result.scalar_one_or_none()

    if window:
        return window

    result = await db.execute(
        select(SubmissionWindowTemplate).filter(
            SubmissionWindowTemplate.mess_id == mess_id,
            SubmissionWindowTemplate.college_id == college_id
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise Exception("Submission window template not configured")

    start_utc, end_utc = build_window_from_template(template, week)

    new_window = MealSubmissionWindow(
        mess_id=mess_id,
        college_id=college_id,
        week_id=week.id,
        start_time=start_utc,
        end_time=end_utc
    )

    try:
        db.add(new_window)
        await db.commit()
        await db.refresh(new_window)
        return new_window

    except IntegrityError:
        # another request inserted it
        await db.rollback()

        result = await db.execute(
            select(MealSubmissionWindow).filter(
                MealSubmissionWindow.mess_id == mess_id,
                MealSubmissionWindow.week_id == week.id
            )
        )
        return result.scalar_one()
