from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # GitHub App
    github_app_id: str
    github_app_private_key_path: str
    
    # LLM
    anthropic_api_key: str
    llm_model: str = "claude-sonnet-4-20250514"
    
    # Database
    database_url: str
    supabase_url: str | None = None
    supabase_key: str | None = None
    
    # Redis & Celery
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str
    
    # Application
    environment: str = "development"
    debug: bool = True
    api_secret_key: str
    
    # Review Configuration
    auto_review_enabled: bool = True
    review_command: str = "/review"
    max_files_to_review: int = 10
    max_diff_size: int = 5000
    enable_memory_persistence: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
