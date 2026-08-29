from pydantic_settings import BaseSettings
from typing import Optional

# 已知弱密钥（拒绝使用，防止 JWT 伪造）
_WEAK_SECRETS = {
    "",
    "your-secret-key-change-in-production",
    "zhilou-secret-key-change-in-production",
    "secret",
    "changeme",
    "password",
}


class Settings(BaseSettings):
    APP_NAME: str = "华夏痔瘘辅助诊疗系统"
    APP_ENV: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://zhilou_user:ZhiLou2026@localhost:5432/zhilou_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 密钥：必须在环境变量中提供强随机值，不留弱默认
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # 允许的跨域来源（逗号分隔），生产环境应仅配置自己的域名
    CORS_ORIGINS: str = "http://localhost:8080,http://localhost:8088"

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-vl-max"

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024

    SENTRY_DSN: Optional[str] = None

    TRIAL_DAYS: int = 30

    # 全开放模式：true 时 get_current_user 允许无凭证请求，
    # 自动落到"公开用户/公开租户"，使所有依赖登录的路由无需登录即可用。
    OPEN_ACCESS: bool = False

    # 访问统计 IP 哈希加盐（不存明文 IP）；为空时回退到 SECRET_KEY。
    VISIT_SALT: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def DEBUG(self) -> bool:
        """仅在非生产环境开启调试（关闭 SQL echo 与详细错误）。"""
        return self.APP_ENV.lower() not in {"production", "prod"}

    @property
    def cors_origins_list(self) -> list:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def visit_salt(self) -> str:
        """IP 哈希加盐值：优先 VISIT_SALT，否则回退到 SECRET_KEY。"""
        return self.VISIT_SALT or self.SECRET_KEY

    def validate_secret(self) -> None:
        if self.SECRET_KEY in _WEAK_SECRETS or len(self.SECRET_KEY) < 32:
            raise RuntimeError(
                "SECRET_KEY 缺失或过弱：请通过环境变量提供至少 32 位的强随机密钥。"
            )


settings = Settings()
