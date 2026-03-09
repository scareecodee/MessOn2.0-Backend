# from sqlalchemy import (
#     Column, String, Integer, ForeignKey,
#     TIMESTAMP, func, UniqueConstraint,
#     Date, Enum, UUID
# )
#
# from app.utils.mealSlot import MealSlot
# from app.utils.mealType import MealType
# from app.utils.weekDays import WeekDays
# from app.db.base import Base
# class MealPreference(Base):
#     __tablename__ = "meal_preferences"
#
#     id = Column(Integer, primary_key=True, index=True)
#
#     student_id = Column(
#         UUID,
#         ForeignKey("students.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True
#     )
#
#     week_start = Column(Date, nullable=False)
#
#     day = Column(Enum(WeekDays), nullable=False)
#
#     meal_slot = Column(Enum(MealSlot), nullable=False)
#
#     preference = Column(
#         Enum(MealType),
#         nullable=False,
#         server_default=MealType.veg
#     )
#
#     created_at = Column(TIMESTAMP, server_default=func.now())
#
#     __table_args__ = (
#         UniqueConstraint(
#             "student_id",
#             "week_start",
#             "day",
#             "meal_slot",
#             name="unique_student_week_day_meal"
#         ),
#     )