
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.dialects.postgresql import insert
# from sqlalchemy.future import select
# from datetime import datetime, timezone
# from zoneinfo import ZoneInfo

# from app.db.session import get_db
# from app.models.user.userModel import User
# from app.models.student.studentModel import Student
# from app.models.mess.mealSubmissionWindowModel import MealSubmissionWindow
# from app.models.student.mealPreferenceModel import MealPreference

# from app.schemas.student.mealPreferenceRequest import MealPreferenceRequest
# from app.security.dependencies.getCurrentRole import get_current_role
# from app.utils.userRole import UserRole
# from app.utils.menuWeek import MenuWeek

# from app.services.weekResolverService import resolve_week

# IST = ZoneInfo("Asia/Kolkata")

# router = APIRouter(
#     prefix="/submit",
#     tags=["Meal Preference"]
# )


# @router.post("/meal-preference/{menu_week}")
# async def submit_meal_preference(
#     menu_week: MenuWeek,
#     payload: list[MealPreferenceRequest],
#     current_user: User = Depends(get_current_role([UserRole.student])),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(
#         select(Student).filter(
#             Student.user_id == current_user.id,
#             Student.college_id == current_user.college_id
#         )
#     )
#     student = result.scalar_one_or_none()

#     if not student:
#         raise HTTPException(404, "Student profile not found")

#     week_id, week_start = await resolve_week(
#         db,
#         menu_week,
#         student.mess_id,
#         current_user.college_id
#     )

#     result = await db.execute(
#         select(MealSubmissionWindow).filter(
#             MealSubmissionWindow.mess_id == student.mess_id,
#             MealSubmissionWindow.week_id == week_id
#         )
#     )
#     window = result.scalar_one_or_none()

#     if not window:
#         raise HTTPException(400, "Submission window not set")

#     now_utc = datetime.now(timezone.utc)

#     if not (window.start_time <= now_utc <= window.end_time):
#         raise HTTPException(400, "Submission window closed")

#     for item in payload:
#         if not (week_start <= item.date < week_start + timedelta(days=7)):
#             raise HTTPException(400, f"Date {item.date} not in selected week")

#     for item in payload:
#         stmt = insert(MealPreference).values(
#             student_id=student.user_id,
#             college_id=current_user.college_id,
#             mess_id=student.mess_id,
#             date=item.date,
#             meal_slot=item.meal_slot,
#             meal_type=item.meal_type
#         )

#         stmt = stmt.on_conflict_do_update(
#             index_elements=["student_id", "date", "meal_slot"],
#             set_={"meal_type": stmt.excluded.meal_type}
#         )

#         await db.execute(stmt)

#     await db.commit()

#     return {"message": "Meal preferences submitted successfully"}