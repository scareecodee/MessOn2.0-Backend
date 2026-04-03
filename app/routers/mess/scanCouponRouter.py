from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.services.couponQueryService import fetch_coupon_by_meal
from app.services.couponScanService import scan_coupon
from app.utils.mealSlot import MealSlot
from app.utils.userRole import UserRole
from app.security.dependencies.getCurrentRole import get_current_role
from app.schemas.mess.couponPayloadSchema import CouponPayload
from app.security.couponSignature import verify_payload_signature

router = APIRouter(
    prefix="/coupons",
    tags=["Scan Coupons"]
    )

@router.post("/scan")
async def scan_coupon_route(
    payload:CouponPayload,
    current_user = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db)
):
    scanned_by=current_user.id
    result = await scan_coupon(db, payload,scanned_by)

    print("after scan func")

    if not result:
        raise HTTPException(400, "error error")

    # if "error" in result:
    #     raise HTTPException(400, result["error"])

    return result

@router.post("/verify")
async def verify_coupon(
    payload:CouponPayload,
    current_user = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db)
):
    scanned_by=current_user.id
    result =  verify_payload_signature(payload)

    if not result:
        raise HTTPException(400, "Invalid Signature")

    if "error" in result:
        raise HTTPException(400, result["error"])

    return result


