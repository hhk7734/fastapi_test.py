from fastapi import FastAPI
from fastapi.middleware import Middleware

from internal.user_interface.restapi import middleware

app = FastAPI(
    middleware=[
        Middleware(middleware.Logger),
        Middleware(middleware.Recovery),
    ]
)
