from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime, date
from uuid import UUID

from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType


class CouponResponse(BaseModel):
    id: UUID
    student_id: UUID
    mess_id: UUID
    date: date
    meal_slot: MealSlot
    meal_type: MealType
    expires_at: datetime
    scanned_at: datetime | None

    class Config:
        from_attributes = True


class ErrorDetail(BaseModel):
    code: int
    message: str

class ScanCouponResponse(BaseModel):
    student_name: str
    roll_no: str
    branch: str
    meal_slot: str
    meal_type: str
    scanned_at: Optional[datetime]
    # scanned_at: datetime
    success: bool
    errors: List[ErrorDetail] = Field(default_factory=list)

    @field_serializer("scanned_at")
    def serialize_scanned_at(self, value):
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class ServiceException(HTTPException):
    def __init__(self, errors: list[ErrorDetail]):
        self.errors = errors
        super().__init__(
            status_code=400,
            detail=[e.dict() for e in errors]
        )


class CouponExpiryResponse(BaseModel):
    meal_slot: MealSlot
    is_expired: bool