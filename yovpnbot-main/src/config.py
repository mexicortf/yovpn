#!/usr/bin/env python3
"""
Конфигурация бота YOVPN
"""

import os
from decouple import config
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    """Класс конфигурации бота"""
    
    def __init__(self):
        # Telegram Bot Configuration
        # Поддерживаем оба варианта названия для обратной совместимости
        self.BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or os.environ.get('USERBOT_TOKEN') or config('TELEGRAM_BOT_TOKEN', default=config('USERBOT_TOKEN', default=None))
        
        # Marzban API Configuration
        self.MARZBAN_API_URL = os.environ.get('MARZBAN_API_URL') or config('MARZBAN_API_URL', default=None)
        self.MARZBAN_ADMIN_TOKEN = os.environ.get('MARZBAN_ADMIN_TOKEN') or config('MARZBAN_ADMIN_TOKEN', default=None)
        
        # Database Configuration
        self.DB_HOST = config('DB_HOST', default='localhost')
        self.DB_PORT = config('DB_PORT', default=3306, cast=int)
        self.DB_NAME = config('DB_NAME', default='marzban')
        self.DB_USER = config('DB_USER', default='marzban')
        self.DB_PASSWORD = config('DB_PASSWORD', default=None)
        
        # Data file path
        self.DATA_FILE = config('DATA_FILE', default='data.json')
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Проверка обязательных переменных окружения"""
        required_vars = {
            'BOT_TOKEN': self.BOT_TOKEN,
            'MARZBAN_API_URL': self.MARZBAN_API_URL,
            'MARZBAN_ADMIN_TOKEN': self.MARZBAN_ADMIN_TOKEN,
            'DB_PASSWORD': self.DB_PASSWORD
        }
        
        missing_vars = [var for var, value in required_vars.items() if value is None]
        
        if missing_vars:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")

# Создаем глобальный экземпляр конфигурации
config = Config()