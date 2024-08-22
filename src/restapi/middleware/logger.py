import time
import traceback
from http import HTTPStatus

import loggingx as logging
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


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

            # FastAPI custom exceptions are already handled before this point.
            # ex) HTTPException, RequestValidationError, WebSocketRequestValidationError
        except Exception:
            res = Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
            error = traceback.format_exc()

        latency = time.time() - start_time

        with logging.addFields(
            method=request.method,
            url=path,
            status=res.status_code,
            remote_address=request.client.host if request.client is not None else "",
            user_agent=request.headers.get("user-agent", ""),
            latency=latency,
        ):
            if error:
                # TODO: if debug mode, dump request body
                logging.error(error)
                logging.error(await self._dump_request(request))
            else:
                logging.info("request")

        return res
