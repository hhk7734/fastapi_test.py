from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware import Middleware

from internal.user_interface.restapi import middleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    lifespan=lifespan,
    middleware=[
        Middleware(middleware.Logger),
        Middleware(middleware.Recovery),
    ],
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
