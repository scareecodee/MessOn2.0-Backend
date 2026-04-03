# app/schemas/student/mealPreferenceRequest.py

from pydantic import BaseModel
from datetime import date
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType


class MealPreferenceRequest(BaseModel):
    date: date
    meal_slot: MealSlot
    meal_type: MealType | None