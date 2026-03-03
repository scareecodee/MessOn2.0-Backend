from app.db.session import SessionLocal
from app.db.seeds.seed_super_admin import seed_super_admins

def run():
    db = SessionLocal()
    try:
        seed_super_admins(db)
    finally:
        db.close()

if __name__ == "__main__":
    run()
# python -m app.db.seeds.run_seed
