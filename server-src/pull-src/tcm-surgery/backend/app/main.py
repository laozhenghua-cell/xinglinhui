"""FastAPI 主应用"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from .routers import cases, diagnosis, diseases, expert, formulas, images, patients, search, stats, syndromes, tips, treatment


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# CORS:仅允许配置的来源(默认本地开发前端)
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 上传图片静态服务(目录需在挂载前存在)
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(diseases.router)
app.include_router(syndromes.router)
app.include_router(formulas.router)
app.include_router(treatment.router)
app.include_router(diagnosis.router)
app.include_router(cases.router)
app.include_router(patients.router)
app.include_router(stats.router)
app.include_router(expert.router)
app.include_router(images.router)
app.include_router(tips.router)
app.include_router(search.router)


@app.get("/")
async def root():
    return {"app": settings.app_name, "status": "ok"}
