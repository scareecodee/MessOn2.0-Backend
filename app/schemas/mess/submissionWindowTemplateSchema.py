# app/schemas/mess/submissionWindowTemplateSchema.py

from pydantic import BaseModel
from datetime import time
from app.utils.weekDays import WeekDays


class SubmissionWindowTemplateRequest(BaseModel):
    start_day: WeekDays
    start_time: time
    end_day: WeekDays
    end_time: time


class SubmissionWindowTemplateResponse(BaseModel):
    start_day: WeekDays | None
    start_time: time | None
    end_day: WeekDays | None
    end_time: time | None