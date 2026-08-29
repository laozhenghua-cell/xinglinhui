from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TCM Ulcer Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"

    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "ulcer_user"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "tcm_ulcer"
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # AI - 千问视觉
    QWEN_API_KEY: str
    QWEN_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_VISION_MODEL: str = "qwen-vl-max-latest"

    # File Storage
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/jpg"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # Expert Consultation
    DEFAULT_CONSULTATION_FEE: int = 100
    PLATFORM_COMMISSION_RATE: float = 0.25

    # Notification
    ENABLE_WEBSOCKET: bool = True
    ENABLE_EMAIL: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
