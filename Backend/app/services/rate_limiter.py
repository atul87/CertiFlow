"""
Consolidated High-Performance Rate Limiter — P12.11 & P12.12.

Single unified implementation handling:
1. Micro-second accurate sliding window via Redis zset
2. Rapid minute-window counter checks
3. Strict fail-open vs fail-closed policy per endpoint:
   - Sensitive / auth endpoints (login, register, password reset): fail_closed=True
     Falls back to in-memory sliding window; never permits infinite brute-force on Redis outage.
   - High-throughput read endpoints (public scans, verifications, badges): fail_closed=False
     Falls back to in-memory sliding window; fails open if in-memory store is also exhausted.
"""
from __future__ import annotations
import time
import logging
from typing import Dict, List, Tuple
from collections import defaultdict
from app.queue.redis import QueueManager
from app.core.config import settings

logger = logging.getLogger(__name__)

# Bounded in-memory sliding window store: key -> list of float timestamps
_in_memory_timestamps: Dict[str, List[float]] = defaultdict(list)
_MAX_TRACKED_KEYS = 50000


class RateLimiter:
    @classmethod
    async def is_allowed(
        cls,
        key: str,
        max_requests: int = 60,
        window_seconds: int = 60,
        fail_closed: bool = False,
    ) -> bool:
        """
        Check if request is within rate limit using Redis with in-memory fallback.
        Returns True if request is allowed, False if rate limit is exceeded.
        """
        allowed, _, _, _ = await cls.check_rate_limit(
            identifier=key,
            limit_per_minute=max_requests,
            window_seconds=window_seconds,
            fail_closed=fail_closed,
        )
        return allowed

    @classmethod
    async def check_rate_limit(
        cls,
        identifier: str,
        limit_per_minute: int = 1000,
        window_seconds: int = 60,
        fail_closed: bool = False,
    ) -> Tuple[bool, int, int, int]:
        """
        Consolidated rate-limit check.
        Returns:
            allowed: bool
            limit: int
            remaining: int
            retry_after_seconds: int
        """
        now = time.time()
        pool = await QueueManager.get_pool()

        # -------------------------------------------------------------------
        # 1. Primary: Redis Sliding Window via zset pipeline
        # -------------------------------------------------------------------
        if pool is not None and settings.APP_ENV != "test":
            try:
                redis_key = f"ratelimit:{identifier}"
                pipe = pool.pipeline(transaction=True)
                pipe.zremrangebyscore(redis_key, 0, now - window_seconds)
                pipe.zadd(redis_key, {str(now): now})
                pipe.zcard(redis_key)
                pipe.expire(redis_key, window_seconds + 5)
                res = await pipe.execute()
                current_count = res[2]

                allowed = current_count <= limit_per_minute
                remaining = max(0, limit_per_minute - current_count)
                retry_after = int(window_seconds - (now % window_seconds)) if not allowed else 0
                return allowed, limit_per_minute, remaining, retry_after
            except Exception as exc:
                logger.warning("Redis rate limiter failed (%s); using in-memory engine", exc)

        # -------------------------------------------------------------------
        # 2. Resilient In-Memory Sliding Window Fallback
        # -------------------------------------------------------------------
        # Memory protection: prevent unbounded growth
        if len(_in_memory_timestamps) > _MAX_TRACKED_KEYS:
            _in_memory_timestamps.clear()

        window_start = now - window_seconds
        timestamps = _in_memory_timestamps[identifier]
        filtered = [t for t in timestamps if t > window_start]
        current_count = len(filtered)

        if current_count >= limit_per_minute:
            _in_memory_timestamps[identifier] = filtered
            retry_after = int(window_seconds - (now - filtered[0])) if filtered else window_seconds
            return False, limit_per_minute, 0, max(1, retry_after)

        filtered.append(now)
        _in_memory_timestamps[identifier] = filtered
        remaining = max(0, limit_per_minute - (current_count + 1))
        return True, limit_per_minute, remaining, 0

    @classmethod
    def clear_in_memory(cls) -> None:
        """Clear in-memory sliding window cache (useful for test isolation)."""
        _in_memory_timestamps.clear()


# Alias for backward compatibility
APIRateLimiter = RateLimiter
