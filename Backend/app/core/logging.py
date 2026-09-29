"""
Structured Logging Engine — P12.25.
Enriches log output with request_id, job_id, organization_id, and certificate_id using Python contextvars.
"""
from __future__ import annotations
import sys
import logging
from contextvars import ContextVar
from typing import Optional
from app.core.config import settings

# Context variables for distributed tracing & structured logging
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
job_id_ctx: ContextVar[str] = ContextVar("job_id", default="")
org_id_ctx: ContextVar[str] = ContextVar("org_id", default="")
certificate_id_ctx: ContextVar[str] = ContextVar("certificate_id", default="")


def set_log_context(
    request_id: Optional[str] = None,
    job_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    certificate_id: Optional[str] = None,
) -> None:
    if request_id is not None:
        request_id_ctx.set(request_id)
    if job_id is not None:
        job_id_ctx.set(job_id)
    if organization_id is not None:
        org_id_ctx.set(organization_id)
    if certificate_id is not None:
        certificate_id_ctx.set(certificate_id)


class StructuredLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(record, "request_id", None) or request_id_ctx.get() or "-"
        record.job_id = getattr(record, "job_id", None) or job_id_ctx.get() or "-"
        record.organization_id = getattr(record, "organization_id", None) or org_id_ctx.get() or "-"
        record.certificate_id = getattr(record, "certificate_id", None) or certificate_id_ctx.get() or "-"
        return True


def setup_logging() -> None:
    """Configure structured logging for CertiFlow backend."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Custom structured formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] [req=%(request_id)s org=%(organization_id)s job=%(job_id)s cert=%(certificate_id)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(StructuredLogFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if reloaded
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

    # Suppress verbose noisy loggers if in non-debug
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.INFO)
