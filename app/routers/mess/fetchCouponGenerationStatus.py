from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.couponGenerationStatus import CouponGenerationStatus
from app.schemas.mess.couponResponseSchema import CouponGenerationResponse
from app.services.couponGenerationStatusService import get_current_week_coupon_generation_status


router = APIRouter(
    prefix="/fetch",
    tags=["Manage Mess Day Policy"]
)


@router.get(
    "/coupon-generation-status",
    response_model=CouponGenerationResponse
)
async def get_coupon_generation_status(
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MessAdmin).where(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        )
    )

    mess_admin = result.scalar_one_or_none()

    if not mess_admin:
        raise HTTPException(
            status_code=404,
            detail="Mess admin not found"
        )

    return await get_current_week_coupon_generation_status(
        db=db,
        mess_id=mess_admin.mess_id,
        college_id=current_user.college_id
    )