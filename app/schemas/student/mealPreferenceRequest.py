from datetime import date
from pydantic import BaseModel
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from typing import List
from app.utils.weekDays import WeekDays

class MealPreferenceItem(BaseModel):
    day: WeekDays
    meal_slot: MealSlot
    preference: MealType


class WeeklyMealPreferenceCreate(BaseModel):
    student_id: str
    week_start: date
    preferences: List[MealPreferenceItem]


from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional

from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.weekDays import WeekDays


class MealPreferenceRequest(BaseModel):
    day:WeekDays
    meal_slot: MealSlot
    meal_type: Optional[MealType] = None  # None allowed for optional days
