from pydantic import BaseModel
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.menuWeek import MenuWeek
from app.utils.weekDay import WeekDay


class CreateMenu(BaseModel):
    day: WeekDay
    meal_slot: MealSlot
    meal_type: MealType
    dishes: str
    # menu_week: MenuWeek