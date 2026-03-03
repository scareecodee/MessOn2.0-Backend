from fastapi import FastAPI, Depends
from app.db.session import get_db
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.init_db import init_db
from fastapi.middleware.cors import CORSMiddleware
from app.routers.student import fetchCouponRouter, studentLoginRouter, messMenuFetchRouter, studentComplaintRouter, \
    notificationRouter
from app.routers.mess import messAdminDashboardRouter, messAdminLoginRouter, messAdminScanRouter, messMenuCreationRouter
from app.routers.superAdmin import adminCsvImport,addStudentsManually,studentActivation

from app.core.backgroundScheduler import start_scheduler

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

@app.get("/startup")
def startup():
    print("SERVER INSTANCE ID:", id(app))
    pass


@app.on_event("startup")
def startup_event():
    start_scheduler()


app.include_router(adminCsvImport.router)
app.include_router(studentLoginRouter.router)
app.include_router(fetchCouponRouter.router)
app.include_router(messAdminScanRouter.router)
app.include_router(messAdminLoginRouter.router)
# app.include_router(messMenuCreationRouter.router)
# app.include_router(messAdminCreationRouter.router)
app.include_router(messMenuFetchRouter.router)
app.include_router(notificationRouter.router)
app.include_router(studentComplaintRouter.router)
app.include_router(messAdminDashboardRouter.router)
app.include_router(addStudentsManually.router)
app.include_router(studentActivation.router)



