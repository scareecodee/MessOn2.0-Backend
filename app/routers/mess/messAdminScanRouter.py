from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import time
from app.security.dependencies import get_current_admin
from app.db.session import get_db
from app.models.mess.couponModel import Coupon
from app.schemas.mess.couponPayloadSchema import CouponPayload,QrResponseSchema, QrUsed
from app.security.couponSignature import verify_payload_signature

router = APIRouter(
    prefix="/admin/coupons",
    tags=["Mess Admin Coupon Scan"],
)


@router.post("/verify", status_code=status.HTTP_200_OK)
def verify_coupon(
    payload: CouponPayload,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    print("entering")
    # Verify payload signature (integrity check)
    expected_signature = verify_payload_signature(payload)
    if expected_signature != payload.signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid coupon signature",
        )
    print("signature is valid")

    # Lock coupon row (prevents double scan)
    coupon = (
        db.query(Coupon)
        .filter(Coupon.id == payload.coupon_id)
        .with_for_update()
        .first()
    )

    if coupon is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found",
        )
    print("Coupon is in DB")

    now_epoch = int(time.time())
    
    # Expired → reject (derived, NOT stored)
    if now_epoch > coupon.expiresAt:
        # raise HTTPException(
        #     status_code=status.HTTP_410_GONE,
        #     detail="Coupon expired",
        # )
        return QrResponseSchema(
            valid=False
    )
    if coupon.used_at is not None:
            coupon.used_at = now_epoch
            return QrResponseSchema(
        valid=False
    )

    # Valid scan → mark as used (epoch)
    # coupon.used_at = now_epoch
    db.commit()
    db.refresh(coupon)

    return QrResponseSchema(
       valid=True
    )

@router.post("/mark-as-used", status_code=status.HTTP_200_OK)
def mark_coupon_as_used(
    payload: CouponPayload,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    now_epoch = int(time.time())

    # Lock coupon row
    coupon = (
        db.query(Coupon)
        .filter(Coupon.id == payload.coupon_id)
        .with_for_update()
        .first()
    )

    if coupon is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found",
        )

    # If already scanned → do nothing
    if coupon.used_at is not None:
        print("inside coupon.used")
        # return QrUsed(markedAsTrue=True)
        coupon.used_at = now_epoch
        db.commit()
        return QrUsed(markedAsTrue=True)

    # Mark coupon as used
    # coupon.used_at = now_epoch

    # # Update analytics table
    # coupon_count = (
    #     db.query(CouponCount)
    #     .filter(
    #         CouponCount.date == coupon.date,
    #         CouponCount.meal_type == coupon.meal,
    #     )
    #     .with_for_update()
    #     .first()
    # )

    # if coupon_count:
    #     coupon_count.count += 1
    # else:
    #     coupon_count = CouponCount(
    #         date=coupon.date,
    #         meal_type=coupon.meal,
    #         count=1
    #     )
    #     db.add(coupon_count)


    return QrUsed(markedAsTrue=True)
