from datetime import datetime, date, time
from zoneinfo import ZoneInfo

from app.models.mess.couponModel import MealType
from app.core.config import get_settings
from app.utils.mealSlot import MealSlot

settings = get_settings()

IST = ZoneInfo("Asia/Kolkata")

MEAL_EXPIRY_MAP: dict[MealType, str] = {
    MealSlot.breakfast: settings.breakfast_expire,  # "11:00"
    MealSlot.lunch: settings.lunch_expire,          # "15:00"
    MealSlot.dinner: settings.dinner_expire,        # "22:00"
}


def compute_expiry_epoch(
    *,
    meal_date: date,
    meal: MealType,
) -> int:
    """
    Expiry = meal_date + fixed meal clock time (IST).
    Independent of scheduler run time.
    Stored as UTC epoch.
    """

    expiry_str = MEAL_EXPIRY_MAP[meal]
    hour, minute = map(int, expiry_str.split(":"))

    # Create local datetime (IST)
    expiry_local_dt = datetime.combine(
        meal_date,
        time(hour=hour, minute=minute),
        tzinfo=IST,
    )

    #  Convert to UTC epoch
    return int(expiry_local_dt.timestamp())

