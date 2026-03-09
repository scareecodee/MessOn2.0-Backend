from pydantic import BaseModel,Field
from uuid import UUID
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.menuWeek import MenuWeek
from app.utils.weekDay import WeekDay


class MenuUpdate(BaseModel):
    menu_dishes: str
    is_available: bool


class MenuResponse(BaseModel):
    menu_id: UUID
    day: WeekDay
    meal_slot: MealSlot
    meal_type: MealType
    dishes: str
    # menu_week: MenuWeek

    class Config:
        from_attributes = True

class DayWiseMenuResponse(BaseModel):
    breakfast: dict[str, MenuResponse] = Field(default_factory=dict)
    lunch: dict[str, MenuResponse] = Field(default_factory=dict)
    dinner: dict[str, MenuResponse] = Field(default_factory=dict)