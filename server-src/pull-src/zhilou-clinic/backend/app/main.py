import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings.validate_secret()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    await init_db()
    yield
    # Shutdown


if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.2)

app = FastAPI(
    title=settings.APP_NAME,
    description="华夏痔瘘辅助诊疗系统 - 中西医结合肛肠病诊疗管理平台",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.v1.auth import router as auth_router
from app.api.v1.patients import router as patients_router
from app.api.v1.consultations import router as consultations_router
from app.api.v1.billing import router as billing_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.vision import router as vision_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.stats import router as stats_router
from app.api.v1.uploads import router as uploads_router
from app.api.v1.followup import router as followup_router
from app.api.v1.diagnosis import router as diagnosis_router
from app.api.v1.external_treatment import router as external_treatment_router
from app.api.v1.medical_cases import router as medical_cases_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(patients_router, prefix="/api/v1")
app.include_router(consultations_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(vision_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")
app.include_router(uploads_router, prefix="/api/v1")
app.include_router(followup_router, prefix="/api/v1")
app.include_router(diagnosis_router, prefix="/api/v1/diagnosis", tags=["辨证诊断"])
app.include_router(external_treatment_router, prefix="/api/v1", tags=["外治法"])
app.include_router(medical_cases_router, prefix="/api/v1", tags=["医案库"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }


@app.get("/api/health", include_in_schema=False)
async def api_health_check():
    return await health_check()


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
    }
