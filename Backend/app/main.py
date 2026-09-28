from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import DatabaseManager
from app.queue.redis import QueueManager
from app.middleware.request_id import RequestContextMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.error_handler import register_error_handlers
from app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    await DatabaseManager.connect()
    from app.repositories.plan_repository import PlanRepository
    await PlanRepository.ensure_default_plans()
    yield
    # Shutdown
    await QueueManager.close()
    await DatabaseManager.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="High-performance Certificate Automation SaaS API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # 1. Custom Request ID & Structured Logging Middleware
    app.add_middleware(RequestContextMiddleware)

    # 2. Production Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # 3. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"]
    )

    # 3. Register centralized error handlers
    register_error_handlers(app)

    # 4. Root health & metrics endpoints
    @app.get("/health", tags=["Health"], summary="Root health check")
    async def root_health():
        return {
            "status": "ok",
            "service": "certificate-api",
            "version": settings.VERSION
        }

    @app.get("/health/ready", tags=["Health"], summary="Root readiness probe")
    async def root_health_ready():
        from app.api.v1.health import readiness_check
        return await readiness_check()

    @app.get("/metrics", tags=["Observability"], summary="Root Prometheus metrics")
    async def root_metrics():
        from app.api.v1.health import get_metrics
        return await get_metrics()

    # 5. Mount API v1 router
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
