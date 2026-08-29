from fastapi import APIRouter
from .auth import router as auth_router
from .ulcers import router as ulcers_router
from .expert import router as expert_router
from .knowledge import router as knowledge_router
from .patients import router as patients_router
from .analytics import router as analytics_router
from .billing import router as billing_router
from .inventory import router as inventory_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(ulcers_router, prefix="/ulcers", tags=["疮疡会诊"])
api_router.include_router(expert_router, prefix="/expert", tags=["专家服务"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["知识库"])
api_router.include_router(patients_router, prefix="/patients", tags=["患者管理"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["数据分析"])
api_router.include_router(billing_router, prefix="/billing", tags=["收费管理"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["库存管理"])
