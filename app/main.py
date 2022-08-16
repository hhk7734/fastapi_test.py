from fastapi import FastAPI
from fastapi.middleware import Middleware

from app.user_interface.fastapi import middleware

app = FastAPI(
    middleware=[
        Middleware(middleware.Logger),
        Middleware(middleware.Recovery),
    ]
)
