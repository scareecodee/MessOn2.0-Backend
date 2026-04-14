from sqlalchemy import text

from app.db.session import engine
from app.db.base import Base

from app.models.user.userModel import User
from app.models.college.collegeModel import College
from app.models.college.collegeAdmin import CollegeAdmin
from app.models.mess.messModel import Mess
from app.models.student.studentModel import Student
from app.models.mess.messMenuModel import Menu
from app.models.mess.mealSubmissionWindowModel import MealSubmissionWindow
from app.models.mess.messWeekModel import MessWeek
from app.models.mess.messClosureModel import MessClosure
from app.models.mess.submissionWindowTemplateModel import SubmissionWindowTemplate
from app.models.mess.messClosureModel import MessClosure
from app.models.college.MessPerDayPriceConfigModel import PerDayMealPrice
from app.models.mess.ratingsModel import Rating
from app.models.mess.ratingAnalyticsModel import RatingAnalytics



async def init_db():
    async with engine.begin() as conn:
        print(Base.metadata.tables.keys())
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        # print("init db")
        await conn.run_sync(Base.metadata.create_all)