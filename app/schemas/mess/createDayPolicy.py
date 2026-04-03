from pydantic import BaseModel
from app.utils.weekDays import WeekDays

class CreateDayPolicy(BaseModel):
    day: WeekDays
    is_compulsory: bool=True
