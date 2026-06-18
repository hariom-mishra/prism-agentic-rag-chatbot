from fastapi import FastAPI, Depends
from core.db import get_db, db_engine, Base
import models
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from api.product import router as product_router
from api.auth import router as auth_router
from api.users import router as users_router

from core.redis import init_redis, close_redis
from core.middleware import ProfilingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with db_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            print("🎉 Database connected successfully on startup!")
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"❌ Database connection failed on startup: {e}")
    
    await init_redis()
    yield
    await close_redis()

app = FastAPI(lifespan=lifespan)
app.add_middleware(ProfilingMiddleware)

app.include_router(product_router)
app.include_router(auth_router)
app.include_router(users_router)

@app.get("/")
async def test(db: AsyncSession = Depends(get_db)):
    return {"message": "testing", "db_status": "connected successfully"}

