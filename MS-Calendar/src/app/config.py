from pydantic import AnyUrl
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    app_name: str = "MS-Calendar"
    app_version: str = "1.0.0"
    debug: bool = False
    
    database_url: str = "sqlite+aiosqlite:///./calendar.db"
    
    host: str = "0.0.0.0"
    port: int = 8000
    
    cors_origins: list[str] = ["*"]
    
    ms_auth_url: str = "http://localhost:8001"
    ms_user_url: str = "http://localhost:8002"

    sports_api_key: str = ""
    sports_api_url: str = ""
    
    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
