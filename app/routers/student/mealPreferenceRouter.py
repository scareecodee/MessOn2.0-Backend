# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from datetime import date, timedelta
# from app.db.session import get_db
# from app.models.student.mealPreferenceModel import MealPreference
# from schemas.student.mealPreferenceSchema import WeeklyMealPreferenceCreate
#
# router = APIRouter(
#     prefix="/meal-preferences",
#     tags=["Meal Preferences"]
# )
#
#
# @router.post("/weekly", status_code=status.HTTP_201_CREATED)
# def create_weekly_meal_preferences(
#     data: WeeklyMealPreferenceCreate,
#     db: Session = Depends(get_db)
# ):
#     today = date.today()
#
#     # 🛑 Allow only Saturday or Sunday
#     if today.weekday() not in [5, 6]:
#         raise HTTPException(
#             status_code=403,
#             detail="Preferences can only be submitted on Saturday or Sunday"
#         )
#
#     # 🧠 Calculate next Monday
#     days_until_monday = 7 - today.weekday()
#     next_monday = today + timedelta(days=days_until_monday)
#
#     # 🛑 Only allow next week's preferences
#     if data.week_start != next_monday:
#         raise HTTPException(
#             status_code=400,
#             detail=f"You can only submit preferences for next week starting {next_monday}"
#         )
#
#     # 🔎 Check if already submitted
#     existing = db.query(MealPreference).filter(
#         MealPreference.student_id == data.student_id,
#         MealPreference.week_start == data.week_start
#     ).first()
#
#     if existing:
#         raise HTTPException(
#             status_code=400,
#             detail="Preferences already submitted for this week"
#         )
#
#     records = []
#
#     for item in data.preferences:
#         pref = MealPreference(
#             student_id=data.student_id,
#             week_start=data.week_start,
#             day=item.day,
#             meal_slot=item.meal_slot,
#             preference=item.preference
#         )
#         records.append(pref)
#
#     db.add_all(records)
#     db.commit()
#
#     return {
#         "message": "Weekly meal preferences submitted successfully",
#         "week_start": str(next_monday),
#         "total_preferences": len(records)
#     }
#
#
#
#
# @router.get("/next-week/{student_id}")
# def get_next_week_pref(
#     student_id: str,
#     db: Session = Depends(get_db)
# ):
#     prefs = get_next_week_preferences(student_id, db)
#
#     if not prefs:
#         raise HTTPException(
#             status_code=404,
#             detail="No preferences found for next week"
#         )
#
#     return prefs
#
#
#
# def get_next_week_preferences(student_id: str, db: Session):
#     today = date.today()
#
#     # 🧠 Calculate next Monday
#     days_until_monday = 7 - today.weekday()
#     next_monday = today + timedelta(days=days_until_monday)
#
#     preferences = db.query(MealPreference).filter(
#         MealPreference.student_id == student_id,
#         MealPreference.week_start == next_monday
#     ).all()
#
#     return preferences