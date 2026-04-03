# app/api/routes/coupon.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.couponQueryService import fetch_coupon_by_meal
from app.models.user.userModel import User
from app.models.student.studentModel import Student
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.mealSlot import MealSlot
from app.schemas.mess.couponPayloadSchema import CouponPayload
from app.models.mess.couponModel import Coupon

router = APIRouter(
    prefix="/fetch",
    tags=[" Fetch Coupons"]
    )

@router.get("/coupons/{meal_slot}",response_model=CouponPayload)
async def get_coupon(
    meal_slot: MealSlot,
    current_user: User = Depends(get_current_role([UserRole.student])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Student).filter(
            Student.user_id == current_user.id,
            Student.college_id == current_user.college_id,
        )
    )

    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(404, "Student profile not found")

    coupon = await fetch_coupon_by_meal(
        db=db,
        student_id=student.user_id,
        mess_id=student.mess_id,
        college_id=current_user.college_id,
        meal_slot=meal_slot
    )

    if not coupon:
        raise HTTPException(404, "Coupon not available")

    return coupon