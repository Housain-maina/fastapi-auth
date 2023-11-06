from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

    MONGODB_URL: str
    DB_NAME: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


settings = Settings()


def get_db() -> AsyncIOMotorDatabase:
    async_client = AsyncIOMotorClient(settings.MONGODB_URL)
    async_db = async_client[settings.DB_NAME]

    return async_db
