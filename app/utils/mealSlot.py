import enum


class MealSlot(str, enum.Enum):
    breakfast= "breakfast"
    lunch = "lunch"
    dinner = "dinner"

