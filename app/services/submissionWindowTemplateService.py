from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from app.utils.weekDayOrder import WEEKDAY_ORDER

IST = ZoneInfo("Asia/Kolkata")


def build_window_from_template(template, week):


    def resolve_date(start_date, target_day):
        start_index = start_date.weekday()
        target_index = WEEKDAY_ORDER[target_day.value]

        delta = (target_index - start_index) % 7
        return start_date + timedelta(days=delta)

    start_date = resolve_date(week.start_date, template.start_day)
    end_date = resolve_date(week.start_date, template.end_day)

    start_ist = datetime.combine(start_date, template.start_time, tzinfo=IST)
    end_ist = datetime.combine(end_date, template.end_time, tzinfo=IST)

    if start_ist >= end_ist:
        raise ValueError("Invalid template window (start >= end)")

    start_utc = start_ist.astimezone(timezone.utc)
    end_utc = end_ist.astimezone(timezone.utc)

    return start_utc, end_utc