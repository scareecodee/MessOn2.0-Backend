from sqlalchemy import Column,Integer,String, Date, Enum
from app.db.base import Base
from app.models.mess.couponModel import MealType
from sqlalchemy import PrimaryKeyConstraint


class CouponCount(Base):
    __tablename__ = "coupon_analytics"

    date = Column(Date, nullable=False)

    meal_type = Column(
        Enum(
            MealType,
            name="meal_type_enum",
            create_type=False
        ),
        nullable=False
    )

    count = Column(Integer, nullable=False)

    day = Column(String, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("date", "meal_type"),
    )
