#!/usr/bin/env python3
"""
YoVPN Bot - Запуск бота
Простой скрипт для запуска бота с проверкой конфигурации
"""

import sys
import os
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Главная функция запуска"""
    print("🚀 Запуск YoVPN Bot v2.0")
    print("=" * 50)
    
    try:
        # Проверяем конфигурацию
        from src.config import config
        
        if not config.validate_config():
            print("❌ Ошибка конфигурации!")
            print("📝 Проверьте файл .env и заполните все обязательные поля")
            print("📋 Пример конфигурации: .env.sample")
            return 1
        
        print("✅ Конфигурация проверена")
        
        # Запускаем бота
        from bot.main import main as bot_main
        import asyncio
        
        print("🤖 Запуск бота...")
        asyncio.run(bot_main())
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки")
        print("👋 До свидания!")
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())