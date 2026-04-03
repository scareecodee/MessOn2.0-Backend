from uuid import UUID

from pydantic import BaseModel,field_serializer
from datetime import datetime
from datetime import date
from typing import Optional

class MessClosureUpdateRequest(BaseModel):
    closure_id: UUID
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None


class MessClosureRequest(BaseModel):
    start_date: date
    end_date: date
    reason: str


class MessClosureResponse(BaseModel):
    closure_id: UUID
    start_date: date
    end_date: date
    reason: str

    class Config:
        from_attributes = True

    # @field_serializer("start_time", "end_time")
    # def serialize_dt(self, value: datetime):
    #      return value.strftime("%Y-%m-%d")