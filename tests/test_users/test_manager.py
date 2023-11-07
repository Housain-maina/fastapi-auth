from fastapi import Depends
from fastapi_users_db_beanie import BeanieUserDatabase
from fastapi_users import InvalidPasswordException
from app.users.db import get_user_db
from app.users.manager import check_password_strength, CustomUserManager
import pytest
from app.users.schemas import UserCreate


def test_check_password_strength_valid():
    assert check_password_strength("Abc@1234") is True


def test_check_password_strength_missing_lowercase():
    assert check_password_strength("ABC@1234") is False


def test_check_password_strength_missing_uppercase():
    assert check_password_strength("abc@1234") is False


def test_check_password_strength_missing_number():
    assert check_password_strength("Abc@XYZ") is False


def test_check_password_strength_missing_special_symbol():
    assert check_password_strength("Abc12345") is False


@pytest.fixture
async def user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield CustomUserManager(user_db)


@pytest.mark.asyncio
async def test_validate_password_valid(user_manager):
    user = UserCreate(
        email="test@example.com",
        password="Abc@1234",
        first_name="John",
        last_name="Doe",
    )
    await user_manager.validate_password(user.password, user)


@pytest.mark.asyncio
async def test_validate_password_short_password(user_manager):
    user = UserCreate(
        email="test@example.com", password="abc123", first_name="John", last_name="Doe"
    )
    with pytest.raises(InvalidPasswordException) as exc_info:
        await user_manager.validate_password(user.password, user)

    assert "Password should be at least 8 characters" in str(exc_info.value.reason)


@pytest.mark.asyncio
async def test_validate_password_contains_email(user_manager):
    user = UserCreate(
        email="test@example.com",
        password="Abc@1234test@example.com",
        first_name="John",
        last_name="Doe",
    )
    with pytest.raises(InvalidPasswordException) as exc_info:
        await user_manager.validate_password(user.password, user)

    assert "Password should not contain e-mail" in str(exc_info.value.reason)


@pytest.mark.asyncio
async def test_validate_password_contains_first_name(user_manager):
    user = UserCreate(
        email="test@example.com",
        password="Abc@1234JohnDoe",
        first_name="John",
        last_name="Doe",
    )
    with pytest.raises(InvalidPasswordException) as exc_info:
        await user_manager.validate_password(user.password, user)

    assert "Password should not contain first_name" in str(exc_info.value.reason)


@pytest.mark.asyncio
async def test_validate_password_contains_last_name(user_manager):
    user = UserCreate(
        email="test@example.com",
        password="Abc@1234Doe",
        first_name="John",
        last_name="Doe",
    )
    with pytest.raises(InvalidPasswordException) as exc_info:
        await user_manager.validate_password(user.password, user)

    assert "Password should not contain last_name" in str(exc_info.value.reason)


@pytest.mark.asyncio
async def test_validate_password_weak(user_manager):
    user = UserCreate(
        email="test@example.com",
        password="abcdefgd",
        first_name="John",
        last_name="Doe",
    )
    with pytest.raises(InvalidPasswordException) as exc_info:
        await user_manager.validate_password(user.password, user)

    assert (
        "Password must contain a lowercase letter, uppercase letter, a number and a special symbol"
        in str(exc_info.value.reason)
    )
