from typing import List

from sqlalchemy import select, func, case
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.models.mess.couponModel import Coupon
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.schemas.mess.couponScanAnalyticsSchema import ScannedCouponResponse
from app.services.mealPreferenceCountService import get_meal_preference_counts
from app.utils.weekDays import WeekDays

IST = ZoneInfo("Asia/Kolkata")


async def get_scan_stats(
    db,
    mess_id,
    college_id,
    days: int = 1
)-> List[ScannedCouponResponse]:

    end_date = datetime.now(IST).date()
    start_date = end_date - timedelta(days=days - 1)

    stmt = (
        select(
            Coupon.date,
            Coupon.meal_slot,

            func.count(
                case((Coupon.meal_type == MealType.veg, 1))
            ).label("veg_count"),

            func.count(
                case((Coupon.meal_type == MealType.nonVeg, 1))
            ).label("non_veg_count"),

            func.count(Coupon.id).label("total_count")
        )
        .filter(
            Coupon.mess_id == mess_id,
            Coupon.college_id == college_id,
            Coupon.date >= start_date,
            Coupon.date <= end_date,
            Coupon.scanned_at.is_not(None)
        )
        .group_by(Coupon.date, Coupon.meal_slot)
        .order_by(Coupon.date)
    )

    result = await db.execute(stmt)
    rows = result.all()

    data_map = {}

    for row in rows:
        if row.date not in data_map:
            data_map[row.date] = {}

        data_map[row.date][row.meal_slot] = row

    total_coupon_count_queries = (
        select(
            Coupon.date,
            Coupon.meal_slot,

            func.count(
                case((Coupon.meal_type == MealType.veg, 1))
            ).label("total_veg_count"),

            func.count(
                case((Coupon.meal_type == MealType.nonVeg, 1))
            ).label("total_non_veg_count"),

        )
        .filter(
            Coupon.mess_id == mess_id,
            Coupon.college_id == college_id,
            Coupon.date >= start_date,
            Coupon.date <= end_date,
        )
        .group_by(Coupon.date, Coupon.meal_slot)
        .order_by(Coupon.date)
    )

    coupons = await db.execute(total_coupon_count_queries)
    coupons = coupons.all()

    all_slots = list(MealSlot)

    total_coupon_counts_data_map = {}

    for coupon_count in coupons :
        if coupon_count.date not in total_coupon_counts_data_map :
            total_coupon_counts_data_map[coupon_count.date] = {}

        total_coupon_counts_data_map[coupon_count.date][coupon_count.meal_slot] = coupon_count

    response = []

    current = start_date
    while current <= end_date:

        slot_map = data_map.get(current, {})
        coupon_count_map = total_coupon_counts_data_map.get(current, {})
        day= WeekDays(current.strftime("%A").lower())

        for slot in all_slots:
            row = slot_map.get(slot)
            coupon_count_row = coupon_count_map.get(slot)

            response.append(
                ScannedCouponResponse(
                    date=current,
                    day=day,
                    meal_slot=slot,
                    scanned_veg_count=row.veg_count if row else 0,
                    total_veg_count=coupon_count_row.total_veg_count if coupon_count_row else 0,
                    scanned_non_veg_count=row.non_veg_count if row else 0,
                    total_non_veg_count=coupon_count_row.total_non_veg_count if coupon_count_row else 0,
                    total_scanned_count=row.total_count if row else 0,
                )
            )

        current += timedelta(days=1)


    return response