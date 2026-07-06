from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from datetime import datetime, timezone, timedelta

from app.db.session import get_db
from app.models.user.userModel import User
from app.models.student.studentModel import Student
from app.models.mess.mealSubmissionWindowModel import MealSubmissionWindow
from app.models.student.mealPreferenceModel import MealPreference

from app.schemas.student.mealPreferenceRequest import MealPreferenceRequest
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek

from app.services.weekResolverService import resolve_week
from app.models.mess.messAdmin import MessAdmin
from app.services.resolveDateFromDay import resolve_date_from_day
from app.services.messClosureService import is_mess_closed

IST = ZoneInfo("Asia/Kolkata")

router = APIRouter(prefix="/submit", tags=["Meal Preference"])


@router.patch("/meal-preference/{menu_week}")
async def upsert_meal_preference(
    menu_week: MenuWeek,
    payload: list[MealPreferenceRequest],
    current_user: User = Depends(get_current_role([UserRole.student])),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
            select(Student).filter(
                Student.user_id == current_user.id,
                Student.college_id == current_user.college_id
            )
        )
    student : Optional[Student] = result.scalar_one_or_none()

    if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

    mess_id = student.mess_id

    week = await resolve_week(
        db,
        menu_week,
        mess_id,
        current_user.college_id
    )

    result = await db.execute(
        select(MealSubmissionWindow).filter(
            MealSubmissionWindow.mess_id == mess_id,
            MealSubmissionWindow.week_id == week.id
        )
    )
    window : Optional[MealSubmissionWindow] = result.scalar_one_or_none()

    if not window:
        raise HTTPException(400, "Submission window not configured")

    now = datetime.now(IST).astimezone(window.start_time.tzinfo)

    if not (window.start_time <= now <= window.end_time):
        raise HTTPException(400, "Submission window closed")


    rows = []

    for item in payload:

        target_date = await resolve_date_from_day(week, item.day)

        if target_date < week.start_date or target_date > week.end_date:
            continue

        if await is_mess_closed(db, student.mess_id, target_date):
            continue

        rows.append({
            "student_id": student.user_id,
            "college_id": current_user.college_id,
            "mess_id": student.mess_id,
            "week_id" : week.id,
            "date": target_date,
            "meal_slot": item.meal_slot,
            "meal_type": item.meal_type
        })
    if rows:
        stmt = insert(MealPreference).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["student_id", "date", "meal_slot"],
            set_={"meal_type": stmt.excluded.meal_type}
        )

        await db.execute(stmt)
        await db.commit()

    return {
        "message": "Meal preferences processed",
        "accepted_days": len(set(r["date"] for r in rows)),
    }