import asyncio
from threading import Event, Thread
from typing import Awaitable


class EventLoop(Thread):
    def __init__(self) -> None:
        super().__init__()
        self.daemon = True

        self._startup_callbacks: list[Awaitable[None]] = []
        self._startup_event = Event()
        self._shutdown_callbacks: list[Awaitable[None]] = []

        self._loop = asyncio.new_event_loop()

    def add_startup(self, coro: Awaitable[None]) -> None:
        self._startup_callbacks.append(coro)

    def add_shutdown(self, coro: Awaitable[None]) -> None:
        self._shutdown_callbacks.append(coro)

    def start(self) -> None:
        super().start()
        self._startup_event.wait()

    def close(self) -> None:
        self._loop.stop()
        self.join()

    def run(self) -> None:
        """
        `run` is used to run a event loop in another thread. Do not call it directly.
        """
        asyncio.set_event_loop(self._loop)
        try:
            # startup
            self._loop.run_until_complete(asyncio.gather(*self._startup_callbacks))
            self._startup_event.set()

            self._loop.run_forever()
        finally:
            try:
                # shutdown
                self._loop.run_until_complete(asyncio.gather(*self._shutdown_callbacks))
                self._loop.run_until_complete(self._loop.shutdown_asyncgens())
                self._loop.run_until_complete(self._loop.shutdown_default_executor())
            finally:
                asyncio.set_event_loop(None)
                self._loop.close()
