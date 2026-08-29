import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app
from app.seed.seed_data import seed_database

# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    # Seed the test in-memory database
    from app.core.rbac import UserRole
    from app.core.security import get_password_hash
    from app.models.user import User
    from app.models.zone import Zone, RiskLevel

    u = User(
        name="Test Commander",
        email="test.commander@mahapolice.gov.in",
        password_hash=get_password_hash("varisetu2026"),
        role=UserRole.ADMIN,
        is_active=True
    )
    u_police = User(
        name="Test Officer Patil",
        email="test.police@mahapolice.gov.in",
        password_hash=get_password_hash("varisetu2026"),
        role=UserRole.POLICE,
        is_active=True
    )
    z = Zone(
        name="Pandharpur Chowk",
        latitude=17.6777,
        longitude=75.3276,
        capacity=50000,
        risk_level=RiskLevel.LOW
    )
    test_db.add(u)
    test_db.add(u_police)
    test_db.add(z)
    await test_db.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
