from fastapi.testclient import TestClient
import pytest
from typing import Dict

from fastapi_users.jwt import generate_jwt
from fastapi_users.password import PasswordHelper
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.users.manager import CustomUserManager


@pytest.fixture
def user_data() -> Dict[str, str]:
    return {
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "Password#123",
    }


@pytest.fixture
def superuser_data() -> Dict[str, str]:
    return {
        "email": "superuser@example.com",
        "first_name": "Super",
        "last_name": "User",
        "password": "Password#123",
    }


def test_auth_register_valid(client: TestClient, user_data: Dict[str, str]):
    response = client.post("/auth/register", json=user_data)
    response_data = response.json()

    assert response.status_code == 201
    assert response_data["id"] is not None
    assert response_data["first_name"] == user_data["first_name"]
    assert response_data["last_name"] == user_data["last_name"]
    assert response_data["email"] == user_data["email"]
    assert response_data["is_active"]
    assert not response_data["is_verified"]
    assert not response_data["is_superuser"]
    assert "created_at" in response_data
    assert "last_login" in response_data
    assert response_data["last_login"] is None


def test_auth_register_invalid(client: TestClient, user_data: Dict[str, str]):
    response = client.post("/auth/register", json=user_data)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["detail"] == "REGISTER_USER_ALREADY_EXISTS"


def test_auth_jwt_login_invalid(client: TestClient, user_data: Dict[str, str]):
    data = {"username": "invalid@example.com", "password": user_data["password"]}

    response = client.post("/auth/jwt/login", data=data)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["detail"] == "LOGIN_BAD_CREDENTIALS"


def test_auth_jwt_login_valid(client: TestClient, user_data: Dict[str, str]):
    data = {"username": user_data["email"], "password": user_data["password"]}

    response = client.post("/auth/jwt/login", data=data)
    response_data = response.json()

    assert response.status_code == 200
    assert "access_token" in response_data
    assert "token_type" in response_data
    assert response_data["token_type"] == "bearer"


def test_auth_jwt_logout_invalid(client: TestClient):
    response = client.post("/auth/jwt/logout")

    assert response.status_code == 401


def test_auth_jwt_logout_valid(client: TestClient, user_data: Dict[str, str]):
    data = {"username": user_data["email"], "password": user_data["password"]}

    login_response = client.post("/auth/jwt/login", data=data)
    login_response_data = login_response.json()

    access_token = login_response_data["access_token"]

    response = client.post(
        "/auth/jwt/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 204


def test_auth_forgot_password(client: TestClient, user_data: Dict[str, str]):
    response = client.post("/auth/forgot-password", json={"email": user_data["email"]})

    assert response.status_code == 202


def test_auth_reset_password_invalid_token(
    client: TestClient, user_data: Dict[str, str]
):
    response = client.post(
        "/auth/reset-password",
        json={
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTQwOTBlYWMxYTExNWM3MTBmMzQ0MzUiLCJwYXN",
            "password": user_data["password"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "RESET_PASSWORD_BAD_TOKEN"


@pytest.mark.asyncio
async def test_auth_reset_password_invalid_password(
    client: TestClient, database: AsyncIOMotorDatabase, user_data: Dict[str, str]
):
    user = await database["User"].find_one({"email": user_data["email"]})

    password_helper = PasswordHelper()
    token_data = {
        "sub": str(user["_id"]),
        "password_fgpt": password_helper.hash(password=user["hashed_password"]),
        "aud": CustomUserManager.reset_password_token_audience,
    }
    token = generate_jwt(
        token_data,
        CustomUserManager.reset_password_token_secret,
        CustomUserManager.reset_password_token_lifetime_seconds,
    )

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "password": "pass",
        },
    )
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["detail"]["code"] == "RESET_PASSWORD_INVALID_PASSWORD"


@pytest.mark.asyncio
async def test_auth_reset_password_valid(
    client: TestClient, database: AsyncIOMotorDatabase, user_data: Dict[str, str]
):
    user = await database["User"].find_one({"email": user_data["email"]})

    password_helper = PasswordHelper()
    token_data = {
        "sub": str(user["_id"]),
        "password_fgpt": password_helper.hash(password=user["hashed_password"]),
        "aud": CustomUserManager.reset_password_token_audience,
    }
    token = generate_jwt(
        token_data,
        CustomUserManager.reset_password_token_secret,
        CustomUserManager.reset_password_token_lifetime_seconds,
    )

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "password": user_data["password"],
        },
    )

    assert response.status_code == 200


