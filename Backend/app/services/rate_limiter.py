from __future__ import annotations
import time
import logging
from typing import Dict, List
from collections import defaultdict
from app.queue.redis import QueueManager

logger = logging.getLogger(__name__)

# In-memory sliding window store: ip/key -> list of timestamps
_in_memory_timestamps: Dict[str, List[float]] = defaultdict(list)


class RateLimiter:
    @classmethod
    async def is_allowed(
        cls,
        key: str,
        max_requests: int = 60,
        window_seconds: int = 60,
    ) -> bool:
        """
        Check if request is within rate limit using Redis if available, with in-memory fallback.
        """
        pool = await QueueManager.get_pool()
        now = time.time()

        if pool is not None:
            try:
                redis_key = f"rate_limit:{key}"
                pipe = pool.pipeline(transaction=True)
                pipe.zremrangebyscore(redis_key, 0, now - window_seconds)
                pipe.zadd(redis_key, {str(now): now})
                pipe.zcard(redis_key)
                pipe.expire(redis_key, window_seconds)
                res = await pipe.execute()
                current_count = res[2]
                return current_count <= max_requests
            except Exception as exc:
                logger.warning("Redis rate limiter failed (%s), falling back to in-memory", exc)

        # In-memory fallback sliding window
        window_start = now - window_seconds
        timestamps = _in_memory_timestamps[key]
        # Filter timestamps older than window
        _in_memory_timestamps[key] = [t for t in timestamps if t > window_start]
        if len(_in_memory_timestamps[key]) >= max_requests:
            return False
        _in_memory_timestamps[key].append(now)
        return True
