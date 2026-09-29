import logging
from typing import Optional
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_redis_settings() -> RedisSettings:
    rs = RedisSettings.from_dsn(settings.REDIS_URL)
    rs.conn_timeout = 1 if settings.APP_ENV == "test" else 2
    rs.conn_retries = 1 if settings.APP_ENV == "test" else 2
    return rs


class QueueManager:
    """Manages Redis ARQ connection pool with automatic self-healing and reconnection — P12.03."""
    _pool: Optional[ArqRedis] = None
    _last_attempt_time: float = 0
    _failed_attempt: bool = False

    @classmethod
    async def reset_pool(cls) -> None:
        """Reset and invalidate cached Redis pool to allow self-healing reconnection."""
        if cls._pool is not None:
            try:
                await cls._pool.close()
            except Exception:
                pass
            cls._pool = None
        cls._failed_attempt = False

    @classmethod
    async def get_pool(cls) -> Optional[ArqRedis]:
        """Return healthy Redis connection pool or establish a new connection if disconnected."""
        if cls._pool is not None:
            try:
                # Active ping probe to ensure connection is healthy
                await cls._pool.ping()
                return cls._pool
            except Exception as exc:
                logger.warning("Redis pool disconnected (%s); resetting pool for reconnection", exc)
                await cls.reset_pool()

        import time
        now = time.time()
        # Cooldown: 10s in test to avoid slow loops, 2s in production/staging to allow prompt self-healing
        cooldown = 10 if settings.APP_ENV == "test" else 2
        if cls._failed_attempt and (now - cls._last_attempt_time < cooldown):
            return None
        cls._last_attempt_time = now
        try:
            redis_settings = get_redis_settings()
            cls._pool = await create_pool(redis_settings)
            cls._failed_attempt = False
            logger.info("Connected to Redis ARQ pool at %s", settings.REDIS_URL)
        except Exception as exc:
            cls._failed_attempt = True
            cls._pool = None
            logger.warning("Could not connect to Redis ARQ pool: %s", exc)
            return None
        return cls._pool

    get_redis = get_pool

    @classmethod
    async def close(cls) -> None:
        await cls.reset_pool()
        logger.info("Closed Redis ARQ pool.")

    @classmethod
    async def enqueue(cls, task_name: str, *args, **kwargs) -> bool:
        """Enqueue task into ARQ Redis queue with self-healing on connection failure."""
        pool = await cls.get_pool()
        if pool is None:
            logger.warning("Redis pool not available; cannot enqueue task '%s'", task_name)
            return False
        try:
            await pool.enqueue_job(task_name, *args, **kwargs)
            logger.info("Enqueued ARQ job: %s with args=%s kwargs=%s", task_name, args, kwargs)
            return True
        except Exception as exc:
            logger.error("Failed to enqueue job %s: %s; resetting Redis pool", task_name, exc)
            await cls.reset_pool()
            return False
