from pydantic import BaseModel
from app.utils.mealSlot import MealSlot
from app.utils.weekDays import WeekDays


class MealAvailability(BaseModel):
    day:WeekDays
    meal_slot:MealSlot
    veg_available:bool
    nonVeg_available:bool