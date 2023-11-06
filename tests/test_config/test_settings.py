import pytest
import os
from app.config.settings import Settings
from motor.motor_asyncio import AsyncIOMotorDatabase


def test_settings(settings: Settings):
    assert settings.MONGODB_URL == os.environ["MONGODB_URL"]
    assert settings.DB_NAME == os.environ["DB_NAME"]
    assert settings.SECRET_KEY == os.environ["SECRET_KEY"]
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == int(
        os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]
    )


@pytest.mark.asyncio
async def test_db_connection(settings: Settings, database: AsyncIOMotorDatabase):
    assert await database.command("ping")
    assert database.name == settings.DB_NAME
