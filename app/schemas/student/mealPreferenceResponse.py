from pydantic import BaseModel
from app.utils.mealSlot import MealSlot
from app.utils.weekDays import WeekDays
from app.utils.mealType import MealType
from app.schemas.mess.mealAvailability import MealAvailability

class MealPreferenceResponse(BaseModel):
    day: WeekDays
    meal_slot: MealSlot
    veg_dishes:str | None
    nonVeg_dishes:str |None
    veg_available: bool
    nonVeg_available: bool
    is_compulsory:bool

    class Config:
        from_attributes=True