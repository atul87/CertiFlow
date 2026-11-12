import os
from typing import Dict, Any
from fastapi import APIRouter, status, Response
from starlette.responses import JSONResponse
from app.core.config import settings
from app.core.database import DatabaseManager
from app.queue.redis import QueueManager
from app.services.storage_service import StorageService
from app.core.metrics import metrics

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", summary="Basic service health check")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "certificate-api",
        "version": settings.VERSION
    }


@router.get("/health/db", summary="MongoDB connectivity health check")
async def db_health_check() -> Dict[str, Any]:
    try:
        db = DatabaseManager.get_db()
        await db.command("ping")
        return {
            "status": "ok",
            "database": "connected",
            "name": settings.MONGODB_DATABASE
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/health/ready", summary="Readiness probe for load balancers and orchestrators")
async def readiness_check():
    """
    Validates core external dependencies required to serve requests:
    - MongoDB connectivity
    - Redis queue broker
    - Local / Object storage write accessibility
    Returns HTTP 200 if ready, or HTTP 503 Service Unavailable if degraded.
    """
    dependencies = {}
    is_ready = True

    # 1. MongoDB Check
    try:
        db = DatabaseManager.get_db()
        await db.command("ping")
        dependencies["mongodb"] = "ok"
    except Exception as e:
        dependencies["mongodb"] = f"error: {str(e)}"
        is_ready = False

    # 2. Redis Check
    try:
        redis = await QueueManager.get_redis()
        if redis:
            await redis.ping()
            dependencies["redis"] = "ok"
        else:
            dependencies["redis"] = "disabled_or_unavailable"
    except Exception as e:
        dependencies["redis"] = f"error: {str(e)}"
        # Redis failure can be non-fatal if running in test environment
        if settings.APP_ENV == "production":
            is_ready = False

    # 3. Storage Check
    try:
        probe_key = f".health-probe/{os.urandom(8).hex()}"
        StorageService.save_bytes(b"probe", probe_key, "text/plain")
        if StorageService.read_file(probe_key) != b"probe":
            raise RuntimeError("Storage probe read-back failed")
        StorageService.delete_file(probe_key)
        dependencies["storage"] = "ok"
    except Exception as e:
        dependencies["storage"] = f"error: {str(e)}"
        is_ready = False

    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "dependencies": dependencies,
            "version": settings.VERSION,
            "environment": settings.APP_ENV
        }
    )


@router.get("/version", summary="Application version metadata")
async def get_version() -> Dict[str, Any]:
    return {
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "commit": getattr(settings, "BUILD_COMMIT", "certiflow-p9-prod")
    }


@router.get("/build", summary="Internal build and service metadata")
async def get_build() -> Dict[str, Any]:
    return {
        "service": "certificate-api",
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "commit": getattr(settings, "BUILD_COMMIT", "certiflow-p9-prod"),
        "debug": settings.DEBUG
    }


@router.get("/metrics", summary="Prometheus metrics exporter")
async def get_metrics():
    """Returns application metrics formatted for Prometheus scraping."""
    content = metrics.generate_prometheus_text()
    return Response(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")
