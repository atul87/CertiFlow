"""
JWT JTI Revocation Blacklist — P12.10.
Stores revoked JWT JTI identifiers in Redis with automatic TTL expiration.
Falls back to in-memory sliding TTL cache if Redis is offline or in testing.
"""
from __future__ import annotations
import time
import logging
from typing import Dict, Optional
from app.queue.redis import QueueManager

logger = logging.getLogger(__name__)

# In-memory fallback: jti -> expiration timestamp
_in_memory_revoked_jtis: Dict[str, float] = {}


class TokenBlacklist:
    @classmethod
    async def revoke_jti(cls, jti: str, ttl_seconds: int = 1800) -> None:
        """Revoke a token's JTI until its original expiration timestamp."""
        if not jti or ttl_seconds <= 0:
            return

        now = time.time()
        # Always record in-memory fallback
        _in_memory_revoked_jtis[jti] = now + ttl_seconds

        # Record in Redis if available
        pool = await QueueManager.get_pool()
        if pool is not None:
            try:
                redis_key = f"jwt_blacklist:{jti}"
                await pool.set(redis_key, "revoked", ex=ttl_seconds)
                logger.info("Blacklisted JWT JTI %s for %d seconds in Redis", jti, ttl_seconds)
            except Exception as exc:
                logger.warning("Could not write JTI blacklist to Redis (%s); cached in-memory", exc)

    @classmethod
    async def is_jti_revoked(cls, jti: Optional[str]) -> bool:
        """Check if a token's JTI has been blacklisted/revoked."""
        if not jti:
            return False

        now = time.time()

        # Check Redis first
        pool = await QueueManager.get_pool()
        if pool is not None:
            try:
                redis_key = f"jwt_blacklist:{jti}"
                val = await pool.get(redis_key)
                if val:
                    return True
            except Exception as exc:
                logger.warning("Could not read JTI blacklist from Redis (%s); checking in-memory", exc)

        # Check in-memory fallback
        exp = _in_memory_revoked_jtis.get(jti)
        if exp:
            if exp > now:
                return True
            else:
                _in_memory_revoked_jtis.pop(jti, None)

        return False

    @classmethod
    def clear_in_memory(cls) -> None:
        """Helper for test cleanup."""
        _in_memory_revoked_jtis.clear()
