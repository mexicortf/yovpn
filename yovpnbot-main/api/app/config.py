from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    app_name: str = "YoVPN WebApp API"
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    api_reload: bool = False
    
    # Telegram
    telegram_bot_token: str
    
    # Security
    secret_key: str
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_pool_max_connections: int = 50
    redis_pool_timeout: int = 20
    
    # Marzban
    marzban_api_url: str
    marzban_username: str = ""
    marzban_password: str = ""
    marzban_admin_token: str = ""  # Alternative to username/password
    marzban_connection_pool_size: int = 10
    marzban_timeout: int = 30
    
    # Cache settings
    cache_ttl_subscription: int = 300  # 5 minutes
    cache_ttl_user: int = 600  # 10 minutes
    cache_ttl_marzban_token: int = 3600  # 1 hour
    
    # Download URLs
    android_apk_url: str
    ios_app_store_url: str
    macos_dmg_url: str
    windows_exe_url: str
    android_tv_apk_url: str
    
    # Performance settings
    max_concurrent_requests: int = 100
    request_timeout: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
