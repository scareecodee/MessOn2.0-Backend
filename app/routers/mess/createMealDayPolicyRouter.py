from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from app.db.session import get_db
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.mealDayPolicy import MessDayPolicy

from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek
# from app.utils.weekDayOrder import WEEKDAY_ORDER

from app.schemas.mess.createDayPolicy import CreateDayPolicy
from app.schemas.mess.dayPolicyResponse import DayPolicyResponse

from app.services.weekResolverService import resolve_week
from app.services.messConfigLockService import is_config_locked# 🔥 IMPORTANT

IST = ZoneInfo("Asia/Kolkata")

router = APIRouter(
    prefix="/messes",
    tags=["Manage Mess Day Policy"]
)


@router.patch("/day-policy/{menu_week}", response_model=List[DayPolicyResponse])
async def upsert_day_policy(
    menu_week: MenuWeek,
    payload: List[CreateDayPolicy],
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MessAdmin).filter(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        )
    )
    mess_admin = result.scalar_one_or_none()

    if not mess_admin:
        raise HTTPException(404, "You are not authorized to access this")

    week = await resolve_week(
        db,
        menu_week,
        mess_admin.mess_id,
        current_user.college_id
    )

    locked = await is_config_locked(
        mess_id=mess_admin.mess_id,
        week_id=week.id,
        db=db
    )

    if locked:
        raise HTTPException(404, "Cannot modify mess day policy for this week")

    # today_day = datetime.now(IST).strftime("%A").lower()
    # today_index = WEEKDAY_ORDER[today_day]

    # -------- FETCH EXISTING --------
    result = await db.execute(
        select(MessDayPolicy).filter(
            MessDayPolicy.mess_id == mess_admin.mess_id,
            MessDayPolicy.college_id == current_user.college_id,
            MessDayPolicy.week_id == week.id   # ✅ FIXED
        )
    )
    existing = result.scalars().all()

    existing_map = {policy.day: policy for policy in existing}

    response = []

    for item in payload:

        # target_index = WEEKDAY_ORDER[item.day.value]
        #
        # if target_index <= today_index:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"Cannot modify policy for {item.day.value} (today or past)"
        #     )

        existing_policy = existing_map.get(item.day)

        if existing_policy:
            existing_policy.is_compulsory = item.is_compulsory
            policy = existing_policy
        else:
            policy = MessDayPolicy(
                mess_id=mess_admin.mess_id,
                college_id=current_user.college_id,
                week_id=week.id,   # ✅ FIXED
                day=item.day,
                is_compulsory=item.is_compulsory
            )
            db.add(policy)

        response.append(policy)

    await db.commit()

    return response