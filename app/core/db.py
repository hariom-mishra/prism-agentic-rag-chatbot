from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import setting
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

db_engine = create_async_engine(
    setting.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

async_session = async_sessionmaker(db_engine, expire_on_commit=False, auto_commit=False,)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as db:
        try:
            yield db
        except Exception as e:
            print(f"something went wrong: {e}")
            await db.close()





