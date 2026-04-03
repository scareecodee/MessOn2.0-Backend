# app/schemas/mess/mealCountResponse.py

from pydantic import BaseModel
from datetime import date
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.weekDays import WeekDays

class MealSlotCount(BaseModel):
    veg_count: int | None
    non_veg_count: int | None

class MealCountResponse(BaseModel):
    date: date
    day : str
    breakfast : MealSlotCount
    lunch: MealSlotCount
    dinner : MealSlotCount