import time
import traceback
from http import HTTPStatus

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from internal.pkg import logger


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
        with logger.new_context():
            start_time = time.time()
            path = request.url.path

            request.state.errors = []
            res = await call_next(request)

            latency = time.time() - start_time
            logger.set_fields(user_id=getattr(request.state, "user_id", -1))
            logger.set_fields(request_id=request.headers.get("x-request-id", ""))

            errors = request.state.errors
            _log = logger.contextual_logger().bind(
                method=request.method,
                url=path,
                status=res.status_code,
                remote_address=request.client.host if request.client is not None else "",
                user_agent=request.headers.get("user-agent", ""),
                latency=latency,
            )

            if len(errors) > 0:
                errors.append(await self._dump_request(request))

                for i, error in enumerate(errors):
                    _log.error(
                        str(i),
                        extra={
                            "error": str(error),
                        },
                    )
            else:
                _log.info(
                    path,
                )
            return res


class Recovery(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except:
            request.state.errors.append(traceback.format_exc())
            return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
