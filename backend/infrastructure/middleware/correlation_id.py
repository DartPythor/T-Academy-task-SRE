from __future__ import annotations

import uuid
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления correlation_id к каждому запросу.

    Correlation ID позволяет связывать логи одного запроса воедино,
    что критично для распределённых систем и микросервисной архитектуры.

    Если клиент передаёт X-Correlation-ID — используем его,
    иначе генерируем новый UUID.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get(
            "X-Correlation-ID",
            str(uuid.uuid4()),
        )
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
