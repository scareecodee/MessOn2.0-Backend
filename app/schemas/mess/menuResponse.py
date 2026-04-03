from pydantic import BaseModel,Field
from uuid import UUID
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.menuWeek import MenuWeek
from app.utils.weekDays import WeekDays



class MenuResponse(BaseModel):
    # menu_id: UUID
    day: WeekDays
    meal_slot: MealSlot
    meal_type: MealType
    dishes: str
    # menu_week: MenuWeek

    class Config:
        from_attributes = True

class SlotMenu(BaseModel):
    veg: MenuResponse | None = None
    nonVeg: MenuResponse | None = None

class DayMenu(BaseModel):
    breakfast: SlotMenu = SlotMenu()
    lunch: SlotMenu = SlotMenu()
    dinner: SlotMenu = SlotMenu()

class WeeklyMenuResponse(BaseModel):
    monday: DayMenu = DayMenu()
    tuesday: DayMenu = DayMenu()
    wednesday: DayMenu = DayMenu()
    thursday: DayMenu = DayMenu()
    friday: DayMenu = DayMenu()
    saturday: DayMenu = DayMenu()
    sunday: DayMenu = DayMenu()