from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# import psycopg
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

settings = get_settings()

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{settings.database_username}:"
    f"{settings.database_password}@"
    f"{settings.database_hostname}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        # Print BEFORE yielding to confirm connection started
        print("Checking DB connection...") 
        yield db
    except Exception as e:
        print(f"Error connecting: {e}")
        raise e
    finally:
        # This runs when request is done
        print("Closing DB session") 
        db.close()
