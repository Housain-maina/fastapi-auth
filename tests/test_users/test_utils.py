from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    JWTStrategy,
    BearerTransport,
    AuthenticationBackend,
)
from app.config.settings import Settings
from app.users.utils import (
    get_user_manager,
    get_jwt_strategy,
    bearer_transport,
    auth_backend,
    fastapi_users,
)
from app.users.manager import CustomUserManager
import pytest


@pytest.mark.asycio
async def test_get_user_manager():
    async for manager in get_user_manager():
        assert isinstance(manager, CustomUserManager)


def test_bearer_transport():
    assert isinstance(bearer_transport, BearerTransport)


def test_get_jwt_strategy(settings: Settings):
    jwt_strategy = get_jwt_strategy()

    assert isinstance(jwt_strategy, JWTStrategy)
    assert jwt_strategy.secret == settings.SECRET_KEY
    assert jwt_strategy.lifetime_seconds == 3600


def test_auth_backend():
    assert isinstance(auth_backend, AuthenticationBackend)
    assert auth_backend.transport == bearer_transport
    assert auth_backend.name == "jwt"
    assert auth_backend.get_strategy == get_jwt_strategy


def test_fastapi_users():
    assert isinstance(fastapi_users, FastAPIUsers)
    assert fastapi_users.get_user_manager == get_user_manager
    assert fastapi_users.authenticator.backends[0] == auth_backend
