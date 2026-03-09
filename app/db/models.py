from app.db.session import engine
from app.db.base import Base

from app.models.user.userModel import User
from app.models.college.collegeModel import College
from app.models.college.collegeAdmin import CollegeAdmin
from app.models.college.collegeAdminMess import CollegeAdminMess
from app.models.mess.messModel import Mess
from app.models.student.studentModel import Student
from app.models.mess.messMenuModel import Menu



def init_db():
    print(Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
