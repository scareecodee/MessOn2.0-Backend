from uuid import UUID

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date,datetime,time
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.db.enums import meal_slot_enum,meal_type_enum


class CouponPayload(BaseModel):
    coupon_id: UUID
    student_id: UUID
    mess_id: UUID
    college_id: UUID
    date: date
    meal_slot: MealSlot
    meal_type: MealType
    scanned_at: datetime | None
    signature: str

    class Config:
        from_attributes = True

class QrResponseSchema(BaseModel):
    valid:bool

class QrExpired(BaseModel):
    expired:bool
    
class QrUsed(BaseModel):
    markedAsTrue:bool=False
    



