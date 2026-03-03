from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.mess.couponAnalytics import CouponCount
from app.schemas.mess.messAdminDashboardSchema import TotalCouponsGenerated,TotalScannedCoupon
from app.models.mess.couponModel import Coupon, MealType
from datetime import datetime
from zoneinfo import ZoneInfo


router = APIRouter(
    prefix="/mess-admin/dashboard",
    tags=["Mess Admin Dashboard"]
)


@router.get("/total-coupons-count", response_model=TotalCouponsGenerated)
def get_total_students_with_coupons(
    db: Session = Depends(get_db),
):
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()

    total_students = (
        db.query(func.count(func.distinct(Coupon.user_id)))
        .filter(Coupon.date == today)
        .scalar()
    )

    return TotalCouponsGenerated(
        total_coupon_count=total_students
    )




@router.get("/scanned-coupons-count",response_model=TotalScannedCoupon)
def get_scanned_coupons_count(
    db: Session = Depends(get_db),
    # current_admin=Depends(get_current_admin)
):
 

    current_date = datetime.now(ZoneInfo("Asia/Kolkata")).date()

    breakfastCount=0
    lunchCount=0
    dinnerCount=0

    rows = (
        db.query(CouponCount)
        .filter(CouponCount.date ==current_date)
        .all()
    )

    for row in rows:
       if(row.meal_type==MealType.breakfast):
           breakfastCount=row.count
       if(row.meal_type==MealType.lunch):
           lunchCount=row.count 
       if(row.meal_type==MealType.dinner):
           dinnerCount=row.count
    
    return TotalScannedCoupon(
        breakfastCount=breakfastCount,
        lunchCount=lunchCount,
        dinnerCount=dinnerCount
    )