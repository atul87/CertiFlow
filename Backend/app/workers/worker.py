from __future__ import annotations
import logging
from arq.connections import RedisSettings
from app.core.config import settings
from app.core.database import DatabaseManager
from app.queue.redis import get_redis_settings
from app.workers.certificate_worker import generate_bulk_certificates_task
from app.workers.zip_worker import create_zip_task

logger = logging.getLogger(__name__)


async def startup(ctx: dict):
    logger.info("Initializing worker process: connecting to database...")
    await DatabaseManager.connect()
    logger.info("Worker database connection established.")


async def shutdown(ctx: dict):
    logger.info("Shutting down worker process...")
    await DatabaseManager.close()
    logger.info("Worker database connection closed.")


class WorkerSettings:
    """ARQ Worker configuration settings."""
    functions = [
        generate_bulk_certificates_task,
        create_zip_task,
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = get_redis_settings()
    max_jobs = settings.WORKER_CONCURRENCY
    job_timeout = settings.RENDER_TIMEOUT_SECONDS * 10
