import sys
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Add both the root directory and 'app' directory to sys.path to resolve core.* and app.core.* imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from main import app
from core.db import Base, get_db

TEST_DATABASE_URL = "postgresql+asyncpg://employee_user:Hariom123@localhost:5432/prism_test"

@pytest.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
    )
    yield engine
    await engine.dispose()

@pytest.fixture
async def init_db(test_engine):
    # Force loading of all models so metadata knows about them
    import models
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def TestingSessionLocal(test_engine):
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )

@pytest.fixture
async def db_session(init_db, TestingSessionLocal):
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
async def client(init_db, TestingSessionLocal):
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
