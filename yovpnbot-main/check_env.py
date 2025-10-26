#!/usr/bin/env python3
"""
Скрипт для проверки переменных окружения
"""

import os
import sys

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import config

print("=" * 60)
print("ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
print("=" * 60)

print("1. Переменные окружения системы:")
print(f"   MARZBAN_API_URL: {os.getenv('MARZBAN_API_URL', 'НЕ УСТАНОВЛЕНА')}")
print(f"   MARZBAN_ADMIN_TOKEN: {os.getenv('MARZBAN_ADMIN_TOKEN', 'НЕ УСТАНОВЛЕНА')[:20]}..." if os.getenv('MARZBAN_ADMIN_TOKEN') else "   MARZBAN_ADMIN_TOKEN: НЕ УСТАНОВЛЕНА")
bot_token = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('USERBOT_TOKEN')
print(f"   TELEGRAM_BOT_TOKEN: {bot_token[:20] if bot_token else 'НЕ УСТАНОВЛЕНА'}..." if bot_token else "   TELEGRAM_BOT_TOKEN: НЕ УСТАНОВЛЕНА")

print("\n2. Значения из config.py:")
print(f"   MARZBAN_API_URL: {config.MARZBAN_API_URL}")
print(f"   MARZBAN_ADMIN_TOKEN: {config.MARZBAN_ADMIN_TOKEN[:20]}..." if config.MARZBAN_ADMIN_TOKEN else "   MARZBAN_ADMIN_TOKEN: НЕ УСТАНОВЛЕН")
print(f"   BOT_TOKEN: {config.BOT_TOKEN[:20]}..." if config.BOT_TOKEN else "   BOT_TOKEN: НЕ УСТАНОВЛЕН")

print("\n3. Файл .env:")
try:
    with open('.env', 'r') as f:
        content = f.read()
        print("   Содержимое .env файла:")
        for line in content.strip().split('\n'):
            if line.strip():
                key, value = line.split('=', 1)
                if 'TOKEN' in key or 'PASSWORD' in key:
                    print(f"   {key}={value[:20]}..." if len(value) > 20 else f"   {key}={value}")
                else:
                    print(f"   {key}={value}")
except FileNotFoundError:
    print("   .env файл не найден")
except Exception as e:
    print(f"   Ошибка чтения .env: {e}")

print("\n4. Рекомендации:")
if config.MARZBAN_API_URL == 'https://test.com/api':
    print("   ❌ Используется тестовый URL API")
    print("   🔧 Решение: Установите переменную MARZBAN_API_URL")
else:
    print("   ✅ Используется реальный URL API")

if config.MARZBAN_ADMIN_TOKEN == 'test_token':
    print("   ❌ Используется тестовый токен")
    print("   🔧 Решение: Установите переменную MARZBAN_ADMIN_TOKEN")
else:
    print("   ✅ Используется реальный токен")

print("\n" + "=" * 60)