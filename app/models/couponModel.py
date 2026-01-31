import uuid
from sqlalchemy import Column, String, Date, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class MealType(str, enum.Enum):
    BREAKFAST = "B"
    LUNCH = "L"
    DINNER = "D"


class CouponStatus(str, enum.Enum):
    ISSUED = "ISSUED"
    USED = "USED"


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("authorized_students.id"), nullable=False)

    date = Column(Date, nullable=False)
    meal = Column(Enum(MealType), nullable=False)

    status = Column(Enum(CouponStatus), default=CouponStatus.ISSUED)

    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
