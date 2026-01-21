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
    
    # RabbitMQ
    rabbitmq_host: str = "localhost"
    rabbitmq_user: str = "user"
    rabbitmq_password: str = "password"
    rabbitmq_calendar_exchange: str = "calendar_exchange"
    rabbitmq_bet_exchange: str = "bet_exchange"
    rabbitmq_calendar_queue: str = "calendar_queue"

    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = False
        extra = "ignore"  # <-- ignore les variables inconnues


@lru_cache()
def get_settings() -> Settings:
    return Settings()
