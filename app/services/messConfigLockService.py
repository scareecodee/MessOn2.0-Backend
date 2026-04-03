from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mess.mealSubmissionWindowModel import MealSubmissionWindow


async def is_config_locked(
    db: AsyncSession,
    mess_id,
    week_id
) -> bool:

    result = await db.execute(
        select(MealSubmissionWindow).filter(
            MealSubmissionWindow.mess_id == mess_id,
            MealSubmissionWindow.week_id == week_id
        )
    )

    window = result.scalar_one_or_none()

    # print(window)

    if not window:
        raise HTTPException(400, "Submission window not configured")

    now = datetime.now(timezone.utc)
    print("after now ")

    if now > window.end_time:
        raise HTTPException(
            400,
            "Configuration locked. Submission window closed."
        )

    return False

