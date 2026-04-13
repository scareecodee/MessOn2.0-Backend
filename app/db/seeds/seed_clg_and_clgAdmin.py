from sqlalchemy import select
from app.models.college.collegeModel import College
from app.models.user.userModel import User
from app.models.college.collegeAdmin import CollegeAdmin
from app.db.session import AsyncSessionLocal
from app.core.config import get_settings
from app.utils.userRole import UserRole

settings = get_settings()


async def seed_college_and_admin():
    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(College).where(College.name == settings.college_name)
        )
        college = result.scalar_one_or_none()

        if not college:
            college = College(
                name=settings.college_name,
                domain=settings.college_domain,
            )
            db.add(college)
            await db.flush() 

        admins = [
            {
                "name": settings.college_admin_1_name,
                "email": settings.college_admin_1_email
            },
            {
                "name": settings.college_admin_2_name,
                "email": settings.college_admin_2_email
            }
        ]

        for admin_data in admins:
            if not admin_data["email"]:
                continue

            # check user
            result = await db.execute(
                select(User).where(User.email == admin_data["email"])
            )
            user = result.scalar_one_or_none()

            if not user:
                user = User(
                    name=admin_data["name"],
                    email=admin_data["email"],
                    role=UserRole.college_admin,
                    college_id=college.id,
                    is_active=True
                )
                db.add(user)
                await db.flush()

            result = await db.execute(
                select(CollegeAdmin).where(CollegeAdmin.id == user.id)
            )
            existing = result.scalar_one_or_none()

            if not existing:
                db.add(
                    CollegeAdmin(
                        id=user.id,
                        college_id=college.id
                    )
                )

        await db.commit()