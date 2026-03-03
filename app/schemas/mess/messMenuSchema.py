from pydantic import BaseModel
from uuid import UUID
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType


class MenuBase(BaseModel):
    day: str
    meal_slot: MealSlot
    meal_type: MealType
    menu_text: str


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    menu_text: str
    is_available: bool


class MenuResponse(BaseModel):
    menu_id: UUID
    day: str
    meal_slot: MealSlot
    meal_type: MealType
    menu_text: str
    is_available: bool

    class Config:
        from_attributes = True


class DayWiseMenuResponse(BaseModel):
    breakfast: dict[str, MenuResponse] | None = None
    lunch: dict[str, MenuResponse] | None = None
    dinner: dict[str, MenuResponse] | None = None
