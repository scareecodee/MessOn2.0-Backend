from datetime import datetime, timedelta, date, timezone
from zoneinfo import ZoneInfo
from app.utils.menuWeek import MenuWeek

IST = ZoneInfo("Asia/Kolkata")

def get_sunday_midnight_utc(menu_week: MenuWeek) -> datetime:

    today = date.today()
    days_until_sunday = (6 - today.weekday()) % 7

    # if today is Sunday, days_until_sunday = 0 — that's correct, today is the limit
    if menu_week == MenuWeek.nextWeek:
        days_until_sunday += 7

    target_sunday = today + timedelta(days=days_until_sunday)

    sunday_end_ist = datetime(
        target_sunday.year,
        target_sunday.month,
        target_sunday.day,
        23, 59, 59,
        tzinfo=IST
    )

    return sunday_end_ist.astimezone(timezone.utc)