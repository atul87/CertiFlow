import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from app.core.config import settings

logger = logging.getLogger("certiflow.http")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 1. Establish or extract Request-ID
        req_id = request.headers.get("X-Request-ID")
        if not req_id:
            req_id = f"req_{uuid.uuid4().hex[:12]}"

        request.state.request_id = req_id

        # 2. Track timing
        start_time = time.perf_counter()

        # 3. Process request
        try:
            response = await call_next(request)
        except Exception:
            # If an unhandled exception occurred, measure time and re-raise for the error handler
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_failed request_id=%s method=%s path=%s duration=%.2fms",
                req_id,
                request.method,
                request.url.path,
                duration_ms
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000

        # 4. Attach X-Request-ID header to response
        response.headers["X-Request-ID"] = req_id

        # 5. Structured HTTP access log (never log passwords or auth headers)
        logger.info(
            "request_id=%s method=%s path=%s status=%s duration=%.2fms",
            req_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms
        )

        # 6. Record Prometheus metrics
        if getattr(settings, "ENABLE_PROMETHEUS_METRICS", True):
            try:
                from app.core.metrics import metrics
                duration_sec = time.perf_counter() - start_time
                metrics.record_http_request(request.method, request.url.path, response.status_code, duration_sec)
            except Exception:
                pass

        return response

