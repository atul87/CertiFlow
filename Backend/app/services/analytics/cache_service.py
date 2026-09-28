from __future__ import annotations
import json
import hashlib
import logging
from typing import Optional, Any, Callable
from app.core.config import settings

logger = logging.getLogger(__name__)


class AnalyticsCacheService:
    @staticmethod
    def _make_key(org_id: str, category: str, params: dict) -> str:
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:12]
        return f"analytics:{org_id}:{category}:{param_hash}"

    @classmethod
    async def get_or_set(
        cls,
        org_id: str,
        category: str,
        params: dict,
        compute_fn: Callable[[], Any],
        ttl_seconds: Optional[int] = None,
    ) -> Any:
        """
        Check cache for analytics computation, otherwise run compute_fn and cache result.
        Gracefully falls back to direct execution if Redis is unavailable.
        """
        ttl = ttl_seconds or settings.ANALYTICS_CACHE_TTL_SECONDS
        cache_key = cls._make_key(org_id, category, params)

        # Attempt to get Redis client if available
        try:
            from app.queue.redis import QueueManager
            pool = QueueManager._pool
            if pool:
                cached = await pool.get(cache_key)
                if cached:
                    return json.loads(cached)
        except Exception as e:
            logger.debug(f"[AnalyticsCache] Redis get error: {e}")

        # Compute
        result = await compute_fn()

        # Cache result
        try:
            from app.queue.redis import QueueManager
            pool = QueueManager._pool
            if pool and result is not None:
                json_data = json.dumps(result, default=str)
                await pool.set(cache_key, json_data, ex=ttl)
        except Exception as e:
            logger.debug(f"[AnalyticsCache] Redis set error: {e}")

        return result
