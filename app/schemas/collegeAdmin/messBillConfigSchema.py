from typing import Optional

from pydantic import BaseModel, EmailStr
from datetime import date

from app.utils.BillRangeType import BillRangeType


class PerDayMealPriceRequest(BaseModel):
    per_day_price: float
    start_date: date


class PerDayMealPriceResponse(BaseModel):
    # id: str
    per_day_price: float
    start_date: date
    end_date: date | None

class BillRequest(BaseModel):
    range_type: BillRangeType
    n_days: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class BillResponse(BaseModel):
     name: str
     email: EmailStr
     roll_no: str
     branch: str
     batch: int
     total_bill_days: int
     bill_start_date : date
     bill_end_date : date
     total_bill : float
