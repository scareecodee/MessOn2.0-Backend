from pydantic import BaseModel
from datetime import date

from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.weekDays import WeekDays


class ScannedCouponResponse(BaseModel):
    date: date
    day:WeekDays
    meal_slot: MealSlot
    scanned_veg_count: int
    total_veg_count: int
    scanned_non_veg_count: int
    total_non_veg_count: int
    total_scanned_count: int
