from pydantic import BaseModel
from app.utils.weekDays import WeekDays
from app.utils.menuWeek import MenuWeek

class DayPolicyResponse(BaseModel):
    day: WeekDays
    is_compulsory: bool=True
    # menu_week: MenuWeek

    class Config:
        from_attributes = True