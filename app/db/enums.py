from sqlalchemy import Enum as SAEnum, Enum
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.weekDays import WeekDays
from app.utils.menuWeek import MenuWeek

# native_enum=True — uses PostgreSQL native ENUM type
# more efficient than VARCHAR with check constraints
meal_slot_enum:Enum = SAEnum(MealSlot, name="meal_slot_enum", native_enum=True)
meal_type_enum  = SAEnum(MealType, name="meal_type_enum", native_enum=True)
weekday_enum = SAEnum(WeekDays, name="weekday_enum", native_enum=True)
menu_week_enum = SAEnum(MenuWeek, name="menu_week_enum", native_enum=True)