from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from zoneinfo import ZoneInfo

from app.db.session import SessionLocal
from app.services.dailyCouponGenerator import generate_today_coupons

IST = ZoneInfo("Asia/Kolkata")


def generate_coupons_job():
    db = SessionLocal()
    try:
        target_date = datetime.now(IST).date()
        generate_today_coupons(db, target_date)
    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler(timezone=IST)

    scheduler.add_job(
        generate_coupons_job,
        trigger="cron",
        hour=1,
        minute=0,
        second=0,
        id="daily_coupon_job",
        replace_existing=True,
    )

    scheduler.start()
