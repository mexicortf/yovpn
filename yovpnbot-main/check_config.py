#!/usr/bin/env python3
"""
YoVPN Bot - Проверка конфигурации
Скрипт для проверки и валидации настроек бота
"""

import sys
import os
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

def check_environment():
    """Проверить переменные окружения"""
    print("🔍 Проверка переменных окружения...")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',  # или USERBOT_TOKEN для обратной совместимости
        'MARZBAN_API_URL',
        'MARZBAN_ADMIN_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные: {', '.join(missing_vars)}")
        return False
    
    print("✅ Все переменные окружения установлены")
    return True

def check_config_file():
    """Проверить файл конфигурации"""
    print("📄 Проверка файла конфигурации...")
    
    config_file = Path('.env')
    if not config_file.exists():
        print("❌ Файл .env не найден!")
        print("📝 Скопируйте .env.sample в .env и заполните настройки")
        return False
    
    print("✅ Файл .env найден")
    return True

def check_dependencies():
    """Проверить зависимости"""
    print("📦 Проверка зависимостей...")
    
    try:
        import aiogram
        import aiohttp
        import redis
        print("✅ Основные зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("📦 Установите зависимости: pip install -r requirements.txt")
        return False

def check_marzban_connection():
    """Проверить подключение к Marzban"""
    print("🌐 Проверка подключения к Marzban...")
    
    try:
        from src.config import config
        from bot.services.marzban_service import MarzbanService
        
        marzban_service = MarzbanService(config.MARZBAN_API_URL, config.MARZBAN_ADMIN_TOKEN)
        
        # Проверяем доступность API
        import asyncio
        result = asyncio.run(marzban_service.check_api_availability())
        
        if result:
            print("✅ Marzban API доступен")
            return True
        else:
            print("❌ Marzban API недоступен")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки Marzban: {e}")
        return False

def check_telegram_connection():
    """Проверить подключение к Telegram"""
    print("🤖 Проверка подключения к Telegram...")
    
    try:
        from src.config import config
        import requests
        
        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Бот подключен: @{bot_info.get('username', 'unknown')}")
                return True
            else:
                print(f"❌ Ошибка Telegram API: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к Telegram: {e}")
        return False

def main():
    """Главная функция проверки"""
    print("🔧 YoVPN Bot - Проверка конфигурации")
    print("=" * 50)
    
    checks = [
        ("Переменные окружения", check_environment),
        ("Файл конфигурации", check_config_file),
        ("Зависимости", check_dependencies),
        ("Подключение к Telegram", check_telegram_connection),
        ("Подключение к Marzban", check_marzban_connection)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    
    for i, (name, _) in enumerate(checks):
        status = "✅" if results[i] else "❌"
        print(f"   {name}: {status}")
    
    all_passed = all(results)
    
    if all_passed:
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОШЛИ!")
        print("🚀 Бот готов к запуску: python run.py")
        return 0
    else:
        print("\n⚠️ ЕСТЬ ПРОБЛЕМЫ С КОНФИГУРАЦИЕЙ")
        print("🔧 Исправьте ошибки и запустите проверку снова")
        return 1

if __name__ == "__main__":
    sys.exit(main())