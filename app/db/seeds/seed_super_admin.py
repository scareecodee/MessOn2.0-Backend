import uuid
from sqlalchemy.orm import Session
from app.models.superAdmin.superAdminModel import SuperAdmin
from app.security.hash_pwd import get_password_hash  # your bcrypt function


def seed_super_admins(db: Session):
    admins = [
        {
            "email": "bipinchourasia14@gmail.com",
            "password": "bipin123"
        },
        {
            "email": "b524066@iiit-bh.ac.in",
            "password": "sundram123"
        }
    ]

    for admin_data in admins:
        existing = db.query(SuperAdmin).filter(
            SuperAdmin.email == admin_data["email"]
        ).first()

        if existing:
            print(f"{admin_data['email']} already exists")
            continue

        super_admin = SuperAdmin(
            id=uuid.uuid4(),
            email=admin_data["email"],
            password=get_password_hash(admin_data["password"]),
            role="super_admin"
        )

        db.add(super_admin)

    db.commit()
    print("Seeding completed")
