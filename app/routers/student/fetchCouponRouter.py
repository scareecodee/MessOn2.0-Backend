from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import time
from app.db.session import get_db
from app.models.mess.couponModel import MealType
from app.models.student.studentModel import Student
from app.security.dependencies import get_current_user
from app.services.couponQueryService import fetch_coupon_by_meal
import app.security.dependencies as security_module
from app.utils.mealSlot import MealSlot

router = APIRouter(
    prefix="/coupons",
     tags=["Fetch Meal-wise Coupons"],
         dependencies=[Depends(security_module.security)]
     )



@router.get("/today/breakfast")
def get_breakfast_coupon(
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):

    coupon = fetch_coupon_by_meal(db, current_user, MealSlot.breakfast)
    if not coupon:
        raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail="Breakfast coupon not found",
)
    print(coupon)
    return coupon


@router.get("/today/lunch")
def get_lunch_coupon(
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    coupon = fetch_coupon_by_meal(db, current_user, MealSlot.lunch)
    if not coupon:
        raise HTTPException(
                             status_code=404,
                             detail="Lunch coupon not found",
)
    print(coupon)
    return coupon


@router.get("/today/dinner")
def get_dinner_coupon(
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    print(current_user.name)
    coupon = fetch_coupon_by_meal(db, current_user, MealSlot.dinner)


    now_epoch = int(time.time())
    if coupon and coupon.expiresAt < now_epoch:
        print("coupon found:", coupon)

    if not coupon:
        raise HTTPException(
        status_code=404,
        detail="Dinner coupon not found",
)

    print(coupon)
    
    return coupon
