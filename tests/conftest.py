import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.settings import Settings
from typing import Generator
from fastapi.testclient import TestClient

from app.config.settings import get_db
import asyncio
from app.main import app


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest.fixture(scope="session")
def database():
    return get_db()


@pytest.fixture(scope="session")
def app_instance():
    return app


@pytest.fixture(scope="session")
def client(app_instance) -> Generator:
    with TestClient(app_instance) as c:
        yield c


@pytest.fixture(scope="session")
def event_loop(database: AsyncIOMotorDatabase):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    database.client.drop_database(database.name)
    loop.close()
