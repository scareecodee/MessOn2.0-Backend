from app.services.weekResolverService import resolve_week
from app.utils.menuWeek import MenuWeek
from app.utils.couponGenerationStatus import CouponGenerationStatus
from app.schemas.mess.couponResponseSchema import CouponGenerationResponse


async def get_current_week_coupon_generation_status(
    db,
    mess_id,
    college_id
):
    week = await resolve_week(
        db=db,
        menu_week=MenuWeek.currentWeek,
        mess_id=mess_id,
        college_id=college_id
    )

    return CouponGenerationResponse(
    coupon_generation_status=CouponGenerationStatus(
        week.coupon_generation_status
    )
)
