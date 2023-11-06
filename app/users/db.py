from beanie import Document
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from pydantic.fields import Field
from typing import cast, Type
from fastapi_users_db_beanie import UP_BEANIE
from datetime import datetime


class User(BeanieBaseUser, Document):
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime | None = Field(default=None)


async def get_user_db():
    yield BeanieUserDatabase(cast(Type[UP_BEANIE], User))
