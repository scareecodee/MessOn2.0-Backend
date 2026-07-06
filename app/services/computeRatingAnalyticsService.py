from typing import List
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import select

from app.models.mess.ratingAnalyticsModel import RatingAnalytics
from app.schemas.student.ratingSchema import RatingAnalyticsResponse
from app.utils.mealSlot import MealSlot
from app.utils.weekDays import WeekDays

IST = ZoneInfo("Asia/Kolkata")


async def get_rating_stats(
    db,
    mess_id,
    college_id,
    days: int = 1
) -> List[RatingAnalyticsResponse]:

    end_date = datetime.now(IST).date()
    start_date = end_date - timedelta(days=days - 1)

    stmt = (
        select(
            RatingAnalytics.date,
            RatingAnalytics.meal_slot,
            RatingAnalytics.veg_sum,
            RatingAnalytics.veg_count,
            RatingAnalytics.non_veg_sum,
            RatingAnalytics.non_veg_count,
            RatingAnalytics.total_sum,
            RatingAnalytics.total_count,
        )
        .filter(
            RatingAnalytics.mess_id == mess_id,
            RatingAnalytics.college_id == college_id,
            RatingAnalytics.date >= start_date,
            RatingAnalytics.date <= end_date,
        )
        .order_by(RatingAnalytics.date)
    )

    result = await db.execute(stmt)
    rows = result.all()

    
    data_map = {}

    for row in rows:
        if row.date not in data_map:
            data_map[row.date] = {}

        data_map[row.date][row.meal_slot] = row

    all_slots = list(MealSlot)

    response = []

    current = start_date

    while current <= end_date:

        slot_map = data_map.get(current, {})
        day = WeekDays(current.strftime("%A").lower())

        for slot in all_slots:

            row = slot_map.get(slot)

           
            veg_avg = (
                row.veg_sum / row.veg_count
                if row and row.veg_count else None
            )

            non_veg_avg = (
                row.non_veg_sum / row.non_veg_count
                if row and row.non_veg_count else None
            )

            total_avg = (
                row.total_sum / row.total_count
                if row and row.total_count else None
            )

            response.append(
                RatingAnalyticsResponse(
                    date=current,
                    day=day,
                    meal_slot=slot,
                    veg_avg=veg_avg,
                    non_veg_avg=non_veg_avg,
                    total_avg=total_avg,
                    max_rating=5
                )
            )

        current += timedelta(days=1)

    return response