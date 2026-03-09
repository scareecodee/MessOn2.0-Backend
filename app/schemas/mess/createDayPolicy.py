from pydantic import BaseModel
from app.utils.weekDay import WeekDay

class CreateDayPolicy(BaseModel):
    day: WeekDay
    is_compulsory: bool=True
