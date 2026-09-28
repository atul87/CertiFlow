import logging
from typing import Optional
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_redis_settings() -> RedisSettings:
    rs = RedisSettings.from_dsn(settings.REDIS_URL)
    rs.conn_timeout = 1
    rs.conn_retries = 0
    return rs


class QueueManager:
    _pool: Optional[ArqRedis] = None
    _last_attempt_time: float = 0
    _failed_attempt: bool = False

    @classmethod
    async def get_pool(cls) -> Optional[ArqRedis]:
        if cls._pool is not None:
            return cls._pool
        import time
        now = time.time()
        # Cooldown 15s if previous attempt failed
        if cls._failed_attempt and (now - cls._last_attempt_time < 15):
            return None
        cls._last_attempt_time = now
        try:
            redis_settings = get_redis_settings()
            cls._pool = await create_pool(redis_settings)
            cls._failed_attempt = False
            logger.info("Connected to Redis ARQ pool at %s", settings.REDIS_URL)
        except Exception as exc:
            cls._failed_attempt = True
            logger.warning("Could not connect to Redis ARQ pool: %s", exc)
            return None
        return cls._pool

    @classmethod
    async def close(cls) -> None:
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
            logger.info("Closed Redis ARQ pool.")

    @classmethod
    async def enqueue(cls, task_name: str, *args, **kwargs) -> bool:
        """Enqueue task into ARQ Redis queue. Returns True if successfully queued."""
        pool = await cls.get_pool()
        if pool is None:
            logger.warning("Redis pool not available; cannot enqueue task '%s'", task_name)
            return False
        try:
            await pool.enqueue_job(task_name, *args, **kwargs)
            logger.info("Enqueued ARQ job: %s with args=%s kwargs=%s", task_name, args, kwargs)
            return True
        except Exception as exc:
            logger.error("Failed to enqueue job %s: %s", task_name, exc)
            return False
