import asyncio
from concurrent.futures import Future
from threading import Event, Thread
from typing import Awaitable, Callable

import loggingx as logging


class EventLoop(Thread):
    def __init__(
        self,
        startup: list[Callable[[None], Awaitable[None]]] | None = None,
        shutdown: list[Callable[[None], Awaitable[None]]] | None = None,
        closed: list[Callable[[None], None]] | None = None,
    ) -> None:
        super().__init__(daemon=True)

        self._startup = startup if startup else []
        self._shutdown = shutdown if shutdown else []
        self._closed = closed if closed else []

        self._startup_finished = Event()
        self._cancelled = Event()
        self._loop = asyncio.new_event_loop()
        self._futures: list[Future] = []

    def start(self) -> None:
        super().start()
        self._startup_finished.wait()

    def add_task(self, coro: Callable[[Event], Awaitable[None]]) -> None:
        """
        Args:
            coro: coroutine with signature `func(cancelled: Event) -> None`
        """
        if self._cancelled.is_set():
            raise RuntimeError("event loop is cancelled")

        fut = asyncio.run_coroutine_threadsafe(coro(self._cancelled), self._loop)
        self._futures.append(fut)
        fut.add_done_callback(lambda _: self._futures.remove(fut))

    def close(self) -> None:
        self._cancelled.set()
        self.join()

    def run(self) -> None:
        """
        `run` is used to run a event loop in another thread. Do not call it directly.
        """
        asyncio.set_event_loop(self._loop)
        try:
            # startup
            logging.info("starting up event loop")
            self._loop.run_until_complete(asyncio.gather(*[coro() for coro in self._startup]))
            self._startup_finished.set()

            # run
            async def main():
                while not self._cancelled.is_set() or self._futures:
                    await asyncio.sleep(1)

            logging.info("running event loop")
            self._loop.run_until_complete(main())
        except Exception:
            logging.exception("event loop failed")
        finally:
            self._cancelled.set()

            try:
                # shutdown
                logging.info("shutting down event loop")
                self._loop.run_until_complete(asyncio.gather(*[coro() for coro in self._shutdown]))
                self._loop.run_until_complete(self._loop.shutdown_asyncgens())
                self._loop.run_until_complete(self._loop.shutdown_default_executor())
            finally:
                asyncio.set_event_loop(None)
                self._loop.close()

        for func in self._closed:
            func()
        logging.info("event loop closed")
