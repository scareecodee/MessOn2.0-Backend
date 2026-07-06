from pydantic import BaseModel,Field
from datetime import date
from uuid import UUID

from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.weekDays import WeekDays


class RatingRequest(BaseModel):
    meal_slot: MealSlot
    rating: int = Field(ge=1, le=5)

class RatingAnalyticsResponse(BaseModel):
    date: date
    day: WeekDays
    meal_slot: MealSlot
    veg_avg: float | None
    non_veg_avg: float | None
    total_avg: float | None
    max_rating: int