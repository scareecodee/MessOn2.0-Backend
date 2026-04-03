from pydantic import BaseModel
from app.utils.mealSlot import MealSlot
from app.utils.weekDays import WeekDays
from app.utils.mealType import MealType

class CreateMealPreference(BaseModel):

    day:WeekDays
    meal_slot:MealSlot
    meal_type:MealType