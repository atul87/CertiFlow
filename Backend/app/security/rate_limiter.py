"""
Redis-based API Rate Limiter (P8).
Enforces requests-per-minute quotas for API keys and Organizations.
"""
from __future__ import annotations
import time
import logging
from typing import Tuple
from app.queue.redis import QueueManager
from app.core.config import settings

logger = logging.getLogger(__name__)


class APIRateLimiter:
    @classmethod
    async def check_rate_limit(
        cls,
        identifier: str,
        limit_per_minute: int = 1000,
    ) -> Tuple[bool, int, int, int]:
        """
        Check rate limit for a given identifier (API key ID or Org ID).
        Returns:
            allowed: bool
            limit: int
            remaining: int
            retry_after_seconds: int
        """
        redis = await QueueManager.get_redis()
        if not redis or settings.APP_ENV == "test":
            # Allow without blocking if Redis is offline or running tests
            return True, limit_per_minute, limit_per_minute - 1, 0

        now = int(time.time())
        window = now // 60
        key = f"ratelimit:{identifier}:{window}"

        try:
            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, 65)  # Auto-expire after 65 seconds

            remaining = max(0, limit_per_minute - current)
            allowed = current <= limit_per_minute
            retry_after = 60 - (now % 60) if not allowed else 0
            return allowed, limit_per_minute, remaining, retry_after
        except Exception as e:
            logger.warning(f"Rate limiter Redis check failed ({e}); failing open")
            return True, limit_per_minute, limit_per_minute, 0
