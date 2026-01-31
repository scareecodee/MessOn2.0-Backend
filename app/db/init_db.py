from app.db.session import engine
from app.db.base import Base

# IMPORTANT: import models so Base knows about them
from app.models.studentModel import Student  # noqa

def init_db():
    Base.metadata.create_all(bind=engine)
