# app/schedulers/couponScheduler.py

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.models.mess.messModel import Mess
from app.services.couponGenerationService import generate_coupons_for_week

IST = ZoneInfo("Asia/Kolkata")

scheduler = AsyncIOScheduler()


async def run_generation():
    print(f"[CRON START] {datetime.now(IST)}")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Mess.id, Mess.college_id).where(Mess.is_active == True)
        )
        messes = result.all()

    for mess_id, college_id in messes:
        try:
            async with AsyncSessionLocal() as db:
                await generate_coupons_for_week(db, mess_id, college_id)
        except Exception as e:
            print(f"[FAILED] mess={mess_id} err={e}")

    print(f"[CRON END] {datetime.now(IST)}")


async def run_with_retry():
    for i in range(5):
        try:
            await run_generation()
            return
        except Exception as e:
            print(f"[RETRY {i+1}] {e}")
            await asyncio.sleep(100)


scheduler.add_job(
    run_with_retry,
    trigger="cron",
    hour=3,
    minute=42,
    timezone="Asia/Kolkata"
)

def start_scheduler():
    scheduler.start()