def test_auth_request_verify_token(client: TestClient, user_data: Dict[str, str]):
    response = client.post(
        "/auth/request-verify-token", json={"email": user_data["email"]}
    )

    assert response.status_code == 202


def test_auth_verify_invalid(
    client: TestClient, database: AsyncIOMotorDatabase, user_data: Dict[str, str]
):
    response = client.post(
        "/auth/verify",
        json={
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTQwOTBlYWMxYTExNWM3MTBmMzQ0MzUiLCJwYXN"
        },
    )
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["detail"] == "VERIFY_USER_BAD_TOKEN"


@pytest.mark.asyncio
async def test_auth_verify(
    client: TestClient, database: AsyncIOMotorDatabase, user_data: Dict[str, str]
):
    user = await database["User"].find_one({"email": user_data["email"]})

    token_data = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "aud": CustomUserManager.verification_token_audience,
    }
    token = generate_jwt(
        token_data,
        CustomUserManager.verification_token_secret,
        CustomUserManager.verification_token_lifetime_seconds,
    )

    response = client.post("/auth/verify", json={"token": token})
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["is_verified"]


async def test_users_me_get_invalid(client: TestClient, user_data: Dict[str, str]):
    user_res = client.get("/users/me/")

    assert user_res.status_code == 401


async def test_users_me_get_valid(client: TestClient, user_data: Dict[str, str]):
    data = {"username": user_data["email"], "password": user_data["password"]}

    login_res = client.post("/auth/jwt/login", data=data)

    access_token = login_res.json()["access_token"]

    user_res = client.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_res.status_code == 200
    assert user_res.json()["email"] == data["username"]


def test_users_me_patch_invalid(client: TestClient, user_data: Dict[str, str]):
    data = {"username": user_data["email"], "password": user_data["password"]}

    login_res = client.post("/auth/jwt/login", data=data)

    access_token = login_res.json()["access_token"]

    user_res = client.patch(
        "/users/me/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"password": "pass"},
    )

    assert user_res.status_code == 400
    assert user_res.json()["detail"]["code"] == "UPDATE_USER_INVALID_PASSWORD"


def test_users_me_patch_valid(client: TestClient, user_data: Dict[str, str]):
    data = {"username": user_data["email"], "password": user_data["password"]}

    login_res = client.post("/auth/jwt/login", data=data)

    access_token = login_res.json()["access_token"]

    user_res = client.patch(
        "/users/me/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "first_name": "Sadiq",
            "last_name": "Musa",
            "password": user_data["password"],
        },
    )

    assert user_res.status_code == 200
    assert user_res.json()["first_name"] == "Sadiq"
    assert user_res.json()["last_name"] == "Musa"


