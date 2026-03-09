from pydantic import BaseModel
from app.utils.weekDay import WeekDay
from app.utils.menuWeek import MenuWeek

class DayPolicyResponse(BaseModel):
    day: WeekDay
    is_compulsory: bool=True
    # menu_week: MenuWeek

    class Config:
        from_attributes = True