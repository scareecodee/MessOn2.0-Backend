# app/api/routes/admin_readiness.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user.userModel import User
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.mealSlotExpiryModel import MealSlotExpiry
from app.models.mess.mealDayPolicy import MessDayPolicy
from app.models.mess.messMenuModel import Menu

from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.utils.menuWeek import MenuWeek

from app.services.weekResolverService import resolve_week

router = APIRouter(prefix="/admin", tags=["Admin Readiness"])


@router.get("/week-readiness/{menu_week}")
async def get_week_readiness(
    menu_week: MenuWeek,
    current_user: User = Depends(get_current_role([UserRole.mess_admin])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MessAdmin).filter(
            MessAdmin.user_id == current_user.id,
            MessAdmin.college_id == current_user.college_id
        )
    )
    admin = result.scalar_one_or_none()

    mess_id = admin.mess_id

    expiry = await db.execute(
        select(MealSlotExpiry).filter(MealSlotExpiry.mess_id == mess_id)
    )

    policy = await db.execute(
        select(MessDayPolicy).filter(
            MessDayPolicy.mess_id == mess_id,
            MessDayPolicy.menu_week == menu_week
        )
    )

    menu = await db.execute(
        select(Menu).filter(
            Menu.mess_id == mess_id,
            Menu.menu_week == menu_week
        )
    )

    return {
        "expiry_set": bool(expiry.scalars().all()),
        "policy_set": bool(policy.scalars().all()),
        "menu_set": bool(menu.scalars().all()),
        "ready_for_generation": all([
            bool(expiry.scalars().all()),
            bool(policy.scalars().all()),
            bool(menu.scalars().all())
        ])
    }