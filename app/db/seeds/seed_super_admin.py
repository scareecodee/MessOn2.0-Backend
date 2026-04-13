from sqlalchemy import select
from app.models.rootAdmin.rootAdminUserModel import RootAdmin
from app.utils.hash_pwd import get_password_hash
from app.db.session import AsyncSessionLocal
from app.core.config import get_settings

settings = get_settings()

async def seed_root_admins():
    async with AsyncSessionLocal() as db:

        admins = [
            {
                "email": settings.root_admin_1_email,
                "name": settings.root_admin_1_name,
                "password": settings.root_admin_1_password
            }
        ]

        for admin_data in admins:
            if not admin_data["email"] or not admin_data["password"]:
                continue

            result = await db.execute(
                select(RootAdmin).where(
                    RootAdmin.email == admin_data["email"]
                )
            )
            existing = result.scalar_one_or_none()

            if not existing:
                new_admin = RootAdmin(
                    name=admin_data["name"],
                    email=admin_data["email"],
                    password=get_password_hash(admin_data["password"]),
                    is_active=True
                )
                db.add(new_admin)

        await db.commit()