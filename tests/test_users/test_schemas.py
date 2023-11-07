import pytest
from datetime import datetime
from app.users.schemas import UserRead, UserCreate, UserUpdate
from beanie import PydanticObjectId


@pytest.fixture
def user_read_data():
    return {
        "id": PydanticObjectId("6549808b53e310b880d3aafa"),
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "created_at": datetime(2023, 1, 1),
        "last_login": datetime(2023, 1, 2),
    }


@pytest.fixture
def user_create_data():
    return {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "password": "Password#123",
    }


@pytest.fixture
def user_update_data():
    return {
        "first_name": "Updated",
        "last_name": "User",
        "password": "NewPassword#123",
    }


def test_user_read_model(user_read_data):
    user_read = UserRead(**user_read_data)
    assert str(user_read.id) == "6549808b53e310b880d3aafa"
    assert user_read.email == "user@example.com"
    assert user_read.first_name == "John"
    assert user_read.last_name == "Doe"
    assert user_read.is_active
    assert not user_read.is_superuser
    assert not user_read.is_verified
    assert user_read.created_at == datetime(2023, 1, 1)
    assert user_read.last_login == datetime(2023, 1, 2)


def test_user_create_model(user_create_data):
    user_create = UserCreate(**user_create_data)
    assert user_create.first_name == "Jane"
    assert user_create.last_name == "Smith"
    assert user_create.email == "jane@example.com"
    assert user_create.password == "Password#123"
    assert user_create.is_active
    assert not user_create.is_superuser
    assert not user_create.is_verified


def test_user_update_model(user_update_data):
    user_update = UserUpdate(**user_update_data)
    assert user_update.first_name == "Updated"
    assert user_update.last_name == "User"
    assert user_update.password == "NewPassword#123"


def test_user_update_model_default_values():
    user_update = UserUpdate()
    assert user_update.first_name is None
    assert user_update.last_name is None
    assert user_update.password is None
