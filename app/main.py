from fastapi import FastAPI, Depends
from app.db.session import get_db
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.models import init_db
from fastapi.middleware.cors import CORSMiddleware

from app.routers.collegeAdmin import (
    fetchCollegeDetails,createMess,fetchAllMess,createMessAdmin,
    fetchMessAdmins,bulkStudentsImport,fetchStudents,createStudentsManually
)

from app.routers.mess import (
     createMessMenuRouter,createMealDayPolicyRouter,fetchMealDayPolicyRouter
)
from app.routers.student import (
     fetchMenuRouter,

)

from app.routers.student import userLoginRouter
# from app.core.backgroundScheduler import start_scheduler

from datetime import datetime, timezone,date
from zoneinfo import ZoneInfo


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #  allow all during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


init_db()   # <-- runs table creation



# print("UTC now:", datetime.now(timezone.utc))
# print("IST now:", datetime.now(ZoneInfo("Asia/Kolkata")))
# print("date.today():", date.today())


@app.get("/")
def health_check(db:Session = Depends(get_db)):
    return {"message": "Hellow World",}

# @app.get("/startup")
# def startup():
#     print("SERVER INSTANCE ID:", id(app))
#     pass
#
#
# @app.on_event("startup")
# def startup_event():
#     start_scheduler()


app.include_router(fetchCollegeDetails.router)
app.include_router(userLoginRouter.router)
app.include_router(createMess.router)
app.include_router(fetchAllMess.router)
app.include_router(createMessAdmin.router)
app.include_router(fetchMessAdmins.router)
app.include_router(bulkStudentsImport.router)
app.include_router(fetchStudents.router)
app.include_router(createStudentsManually.router)
app.include_router(createMessMenuRouter.router)
app.include_router(fetchMenuRouter.router)
app.include_router(createMealDayPolicyRouter.router)
app.include_router(fetchMealDayPolicyRouter.router)





