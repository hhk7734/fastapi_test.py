import uuid

import loggingx as logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class RequestID(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-Id")
        if request_id is None:
            request_id = str(uuid.uuid4())

        with logging.addFields(request_id=request_id):
            res = await call_next(request)

        res.headers["X-Request-Id"] = request_id
        return res
