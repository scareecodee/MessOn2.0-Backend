from app.db.session import engine
from app.db.base import Base

from app.models.user.userModel import User
from app.models.college.collegeModel import College
from app.models.college.collegeAdmin import CollegeAdmin
from app.models.college.collegeAdminMess import CollegeAdminMess
from app.models.mess.messModel import Mess
from app.models.student.studentModel import Student
from app.models.mess.messMenuModel import Menu
from app.models.mess.mealSubmissionWindowModel import MealSubmissionWindow
from app.models.mess.messWeekModel import MessWeek
from app.models.mess.messClosureModel import MessClosure
from app.models.mess.submissionWindowTemplateModel import SubmissionWindowTemplate
from app.models.mess.messClosureModel import MessClosure
from app.models.college.MessPerDayPriceConfigModel import PerDayMealPrice


#
# def init_db():
#     print(Base.metadata.tables.keys())
#     Base.metadata.create_all(bind=engine)
async def init_db():
    async with engine.begin() as conn:
        print(Base.metadata.tables.keys())
        # print("init db")
        await conn.run_sync(Base.metadata.create_all)