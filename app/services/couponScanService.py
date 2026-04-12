from time import timezone
from typing import Optional

from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from uuid import UUID
from fastapi import Response

from app.models.mess.couponModel import Coupon
from app.models.student.studentModel import Student
from app.models.user.userModel import User
from app.models.mess.mealSlotExpiryModel import MealSlotExpiry

from app.security.couponSignature import sign_payload
from app.services.messClosureService import is_mess_closed
from app.schemas.mess.couponPayloadSchema import CouponPayload
from app.security.couponSignature import verify_payload_signature
from app.schemas.mess.couponResponseSchema import ScanCouponResponse, ServiceException, ErrorDetail

IST = ZoneInfo("Asia/Kolkata")
response = Response()

async def scan_coupon(
    db: AsyncSession,
    payload: CouponPayload,
    scanned_by: UUID
) -> ScanCouponResponse:

    print(payload.coupon_id)

    errors = []

    if not verify_payload_signature(payload):
        errors.append(ErrorDetail(code=401, message="Invalid signature"))

    result = await db.execute(
        select(Coupon).where(
            Coupon.id == payload.coupon_id,
            Coupon.college_id == payload.college_id,
            Coupon.mess_id == payload.mess_id,
            Coupon.student_id == payload.student_id,
        )
    )
    coupon : Optional[Coupon] = result.scalar_one_or_none()


    if not coupon:
        errors.append(ErrorDetail(code=404, message="Coupon not found"))
        raise HTTPException(status_code=404, detail="Coupon not found")

    students = await db.execute(
        select(Student, User)
        .join(User, User.id == Student.user_id)
        .where(
            Student.user_id == coupon.student_id,
            User.is_active == True,
        )
    )

    # student, user = result.one()

    row = students.one_or_none()

    if not row:
        raise HTTPException(status_code=404, detail="Student not found")

    student, user = row

    # if coupon.student_id != payload.student_id:
    #     errors.append(ErrorDetail(code=401, message="Invalid student"))
    #
    # if coupon.mess_id != payload.mess_id:
    #     errors.append(ErrorDetail(code=401, message="Invalid mess"))
    #
    # if coupon.college_id != payload.college_id:
    #     errors.append(ErrorDetail(code=401, message="Invalid college"))

    if coupon.date.isoformat() != payload.date.isoformat():
        errors.append(ErrorDetail(code=401, message="Invalid date"))

    if coupon.meal_type.value != payload.meal_type.value:
        errors.append(ErrorDetail(code=401, message="Invalid meal type"))

    if coupon.meal_slot.value != payload.meal_slot.value:
        errors.append(ErrorDetail(code=401, message="Invalid meal slot"))

    if await is_mess_closed(db, coupon.mess_id, coupon.date):
        errors.append(ErrorDetail(code=401, message="Mess is closed"))

    result = await db.execute(
        select(MealSlotExpiry).where(
            MealSlotExpiry.mess_id == coupon.mess_id,
            MealSlotExpiry.meal_slot == coupon.meal_slot
        )
    )

    expiry : Optional[MealSlotExpiry] = result.scalar_one_or_none()

    if not expiry:
        errors.append(ErrorDetail(code=401, message="Expiry config missing"))
    else:
        # expiry = datetime.combine(coupon.date, expiry.end_time, tzinfo=IST)

        now_ist = datetime.now(IST)

        start_dt = datetime.combine(coupon.date, expiry.start_time, tzinfo=IST)
        end_dt = datetime.combine(coupon.date, expiry.end_time, tzinfo=IST)

        if end_dt < start_dt:
            end_dt = end_dt + timedelta(days=1)

        if not (start_dt <= now_ist <= end_dt):
            errors.append(
                ErrorDetail(
                    code=401,
                    message="Coupon Expired !"
                )
            )

    if errors or coupon.scanned_at :
        scanned_time = (
            coupon.scanned_at.astimezone(IST)
            if coupon.scanned_at else None
        )
        print("printing success false errors",errors)

        return ScanCouponResponse(
            student_name=user.name,
            roll_no=student.roll_number,
            branch=student.branch,
            meal_slot=coupon.meal_slot.value,
            meal_type=coupon.meal_type.value,
            scanned_at=scanned_time,
            success=False,
            errors=errors
        )

    now_utc = datetime.now(timezone.utc)

    stmt = (
        update(Coupon)
        .where(
            Coupon.id == coupon.id,
            Coupon.college_id == payload.college_id,
            Coupon.mess_id == payload.mess_id,
            Coupon.student_id == payload.student_id,
            Coupon.scanned_at.is_(None)
        )
        .values(scanned_at=now_utc, scanned_by=scanned_by)
        .returning(Coupon)
    )

    result = await db.execute(stmt)
    updated_coupon = result.scalar_one_or_none()

    await db.commit()

    if not updated_coupon:
        errors.append(ErrorDetail(code=409, message="Already scanned"))

    final_coupon = updated_coupon or coupon

    scanned_time = (
        final_coupon.scanned_at.astimezone(IST)
        if final_coupon.scanned_at else None
    )

    return ScanCouponResponse(
        student_name=user.name,
        roll_no=student.roll_number,
        branch=student.branch,
        meal_slot=final_coupon.meal_slot.value,
        meal_type=final_coupon.meal_type.value,
        scanned_at=scanned_time,
        success=True,
        errors=errors
    )
