import asyncio
import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware import Middleware

from internal.pkg.event_loop import EventLoop
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
    async def _lifespan(self, app: FastAPI):
        # Startup
        app.state.event_loop = EventLoop(
            startup=[],
            shutdown=[],
            closed=[self._raise_sigint],
        )
        app.state.event_loop.start()

        try:
            yield
        except asyncio.CancelledError:
            pass
        finally:
            # Shutdown
            app.state.event_loop.close()

    @staticmethod
    def _raise_sigint():
        signal.raise_signal(signal.SIGINT)
