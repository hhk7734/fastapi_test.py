import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware import Middleware

from internal.user_interface.restapi import middleware
from internal.user_interface.restapi.controller import healthz


class RestAPI:
    def create_app(self):
        app = FastAPI(
            lifespan=self._lifespan,
            middleware=[
                Middleware(middleware.Logger),
            ],
        )

        app.include_router(healthz.router)

        return app

    @asynccontextmanager
    async def _lifespan(self, _: FastAPI):
        # Startup
        try:
            yield
        except asyncio.CancelledError:
            pass
        finally:
            # Shutdown
            pass
