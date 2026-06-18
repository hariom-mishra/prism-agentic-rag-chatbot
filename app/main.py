import logging
import json
import os
from datetime import datetime

class SimpleJsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage()
        })

handler = logging.StreamHandler()
if os.getenv("LOG_FORMAT") == "json":
    handler.setFormatter(SimpleJsonFormatter())
else:
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)

# Monkey patch _IncludedRouter to add path property for prometheus compatibility
try:
    from fastapi.routing import _IncludedRouter
    _IncludedRouter.path = property(lambda self: "")
except ImportError:
    pass

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

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(lifespan=lifespan)
app.add_middleware(ProfilingMiddleware)
Instrumentator().instrument(app).expose(app)

app.include_router(product_router)
app.include_router(auth_router)
app.include_router(users_router)

@app.get("/")
async def test(db: AsyncSession = Depends(get_db)):
    return {"message": "testing", "db_status": "connected successfully"}

