"""
Configuration Settings
Настройки приложения из переменных окружения
"""

import os
from typing import List
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class Settings:
    """Настройки приложения"""
    
    # === TELEGRAM BOT ===
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_TG_ID: int = int(os.getenv("ADMIN_TG_ID", "7610842643"))
    
    # === DATABASE ===
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+aiomysql://root:password@localhost:3306/yovpn"
    )
    
    # === MARZBAN API ===
    MARZBAN_API_URL: str = os.getenv("MARZBAN_API_URL", "http://localhost:8000")
    MARZBAN_API_TOKEN: str = os.getenv(
        "MARZBAN_API_TOKEN",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzZHE4QWRieXJiSm1GOGVoIiwiYWNjZXNzIjoic3VkbyIsImlhdCI6MTc2MTMyNDMxNCwiZXhwIjoxNzYxNDEwNzE0fQ.vXhALPxAscjum9_6EIK98-V8xY-YKy7CH6BCWeR5Fv4"
    )
    
    # === ADMIN PANEL ===
    ADMIN_HOST: str = os.getenv("ADMIN_HOST", "0.0.0.0")
    ADMIN_PORT: int = int(os.getenv("ADMIN_PORT", "8080"))
    
    # === WEBAPP ===
    WEBAPP_URL: str = os.getenv("WEBAPP_URL", "http://localhost:3000")
    
    # === REDIS (CACHE) ===
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # === APP SETTINGS ===
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # === PAYMENT SETTINGS ===
    DAILY_PRICE: float = float(os.getenv("DAILY_PRICE", "4.0"))
    WELCOME_BONUS: float = float(os.getenv("WELCOME_BONUS", "12.0"))
    REFERRAL_BONUS: float = float(os.getenv("REFERRAL_BONUS", "8.0"))
    MIN_DEPOSIT: float = float(os.getenv("MIN_DEPOSIT", "40.0"))
    
    # === SUPPORT ===
    SUPPORT_USERNAME: str = os.getenv("SUPPORT_USERNAME", "@YoVPNSupport")
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "@YoVPN")
    
    def validate(self) -> bool:
        """Валидация настроек"""
        errors = []
        
        if not self.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL is required")
        
        if not self.MARZBAN_API_URL:
            errors.append("MARZBAN_API_URL is required")
        
        if not self.MARZBAN_API_TOKEN:
            errors.append("MARZBAN_API_TOKEN is required")
        
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True


# Создаем экземпляр настроек
settings = Settings()


def check_config():
    """Проверка конфигурации"""
    print("🔧 Checking configuration...")
    
    if settings.validate():
        print("✅ Configuration is valid")
        print(f"📡 Bot Token: {settings.BOT_TOKEN[:10]}...")
        print(f"🗄️ Database: {settings.DATABASE_URL.split('@')[-1]}")
        print(f"🌐 Marzban API: {settings.MARZBAN_API_URL}")
        print(f"⚙️ Admin Panel: {settings.ADMIN_HOST}:{settings.ADMIN_PORT}")
        return True
    else:
        print("❌ Configuration is invalid")
        return False


if __name__ == "__main__":
    check_config()
