# app/schemas/meal_slot_expiry.py

# from pydantic import BaseModel
# from datetime import time
# from app.utils.mealSlot import MealSlot
#
#
# class MealSlotExpiryRequest(BaseModel):
#     meal_slot: MealSlot
#     start_time: time
#     end_time: time
#
#
# class MealSlotExpiryResponse(BaseModel):
#     meal_slot: MealSlot
#     start_time: time
#     end_time: time
#
#     class Config:
#         from_attributes = True
#

# app/schemas/meal_slot_expiry.py

from pydantic import BaseModel
from datetime import time
from app.utils.mealSlot import MealSlot


class MealSlotExpiryRequest(BaseModel):
    meal_slot: MealSlot
    start_time: time
    end_time: time


class MealSlotExpiryResponse(BaseModel):
    meal_slot: MealSlot
    start_time: time
    end_time: time

    class Config:
        from_attributes = True