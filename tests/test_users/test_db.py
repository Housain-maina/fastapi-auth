import pytest
from app.users.db import User, get_user_db
from fastapi_users.db import BeanieUserDatabase


@pytest.mark.asyncio
async def test_get_user_db() -> None:
    async for user_db in get_user_db():
        assert isinstance(user_db, BeanieUserDatabase)
        assert user_db.user_model == User
