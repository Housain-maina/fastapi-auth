from beanie import PydanticObjectId
from fastapi_users import schemas
from pydantic.fields import Field
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime


class UserRead(schemas.BaseUser[PydanticObjectId]):
    first_name: str
    last_name: str
    created_at: datetime
    last_login: datetime | None


class UserCreate(schemas.BaseUserCreate):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Hussaini",
                "last_name": "Usman",
                "email": "hussaini@example.com",
                "password": "Password#123",
            }
        }
    )

    first_name: str
    last_name: str


class UserUpdate(schemas.CreateUpdateDictModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Hussaini",
                "last_name": "Usman",
                "password": "Password#123",
            }
        }
    )

    first_name: Optional[str] = Field(min_length=3, default=None)
    last_name: Optional[str] = Field(min_length=3, default=None)
    password: Optional[str] = None
