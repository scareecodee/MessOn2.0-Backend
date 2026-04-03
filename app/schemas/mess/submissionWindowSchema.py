from pydantic import BaseModel,field_serializer
from datetime import datetime
from uuid import UUID


class SubmissionWindowRequest(BaseModel):
    start_time: datetime
    end_time: datetime


class SubmissionWindowResponse(BaseModel):
    start_time: datetime | None
    end_time: datetime | None
    is_active: bool


    @field_serializer("start_time", "end_time")
    def serialize_dt(self, value: datetime):
         return value.strftime("%Y-%m-%d %H:%M")

    class Config:
        from_attributes = True
