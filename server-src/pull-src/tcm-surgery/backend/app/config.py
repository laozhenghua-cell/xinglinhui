"""应用配置"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "中医外科疮疡辅助诊疗系统"
    # 默认使用本地 SQLite(零依赖即可跑),生产环境在 .env 里换成 PostgreSQL
    database_url: str = "sqlite+aiosqlite:///./data/surgery.db"

    # 上传图片存储目录
    upload_dir: str = "./uploads"
    # 上传图片大小上限(字节),默认 10MB
    max_upload_size: int = 10 * 1024 * 1024
    # CORS 允许的来源(逗号分隔)
    cors_origins: str = "http://localhost:5180,http://127.0.0.1:5180"

    # DeepSeek(文本)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # 通义千问 QWEN Vision(拍照辨病,OpenAI 兼容接口)
    qwen_api_key: str = ""
    qwen_api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_vision_model: str = "qwen-vl-max"


settings = Settings()
