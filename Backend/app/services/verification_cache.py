from __future__ import annotations
import json
import logging
import time
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.queue.redis import QueueManager

logger = logging.getLogger(__name__)

# In-memory cache fallback: code -> (data, expires_at)
_in_memory_cache: Dict[str, tuple[Dict[str, Any], float]] = {}


class VerificationCache:
    @classmethod
    async def get(cls, code: str) -> Optional[Dict[str, Any]]:
        norm_code = code.upper().strip()
        pool = await QueueManager.get_pool()

        if pool is not None:
            try:
                raw = await pool.get(f"verification:{norm_code}")
                if raw:
                    return json.loads(raw)
            except Exception as exc:
                logger.warning("Redis cache get failed: %s", exc)

        # In-memory fallback
        if norm_code in _in_memory_cache:
            data, exp = _in_memory_cache[norm_code]
            if time.time() < exp:
                return data
            else:
                del _in_memory_cache[norm_code]

        return None

    @classmethod
    async def set(cls, code: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        norm_code = code.upper().strip()
        expire_sec = ttl or settings.VERIFICATION_CACHE_TTL_SECONDS
        pool = await QueueManager.get_pool()

        if pool is not None:
            try:
                await pool.set(
                    f"verification:{norm_code}",
                    json.dumps(data, default=str),
                    ex=expire_sec,
                )
            except Exception as exc:
                logger.warning("Redis cache set failed: %s", exc)

        # Also store in memory
        _in_memory_cache[norm_code] = (data, time.time() + expire_sec)

    @classmethod
    async def invalidate(cls, code: str) -> None:
        norm_code = code.upper().strip()
        pool = await QueueManager.get_pool()

        if pool is not None:
            try:
                await pool.delete(f"verification:{norm_code}")
            except Exception as exc:
                logger.warning("Redis cache invalidate failed: %s", exc)

        if norm_code in _in_memory_cache:
            del _in_memory_cache[norm_code]

    @classmethod
    async def invalidate_many(cls, codes: List[str]) -> None:
        for code in codes:
            await cls.invalidate(code)
