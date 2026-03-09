from datetime import date
from pydantic import BaseModel
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from typing import List
from app.utils.weekDay import WeekDays

class MealPreferenceItem(BaseModel):
    day: WeekDays
    meal_slot: MealSlot
    preference: MealType


class WeeklyMealPreferenceCreate(BaseModel):
    student_id: str
    week_start: date
    preferences: List[MealPreferenceItem]