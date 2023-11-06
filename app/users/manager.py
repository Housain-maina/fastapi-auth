from beanie import PydanticObjectId
from fastapi_users import BaseUserManager, InvalidPasswordException
from fastapi import Request, Response
from typing import Optional
from datetime import datetime
from fastapi_users.db import ObjectIDIDMixin
from .schemas import UserCreate, UserUpdate
from .db import User
from app.config.settings import settings
import re
from fastapi_users import models


def check_password_strength(password: str):
    """
    Checks if password is a combination of
    lowercase, uppercase, number and special symbol.
    """

    regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=!])[A-Za-z\d@#$%^&+=!]*$"
    if not re.search(regex, password):
        return False
    return True


class CustomUserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def validate_password(self, password: str, user: UserCreate | User) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(reason="Password should not contain e-mail")

        if user.first_name and user.first_name in password:
            raise InvalidPasswordException(
                reason="Password should not contain first_name"
            )
        if user.first_name and user.last_name in password:
            raise InvalidPasswordException(
                reason="Password should not contain last_name"
            )
        if not check_password_strength(password):
            raise InvalidPasswordException(
                reason="Password must contain a lowercase letter, uppercase letter, a number and a special symbol"
            )

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        await self.update(
            user_update=UserUpdate(last_login=datetime.utcnow()), user=user, safe=True
        )

    async def on_after_forgot_password(
        self, user: models.UP, token: str, request: Optional[Request] = None
    ) -> str:
        # send the user an email with link to reset their password
        return token

    async def on_after_reset_password(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        # send the user an email notifying them of successfully changing their password
        pass

    async def on_after_request_verify(
        self, user: models.UP, token: str, request: Optional[Request] = None
    ) -> None:
        pass