@pytest.mark.asyncio
async def test_users_get_by_id_invalid(
    client: TestClient,
    user_data: Dict[str, str],
    superuser_data: Dict[str, str],
    database: AsyncIOMotorDatabase,
):
    # test missing token
    response_401 = client.get("/users/654090eac1a115c710f34435/")
    assert response_401.status_code == 401

    # test not superuser
    data = {"username": user_data["email"], "password": user_data["password"]}
    login_res = client.post("/auth/jwt/login", data=data)
    access_token = login_res.json()["access_token"]

    response_403 = client.get(
        "/users/654090eac1a115c710f34435/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response_403.status_code == 403

    # test user does not exist
    client.post("/auth/register", json=superuser_data)
    await database["User"].update_one(
        {"email": superuser_data["email"]},
        {"$set": {"is_verified": "true", "is_superuser": "true"}},
    )

    super_login_res = client.post(
        "/auth/jwt/login",
        data={
            "username": superuser_data["email"],
            "password": superuser_data["password"],
        },
    )
    super_access_token = super_login_res.json()["access_token"]
    response_404 = client.get(
        "/users/654090eac1a115c710f34435/",
        headers={"Authorization": f"Bearer {super_access_token}"},
    )

    assert response_404.status_code == 404


@pytest.mark.asyncio
async def test_users_get_by_id_valid(
    client: TestClient,
    superuser_data: Dict[str, str],
    user_data: Dict[str, str],
    database: AsyncIOMotorDatabase,
):
    login_res = client.post(
        "/auth/jwt/login",
        data={
            "username": superuser_data["email"],
            "password": superuser_data["password"],
        },
    )
    access_token = login_res.json()["access_token"]

    valid_user = await database["User"].find_one({"email": user_data["email"]})
    user_res = client.get(
        f"/users/{str(valid_user['_id'])}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert user_res.status_code == 200
    assert user_res.json()["id"] == str(valid_user["_id"])


@pytest.mark.asyncio
async def test_users_patch_by_id_invalid(
    client: TestClient,
    superuser_data: Dict[str, str],
    database: AsyncIOMotorDatabase,
    user_data: Dict[str, str],
):
    # test missing token
    response_401 = client.patch(f"/users/df333ffsdfsdf/", json={"first_name": "Garba"})
    assert response_401.status_code == 401

    # get superuser access token
    super_login_res = client.post(
        "/auth/jwt/login",
        data={
            "username": superuser_data["email"],
            "password": superuser_data["password"],
        },
    )
    super_user_token = super_login_res.json()["access_token"]

    # get non superuser access token
    user_login_res = client.post(
        "/auth/jwt/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )
    user_token = user_login_res.json()["access_token"]

    # retrieve a valid user from database
    valid_user = await database["User"].find_one({"email": user_data["email"]})

    # test update password invalid
    response_400 = client.patch(
        f"/users/{str(valid_user['_id'])}/",
        headers={"Authorization": f"Bearer {super_user_token}"},
        json={"password": "pass"},
    )
    assert response_400.status_code == 400
    assert response_400.json()["detail"]["code"] == "UPDATE_USER_INVALID_PASSWORD"

    # test not superuser
    response_403 = client.patch(
        f"/users/{str(valid_user['_id'])}/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"password": "Password#123"},
    )
    assert response_403.status_code == 403

    # test user does not exist
    response_404 = client.patch(
        "/users/fsdfsdfsdf/",
        headers={"Authorization": f"Bearer {super_user_token}"},
        json={"password": "Password#123"},
    )
    assert response_404.status_code == 404


@pytest.mark.asyncio
async def test_users_patch_by_id_valid(
    client: TestClient,
    superuser_data: Dict[str, str],
    database: AsyncIOMotorDatabase,
    user_data: Dict[str, str],
):
    # get superuser access token
    login_res = client.post(
        "/auth/jwt/login",
        data={
            "username": superuser_data["email"],
            "password": superuser_data["password"],
        },
    )
    access_token = login_res.json()["access_token"]

    # retrieve a valid user from database
    valid_user = await database["User"].find_one({"email": user_data["email"]})

    response = client.patch(
        f"/users/{str(valid_user['_id'])}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "password": "Password#123",
            "first_name": "Musa",
            "last_name": "Jamilu",
        },
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["id"] == str(valid_user["_id"])
    assert response_data["first_name"] == "Musa"
    assert response_data["last_name"] == "Jamilu"


@pytest.mark.asyncio
async def test_users_delete_by_id_invalid(
    client: TestClient,
    superuser_data: Dict[str, str],
    database: AsyncIOMotorDatabase,
    user_data: Dict[str, str],
):
    # test missing token
    response_401 = client.delete(f"/users/df333ffsdfsdf/")
    assert response_401.status_code == 401

    # get superuser access token
    super_login_res = client.post(
        "/auth/jwt/login",
        data={
            "username": superuser_data["email"],
            "password": superuser_data["password"],
        },
    )
    super_user_token = super_login_res.json()["access_token"]

    # get non superuser access token
    user_login_res = client.post(
        "/auth/jwt/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )
    user_token = user_login_res.json()["access_token"]

    # retrieve a valid user from database
    valid_user = await database["User"].find_one({"email": user_data["email"]})

    # test not superuser
    response_403 = client.delete(
        f"/users/{str(valid_user['_id'])}/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response_403.status_code == 403

    # test user does not exist
    response_404 = client.delete(
        "/users/fsdfsdfsdf/",
        headers={"Authorization": f"Bearer {super_user_token}"},
    )
    assert response_404.status_code == 404


@pytest.mark.asyncio
async def test_users_delete_by_id_valid(
    client: TestClient,
    superuser_data: Dict[str, str],
    database: AsyncIOMotorDatabase,
    user_data: Dict[str, str],
):
    # get superuser access token
    login_res = client.post(
        "/auth/jwt/login",
        data={
            "username": superuser_data["email"],
            "password": superuser_data["password"],
        },
    )
    access_token = login_res.json()["access_token"]

    # retrieve a valid user from database
    valid_user = await database["User"].find_one({"email": user_data["email"]})

    response = client.delete(
        f"/users/{str(valid_user['_id'])}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 204
