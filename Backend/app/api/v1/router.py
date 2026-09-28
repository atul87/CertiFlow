from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.health import router as health_router

from app.api.v1.templates import router as templates_router
from app.api.v1.fonts import router as fonts_router
from app.api.v1.imports import router as imports_router
from app.api.v1.mapping_profiles import router as mapping_profiles_router
from app.api.v1.certificates import router as certificates_router
from app.api.v1.issuance_jobs import router as issuance_jobs_router
from app.api.v1.public import router as public_router
from app.api.v1.email_templates import router as email_templates_router
from app.api.v1.email import router as email_router
from app.api.v1.email_jobs import router as email_jobs_router
from app.api.v1.email_deliveries import router as email_deliveries_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.reports import router as reports_router
from app.api.v1.activity import router as activity_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(organizations_router)
api_v1_router.include_router(templates_router)
api_v1_router.include_router(fonts_router)
api_v1_router.include_router(imports_router)
api_v1_router.include_router(mapping_profiles_router)
api_v1_router.include_router(certificates_router)
api_v1_router.include_router(issuance_jobs_router)
api_v1_router.include_router(public_router)
api_v1_router.include_router(email_templates_router)
api_v1_router.include_router(email_router)
api_v1_router.include_router(email_jobs_router)
api_v1_router.include_router(email_deliveries_router)
api_v1_router.include_router(webhooks_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(activity_router)
