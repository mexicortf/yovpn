#!/usr/bin/env python3
"""
Скрипт для проверки и настройки YoVPN Bot
Проверяет наличие всех необходимых переменных окружения
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

class Colors:
    """ANSI цвета для вывода"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Красивый заголовок"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_success(text):
    """Сообщение об успехе"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    """Сообщение об ошибке"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    """Предупреждение"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    """Информация"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_env_file():
    """Проверка наличия .env файла"""
    env_path = Path('.env')
    if not env_path.exists():
        print_error("Файл .env не найден!")
        print_info("Создайте .env файл на основе .env.example:")
        print(f"   {Colors.BOLD}cp .env.example .env{Colors.END}")
        return False
    print_success("Файл .env найден")
    return True

def check_bot_token():
    """Проверка токена бота"""
    token = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('BOT_TOKEN') or os.getenv('USERBOT_TOKEN')
    
    if not token:
        print_error("Токен Telegram бота не найден!")
        print_info("Получите токен у @BotFather:")
        print("   1. Откройте Telegram и найдите @BotFather")
        print("   2. Отправьте /newbot")
        print("   3. Следуйте инструкциям")
        print("   4. Скопируйте токен в .env")
        print(f"\n   {Colors.BOLD}TELEGRAM_BOT_TOKEN=ваш_токен{Colors.END}\n")
        return False
    
    if token in ['YOUR_BOT_TOKEN_HERE', 'your_bot_token_here']:
        print_error("Токен бота не настроен (используется значение по умолчанию)")
        print_info("Замените YOUR_BOT_TOKEN_HERE на реальный токен")
        return False
    
    # Проверка формата токена
    if ':' not in token or len(token) < 20:
        print_error(f"Неверный формат токена: {token[:20]}...")
        print_info("Токен должен иметь формат: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        return False
    
    print_success(f"Токен бота найден: {token[:10]}...{token[-5:]}")
    return True

def check_marzban_url():
    """Проверка URL Marzban"""
    url = os.getenv('MARZBAN_API_URL')
    
    if not url:
        print_error("URL Marzban API не найден!")
        print_info("Укажите URL вашей панели Marzban в .env:")
        print(f"   {Colors.BOLD}MARZBAN_API_URL=http://localhost:8000{Colors.END}")
        return False
    
    if url in ['http://localhost:8000', 'https://your-domain.com']:
        print_warning(f"Используется URL по умолчанию: {url}")
        print_info("Убедитесь, что это правильный адрес вашей панели Marzban")
    
    print_success(f"URL Marzban: {url}")
    return True

def check_marzban_token():
    """Проверка токена Marzban"""
    token = os.getenv('MARZBAN_ADMIN_TOKEN')
    
    if not token:
        print_error("Токен Marzban не найден!")
        print_info("Получите токен в панели Marzban:")
        print("   1. Откройте панель Marzban")
        print("   2. Перейдите в Settings → API")
        print("   3. Создайте или скопируйте токен")
        print("   4. Добавьте в .env:")
        print(f"   {Colors.BOLD}MARZBAN_ADMIN_TOKEN=ваш_токен{Colors.END}\n")
        return False
    
    if token in ['YOUR_MARZBAN_TOKEN_HERE', 'your_marzban_token_here']:
        print_error("Токен Marzban не настроен (используется значение по умолчанию)")
        print_info("Замените YOUR_MARZBAN_TOKEN_HERE на реальный токен")
        return False
    
    # Проверка формата JWT токена
    if not token.startswith('eyJ'):
        print_warning(f"Формат токена не похож на JWT: {token[:20]}...")
        print_info("Убедитесь, что это правильный токен из панели Marzban")
    
    print_success(f"Токен Marzban найден: {token[:20]}...{token[-10:]}")
    return True

def check_database():
    """Проверка настроек базы данных"""
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print_warning("DATABASE_URL не найден, будет использован SQLite")
        return True
    
    print_success(f"База данных: {db_url.split('@')[-1] if '@' in db_url else 'SQLite'}")
    return True

def main():
    """Главная функция проверки"""
    print_header("YoVPN Bot - Проверка конфигурации")
    
    checks = {
        "Файл .env": check_env_file(),
        "Токен Telegram бота": check_bot_token(),
        "URL Marzban API": check_marzban_url(),
        "Токен Marzban": check_marzban_token(),
        "База данных": check_database()
    }
    
    # Итоговый результат
    print_header("Результат проверки")
    
    passed = sum(checks.values())
    total = len(checks)
    
    if passed == total:
        print_success(f"Все проверки пройдены ({passed}/{total})")
        print_info("Можно запускать бота:")
        print(f"   {Colors.BOLD}python3 bot/main.py{Colors.END}\n")
        return 0
    else:
        print_error(f"Не пройдено проверок: {total - passed}/{total}")
        print_info("Исправьте ошибки и запустите проверку снова:")
        print(f"   {Colors.BOLD}python3 setup_check.py{Colors.END}")
        print_info("Подробная инструкция:")
        print(f"   {Colors.BOLD}cat SETUP_TOKENS.md{Colors.END}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Проверка прервана{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Ошибка: {e}")
        sys.exit(1)
