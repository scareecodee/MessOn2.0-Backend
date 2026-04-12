from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from dotenv import load_dotenv
from app.tasks.cronJobs import start_scheduler
from app.db.models import init_db
from fastapi.middleware.cors import CORSMiddleware

from app.routers.collegeAdmin import (
    fetchCollegeDetails, createMess, fetchAllMess, createMessAdmin,
    fetchMessAdmins, bulkStudentsImport, fetchStudents, createStudentsManually, studentActivation,
    updateStudentDetails, createMessBill, AllStudentMessBill, studentDetailedMealConsumptionHistory,
    studentMessBillRouter, deleteMess,deleteUsers, createCollegeAdmin
)

from app.routers.mess import (
    createMessMenuRouter, createMealDayPolicyRouter, fetchMealDayPolicyRouter, fetchSubmissionWindowRouter,
    createMealSlotExpiryRouter, generateMessWeekRouter, createSubmissionWindowRouter,
    generateCouponsManually, scanCouponRouter, submissionWindowTemplateRouter, fetchMealSlotExpiryRouter,
    createMessClosureRouter, updateMessClosureRouter, fetchMessClosureRouter,
    fetchMealPreferenceAnalytics, scannedCouponAnalyticsRouter
)
from app.routers.student import (
     fetchMenuRouter,mealAvailabilityRouter,fetchMealPreferenceRouter,userLoginRouter,submitMealPrefernceRouter,
     fetchCouponRouter

)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #  allow all during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()


@app.on_event("startup")
async def startup():
    start_scheduler()
@app.get("/db-test")
async def db_test(db: AsyncSession = Depends(get_db)):
    return {"status": "connected"}

# @app.get("/startup")
# def startup():
#     print("SERVER INSTANCE ID:", id(app))
#     pass
#
#
# @app.on_event("startup")
# def startup_event():


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
app.include_router(mealAvailabilityRouter.router)
app.include_router(fetchMealPreferenceRouter.router)
app.include_router(submitMealPrefernceRouter.router)
app.include_router(fetchSubmissionWindowRouter.router)
app.include_router(createMealSlotExpiryRouter.router)

app.include_router(generateMessWeekRouter.router)

app.include_router(createSubmissionWindowRouter.router)
app.include_router(fetchCouponRouter.router)
app.include_router(generateCouponsManually.router)
app.include_router(scanCouponRouter.router)
app.include_router(submissionWindowTemplateRouter.router)
app.include_router(fetchMealSlotExpiryRouter.router)
app.include_router(createMessClosureRouter.router)
app.include_router(updateMessClosureRouter.router)
app.include_router(fetchMessClosureRouter.router)
app.include_router(studentActivation.router)
app.include_router(scannedCouponAnalyticsRouter.router)
app.include_router(updateStudentDetails.router)
app.include_router(fetchMealPreferenceAnalytics.router)
app.include_router(createMessBill.router)
app.include_router(AllStudentMessBill.router)
app.include_router(studentDetailedMealConsumptionHistory.router)
app.include_router(studentMessBillRouter.router)
app.include_router(deleteMess.router)
app.include_router(createCollegeAdmin.router)
app.include_router(deleteUsers.router)




