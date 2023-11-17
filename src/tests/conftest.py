import asyncio
from typing import AsyncGenerator
from uuid import UUID

import asyncpg
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text

import settings
from auth.services.hashing import Hasher
from db.models import Base
from db.session import get_db
from main import app

test_engine = create_async_engine(settings.TEST_DATABASE_URL, poolclass=NullPool)
test_session_maker = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)
Base.metadata.bind = test_engine


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_maker() as session:
        yield session


app.dependency_overrides[get_db] = override_get_async_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True, scope="function")
async def truncate_tables():
    async with test_engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            await conn.execute(text(f"TRUNCATE {table.name} CASCADE;"))


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool(
        "".join(settings.TEST_DATABASE_URL.split("+asyncpg"))
    )
    yield pool
    await pool.close()


@pytest.fixture
async def get_user_from_database(asyncpg_pool):
    async def get_user(id: str):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetch("SELECT * FROM users WHERE id = $1;", id)

    return get_user


@pytest.fixture
async def create_user_in_database(asyncpg_pool):
    async def create_user(
        id: UUID,
        name: str,
        surname: str,
        email: str,
        is_active: bool,
    ):
        async with asyncpg_pool.acquire() as connection:
            return await connection.execute(
                """
                INSERT INTO users (id, name, surname, email, is_active, hashed_password)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                id,
                name,
                surname,
                email,
                is_active,
                Hasher.get_password_hash("12345678"),
            )

    return create_user
