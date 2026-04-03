from pydantic import BaseModel
from app.utils.weekDays import WeekDay

class FetchDayPolicy(BaseModel):
    day: WeekDay
    is_compulsory: bool=True