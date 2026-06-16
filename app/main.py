from fastapi import FastAPI, Depends
from core.db import get_db, db_engine, Base
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with db_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("🎉 Database connected successfully on startup!")
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"❌ Database connection failed on startup: {e}")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def test(db: AsyncSession = Depends(get_db)):
    return {"message": "testing", "db_status": "connected successfully"}

