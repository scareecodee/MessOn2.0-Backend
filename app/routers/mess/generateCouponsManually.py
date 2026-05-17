# from typing import Optional
#
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
#
# from app.db.session import get_db, AsyncSessionLocal
# from app.models.user.userModel import User
# from app.models.mess.messAdmin import MessAdmin
# from app.models.mess.messWeekModel import MessWeek
#
# from app.security.dependencies.getCurrentRole import get_current_role
# from app.utils.userRole import UserRole
#
# from app.services.couponGenerationService import generate_coupons_for_week
#
# from datetime import datetime
# from zoneinfo import ZoneInfo
#
# from app.services.messWeekGenerationService import generate_weeks_for_mess
# from app.services.weekResolverService import resolve_week
# from app.utils.menuWeek import MenuWeek
#
# IST = ZoneInfo("Asia/Kolkata")
#
# router = APIRouter(
#     prefix="/admin/coupons",
#     tags=["Generate Coupons Manually"]
# )
#
# @router.post("/generate-manually")
# async def generate_coupons_manual(
#     current_user: User = Depends(get_current_role([UserRole.mess_admin])),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(
#         select(MessAdmin).filter(
#             MessAdmin.user_id == current_user.id,
#             MessAdmin.college_id == current_user.college_id
#         )
#     )
#     mess_admin = result.scalar_one_or_none()
#
#     if not mess_admin:
#         raise HTTPException(404, "Mess admin not found")
#
#     mess_id = mess_admin.mess_id
#     college_id = current_user.college_id
#
#     today = datetime.now(IST).date()
#
#     result = await db.execute(
#         select(MessWeek).filter(
#             MessWeek.mess_id == mess_id,
#             MessWeek.start_date <= today,
#             MessWeek.end_date >= today
#         )
#     )
#
#     week : Optional[MessWeek] = result.scalar_one_or_none()
#
#     if week is None:
#         await resolve_week(
#             db=db,
#             menu_week=MenuWeek.currentWeek,
#             mess_id=mess_id,
#             college_id=college_id
#         )
#         # await generate_weeks_for_mess(
#         #     db=db,
#         #     mess_id=mess_id,
#         #     college_id=college_id,
#         # )
#
#         # raise HTTPException(404, "No active week found")
#     #
#     # if week.coupon_generation_status == "generated":
#     #     return {
#     #         "status": "already_generated",
#     #         "week_id": str(week.id)
#     #     }
#     #
#     # if week.coupon_generation_status == "skipped":
#     #     return {
#     #         "status": "skipped_week",
#     #         "reason": "mess closed entire week"
#     #     }
#
#     try:
#         async with AsyncSessionLocal() as db:
#             await generate_coupons_for_week(db, mess_id, college_id)
#     except Exception as e:
#         raise HTTPException(500, f"Generation failed: {str(e)}")
#
#     return {
#         "status": "generation_triggered",
#         "week_id": str(week.id)
#     }



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.mess.messAdmin import MessAdmin
from app.models.user.userModel import User

from app.security.dependencies.getCurrentRole import get_current_role
from app.services.couponGenerationService import generate_coupons_for_week
from app.services.weekResolverService import resolve_week

from app.utils.menuWeek import MenuWeek
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/admin/coupons",
    tags=["Generate Coupons"]
)


@router.post("/generate-manually")
async def generate_coupons_manual(
    current_user: User = Depends(
        get_current_role([UserRole.mess_admin])
    ),
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

    mess_id = mess_admin.mess_id
    college_id = current_user.college_id

    week = await resolve_week(
        db=db,
        menu_week=MenuWeek.currentWeek,
        mess_id=mess_id,
        college_id=college_id
    )

    try:

        await generate_coupons_for_week(
            db=db,
            mess_id=mess_id,
            college_id=college_id
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )

    return {
        "status": "generation_triggered",
        "week_id": str(week.id)
    }