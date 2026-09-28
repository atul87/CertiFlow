from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import DatabaseManager
from app.middleware.request_id import RequestContextMiddleware
from app.middleware.error_handler import register_error_handlers
from app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    await DatabaseManager.connect()
    yield
    # Shutdown
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

    # 2. CORS Middleware
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

    # 4. Root /health endpoint
    @app.get("/health", tags=["Health"], summary="Root health check")
    async def root_health():
        return {
            "status": "ok",
            "service": "certificate-api",
            "version": settings.VERSION
        }

    # 5. Mount API v1 router
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
