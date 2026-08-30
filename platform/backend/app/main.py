import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse

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

from app.core.observability import ObservabilityMiddleware, metrics_text

app.add_middleware(ObservabilityMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 上传文件静态服务(疮疡 book 图版等 /uploads/... 直接可访问;目录需在挂载前存在)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

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
from app.api.v1.visits import router as visits_router
from app.api.v1.public_stats import router as public_stats_router
from app.api.v1.dx import router as dx_router
from app.api.v1.learn import router as learn_router
from app.api.v1.clinic import router as clinic_router
from app.api.v1.kb import router as kb_router

# 疮疡(外科)模块
from app.api.v1.surgery import diseases as surgery_diseases
from app.api.v1.surgery import syndromes as surgery_syndromes
from app.api.v1.surgery import formulas as surgery_formulas
from app.api.v1.surgery import treatment as surgery_treatment
from app.api.v1.surgery import diagnosis as surgery_diagnosis
from app.api.v1.surgery import cases as surgery_cases
from app.api.v1.surgery import patients as surgery_patients
from app.api.v1.surgery import stats as surgery_stats
from app.api.v1.surgery import expert as surgery_expert
from app.api.v1.surgery import images as surgery_images
from app.api.v1.surgery import tips as surgery_tips
from app.api.v1.surgery import search as surgery_search

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

# 访问统计(免鉴权)
app.include_router(visits_router, prefix="/api/v1")
app.include_router(public_stats_router, prefix="/api/v1")
app.include_router(dx_router, prefix="/api/v1")
app.include_router(learn_router, prefix="/api/v1")
app.include_router(clinic_router, prefix="/api/v1")

# 统一共用知识总库(免鉴权)
app.include_router(kb_router, prefix="/api/v1")

# 词库管理(口语映射增删改)
from app.api.v1.admin import router as admin_router

app.include_router(admin_router, prefix="/api/v1")

# 疮疡(外科)模块：各路由 prefix 已含 /api/v1/surgery/...
app.include_router(surgery_diseases.router)
app.include_router(surgery_syndromes.router)
app.include_router(surgery_formulas.router)
app.include_router(surgery_treatment.router)
app.include_router(surgery_diagnosis.router)
app.include_router(surgery_cases.router)
app.include_router(surgery_patients.router)
app.include_router(surgery_stats.router)
app.include_router(surgery_expert.router)
app.include_router(surgery_images.router)
app.include_router(surgery_tips.router)
app.include_router(surgery_search.router)


@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus 指标(可观测性)。"""
    return PlainTextResponse(metrics_text())


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
