from app.db.session import engine
from app.db.base import Base

# IMPORTANT: import models so Base knows about them
from app.models.student.studentModel import Student
from app.models.student.mealPreferenceModel import MealPreference
from app.models.student.studentImportSession import StudentImportSession
from app.models.superAdmin.superAdminModel import SuperAdmin


def init_db():
    print(Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
