from fastapi import FastAPI
from beanie import init_beanie
from app.config.settings import get_db
from app.users.db import User
from app.users.router import router as users_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(
        database=get_db(),
        document_models=[
            User,
        ],
    )
    yield


app = FastAPI(
    title="FastAPI Auth",
    contact={"name": "Hussaini Usman", "email": "hussainmaina27@gmail.com"},
    lifespan=lifespan,
)


app.include_router(users_router)
