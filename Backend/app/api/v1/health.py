from typing import Dict, Any
from fastapi import APIRouter, status
from app.core.config import settings
from app.core.database import DatabaseManager

router = APIRouter(tags=["Health"])


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
