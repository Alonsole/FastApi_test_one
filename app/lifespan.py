from contextlib import asynccontextmanager
from fastapi import FastAPI
from models import close_orm


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("START")
    yield
    await close_orm()
    print("FINISH")