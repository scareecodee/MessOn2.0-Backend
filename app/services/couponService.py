import time
from datetime import datetime, date, timedelta
from app.schemas.couponPayloadSchema import CouponPayload
from app.security.couponSignature import sign_payload
from app.models.couponModel import MealType
from app.core.config import get_settings

settings=get_settings()

MEAL_EXPIRY = {
    MealType.BREAKFAST: settings.breakfast_expire,  
    MealType.LUNCH: settings.lunch_expire,      
    MealType.DINNER: settings.dinner_expire      
}


def build_coupon_payload(
    *,
    coupon_id: str,
    user_id: str,
    coupon_date: date,
    meal: MealType
) -> CouponPayload:

    issued_at = int(time.time())

    expiry_time = datetime.combine(
        coupon_date,
        datetime.min.time()
    ) + timedelta(hours=MEAL_EXPIRY[meal])

    expiry_epoch = int(expiry_time.timestamp())

    unsigned = f"1|{coupon_id}|{user_id}|{coupon_date}|{meal.value}|{issued_at}|{expiry_epoch}"

    signature = sign_payload(unsigned)

    return CouponPayload(
        v=1,
        cid=coupon_id,
        uid=user_id,
        d=coupon_date,
        m=meal.value,
        iat=issued_at,
        exp=expiry_epoch,
        sig=signature
    )
