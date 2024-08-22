import asyncio
import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware import Middleware

from ..event_loop import EventLoop
from . import controller, middleware


class RestAPI:
    def create_app(self):
        app = FastAPI(
            lifespan=self._lifespan,
            middleware=[
                Middleware(middleware.request_id.RequestID),
                Middleware(middleware.logger.Logger),
            ],
        )

        app.include_router(controller.healthz.router)

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
