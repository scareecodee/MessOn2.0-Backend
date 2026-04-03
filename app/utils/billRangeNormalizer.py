from datetime import date, timedelta
from fastapi import HTTPException

def normalize_billing_range(
    *,
    range_type,
    n_days: int | None,
    start_date: date | None,
    end_date: date | None,
    mess_start_date: date
) -> tuple[date, date]:

    today = date.today()

    if range_type == "last_n_days":
        if not n_days or n_days <= 0:
            raise HTTPException(400, "n_days must be positive")

        end_date = today
        start_date = today - timedelta(days=n_days - 1)

    elif range_type == "custom":
        if not start_date:
            raise HTTPException(400, "start_date is required")

        end_date = end_date or today

    else:
        raise HTTPException(400, "Invalid range_type")

    if start_date < mess_start_date:
        start_date = mess_start_date
    else:
        start_date = start_date

    # start_date = max(start_date, mess_start_date)
    end_date = min(end_date, today)

    if start_date > end_date:
        raise HTTPException(400, "No valid billing range after normalization")

    return start_date, end_date