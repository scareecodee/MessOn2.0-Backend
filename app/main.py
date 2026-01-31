from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from app.db.session import get_db
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from app.db.session import engine, Base
from app.db.init_db import init_db
from fastapi.middleware.cors import CORSMiddleware
from app.routers import adminImportRouter,googleLoginRouter,couponRouter



# Base.metadata.create_all(bind=engine)


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "google.com",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


init_db()   # <-- runs table creation


@app.get("/")
def health_check(db:Session = Depends(get_db)):
    return {"messgae": "Hellow World"}


app.include_router(adminImportRouter.router)
app.include_router(googleLoginRouter.router)
app.include_router(couponRouter.router)


