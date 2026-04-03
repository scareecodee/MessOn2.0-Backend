# app/services/dateResolverService.py

from datetime import timedelta
from fastapi import HTTPException
from app.utils.weekDays import WeekDays
from app.utils.weekDayOrder import WEEKDAY_ORDER


async def resolve_date_from_day(week, day: WeekDays):
    start_weekday = week.start_date.weekday()  # 0=Mon
    target_weekday = WEEKDAY_ORDER[day.value]

    offset = (target_weekday - start_weekday) % 7
    target_date = week.start_date + timedelta(days=offset)

    # if not (week.start_date <= target_date <= week.end_date):
        # raise HTTPException(400, f"{day.value} not in this week")


    return target_date