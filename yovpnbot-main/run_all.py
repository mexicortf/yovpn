#!/usr/bin/env python3
"""
YoVPN Bot - Мастер-скрипт запуска
Единая точка входа для запуска всех компонентов бота

Этот скрипт:
- Проверяет конфигурацию
- Запускает основной бот
- Обрабатывает ошибки
- Логирует выполнение
"""

import sys
import os
import logging
import asyncio
import signal
from pathlib import Path
from typing import Optional

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "0") == "1"
LOG_FILE = os.getenv("LOG_FILE", "/tmp/bot.log")

logger = logging.getLogger("yovpn.bot")
logger.setLevel(LOG_LEVEL)
logger.handlers.clear()

formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

if LOG_TO_FILE:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
else:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

class YoVPNBotManager:
    """
    Менеджер для управления всеми компонентами бота
    """
    
    def __init__(self):
        """Инициализация менеджера"""
        self.bot_process = None
        self.running = False
        
    def check_environment(self) -> bool:
        """
        Проверка окружения и конфигурации
        
        Returns:
            bool: True если все проверки пройдены
        """
        logger.info("🔍 Проверка окружения...")
        
        try:
            # Проверяем Python версию
            if sys.version_info < (3, 8):
                logger.error("❌ Требуется Python 3.8 или выше")
                return False
            
            logger.info(f"✅ Python версия: {sys.version}")
            
            # Проверяем наличие .env файла
            env_file = Path('.env')
            if not env_file.exists():
                logger.warning("⚠️ Файл .env не найден. Создайте его на основе .env.sample")
                return False
            
            logger.info("✅ Файл .env найден")
            
            # Проверяем конфигурацию
            from src.config import config
            
            if not config.validate_config():
                logger.error("❌ Ошибка конфигурации!")
                logger.error("📝 Проверьте переменные окружения в файле .env")
                return False
            
            logger.info("✅ Конфигурация проверена")
            
            # Проверяем зависимости
            try:
                import aiogram
                import decouple
                logger.info("✅ Основные зависимости найдены")
            except ImportError as e:
                logger.error(f"❌ Отсутствует зависимость: {e}")
                logger.error("📦 Установите зависимости: pip install -r requirements.txt")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки окружения: {e}")
            return False
    
    def check_marzban_connection(self) -> bool:
        """
        Проверка подключения к Marzban API
        
        Returns:
            bool: True если подключение успешно
        """
        logger.info("🔗 Проверка подключения к Marzban API...")
        
        try:
            from src.services.marzban_service import MarzbanService
            
            marzban_service = MarzbanService()
            
            if marzban_service.health_check():
                logger.info("✅ Marzban API доступен")
                return True
            else:
                logger.warning("⚠️ Marzban API недоступен, но бот продолжит работу")
                return True  # Бот может работать без Marzban
                
        except Exception as e:
            logger.warning(f"⚠️ Ошибка проверки Marzban API: {e}")
            logger.warning("⚠️ Бот продолжит работу в автономном режиме")
            return True
    
    async def start_bot(self) -> bool:
        """
        Запуск основного бота
        
        Returns:
            bool: True если бот успешно запущен
        """
        logger.info("🚀 Запуск YoVPN Bot...")
        
        try:
            from bot.main import main as bot_main
            
            # Запускаем бота
            await bot_main()
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал остановки")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {e}")
            return False
    
    def setup_signal_handlers(self):
        """Настройка обработчиков сигналов для корректного завершения"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Получен сигнал {signum}, завершение работы...")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self) -> int:
        """
        Главная функция запуска
        
        Returns:
            int: Код возврата (0 - успех, 1 - ошибка)
        """
        logger.info("=" * 60)
        logger.info("🤖 YoVPN Bot - Мастер-скрипт запуска")
        logger.info("=" * 60)
        
        # Настраиваем обработчики сигналов
        self.setup_signal_handlers()
        
        try:
            # Проверяем окружение
            if not self.check_environment():
                logger.error("❌ Проверка окружения не пройдена")
                return 1
            
            # Проверяем подключение к Marzban
            self.check_marzban_connection()
            
            # Запускаем бота
            self.running = True
            success = await self.start_bot()
            
            if success:
                logger.info("✅ Бот успешно завершил работу")
                return 0
            else:
                logger.error("❌ Бот завершился с ошибкой")
                return 1
                
        except Exception as e:
            logger.error(f"💥 Критическая ошибка: {e}")
            return 1
        finally:
            logger.info("👋 До свидания!")

def print_usage():
    """Вывод справки по использованию"""
    print("""
🤖 YoVPN Bot - Мастер-скрипт запуска

Использование:
    python3 run_all.py          # Запуск бота
    python3 run_all.py --help   # Показать эту справку

Описание:
    Этот скрипт автоматически:
    - Проверяет конфигурацию
    - Проверяет подключение к Marzban API
    - Запускает основной бот
    - Обрабатывает ошибки и логирует выполнение

Требования:
    - Python 3.8+
    - Файл .env с настройками
    - Установленные зависимости (requirements.txt)

Для остановки нажмите Ctrl+C
""")

def main():
    """Главная функция"""
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print_usage()
        return 0
    
    # Создаем менеджер и запускаем
    manager = YoVPNBotManager()
    
    try:
        # Запускаем асинхронную функцию
        return asyncio.run(manager.run())
    except KeyboardInterrupt:
        logger.info("👋 До свидания!")
        return 0
    except Exception as e:
        logger.error(f"💥 Фатальная ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
