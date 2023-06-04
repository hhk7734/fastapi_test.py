import logging
import time
import traceback
from http import HTTPStatus

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from internal.pkg.logger import logger


class Logger(BaseHTTPMiddleware):
    @staticmethod
    async def _dump_request(request: Request, body: bool = False) -> str:
        headers = {k: v for k, v in request.headers.items()}
        dump = f"{request.method} {request.url.path} HTTP/{request.scope.get('http_version')}\r\n"
        dump += f"Host: {headers.pop('host', '')}\r\n"
        for k, v in headers.items():
            dump += f"{k.title()}: {v}\r\n"

        if body:
            dump += (await request.body()).decode()
            dump += "\r\n"

        return dump

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        path = request.url.path

        error = None
        try:
            res = await call_next(request)
        except:
            res = Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
            error = traceback.format_exc()

        latency = time.time() - start_time

        _log = logger.bind(
            method=request.method,
            url=path,
            status=res.status_code,
            remote_address=request.client.host if request.client is not None else "",
            user_agent=request.headers.get("user-agent", ""),
            latency=latency,
        )

        if error:
            # TODO: if debug mode, dump request body
            _log.error(error)
            _log.error(await self._dump_request(request))
        else:
            _log.info("request")

        return res


for name in logging.root.manager.loggerDict:  # pylint: disable=no-member
    if name.startswith("uvicorn"):
        logging.getLogger(name).handlers.clear()

# pylint: disable=protected-access
logging.getLogger("uvicorn.error").addHandler(logger._handler)
logging.getLogger("uvicorn.error").propagate = False
