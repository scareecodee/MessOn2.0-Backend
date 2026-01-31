from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.db.session import get_db
from app.models.couponModel import Coupon, MealType
from app.services.couponService import build_coupon_payload
from app.models.studentModel import Student
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/coupons",
    tags=["Coupons"]
    )


@router.get("/today")
def get_today_coupons(
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    today = date.today()

    coupons = (
        db.query(Coupon)
        .filter(
            Coupon.user_id == current_user.id,
            Coupon.date == today
        )
        .all()
    )

    payloads = []

    for coupon in coupons:
        payloads.append(
            build_coupon_payload(
                coupon_id=str(coupon.id),
                user_id=str(current_user.id),
                coupon_date=coupon.date,
                meal=coupon.meal
            )
        )

    print(payloads)

    return payloads
