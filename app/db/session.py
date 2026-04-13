from click import echo
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine



settings = get_settings()

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.database_username}:"
    f"{settings.database_password}@"
    f"{settings.database_hostname}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        print("connecting to db")
        yield session



