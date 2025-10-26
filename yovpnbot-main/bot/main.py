#!/usr/bin/env python3
"""
YoVPN Telegram Bot - Главный файл
Современный бот для продажи VPN-подписок с ежедневной оплатой

Особенности:
- Анимированные эффекты сообщений
- Современный UX/UI дизайн
- Ежедневная модель оплаты (4 рубля в день)
- Полная безопасность и валидация
- Асинхронная архитектура
"""

import asyncio
import logging
import sys
import os
import fcntl
import time
import random
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramConflictError

# Импорты конфигурации и сервисов
from src.config import config
from bot.handlers import register_handlers, init_admin_panel
from bot.middleware import register_middleware
from bot.services import BotServices

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

# Файл блокировки для предотвращения запуска нескольких экземпляров
LOCK_FILE = "/tmp/yovpn_bot.lock"
lock_file_handle = None

def acquire_lock():
    """Получить эксклюзивную блокировку для предотвращения запуска нескольких экземпляров"""
    global lock_file_handle
    try:
        lock_file_handle = open(LOCK_FILE, 'w')
        fcntl.flock(lock_file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_file_handle.write(str(os.getpid()))
        lock_file_handle.flush()
        logger.info(f"✅ Блокировка получена (PID: {os.getpid()})")
        return True
    except IOError:
        logger.error("❌ Другой экземпляр бота уже запущен!")
        logger.error("⚠️ Убедитесь, что запущен только один экземпляр бота с этим токеном.")
        return False

def release_lock():
    """Освободить блокировку"""
    global lock_file_handle
    if lock_file_handle:
        try:
            fcntl.flock(lock_file_handle, fcntl.LOCK_UN)
            lock_file_handle.close()
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
            logger.info("✅ Блокировка освобождена")
        except Exception as e:
            logger.error(f"❌ Ошибка при освобождении блокировки: {e}")

class YoVPNBot:
    """
    Главный класс бота YoVPN
    
    Отвечает за:
    - Инициализацию бота и диспетчера
    - Регистрацию обработчиков и middleware
    - Запуск и остановку бота
    - Управление сервисами
    """
    
    def __init__(self):
        """Инициализация бота"""
        self.bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Создаем сервисы ОДИН РАЗ
        self.services = BotServices(self.bot)
        
        # Регистрируем middleware с готовыми сервисами
        register_middleware(self.dp, self.services)
        
        # Регистрируем обработчики
        register_handlers(self.dp)
        
        # Инициализируем админ панель с ВСЕМИ сервисами
        init_admin_panel(
            self.services.user_service,
            self.services.marzban_service,
            self.services.ui_service,
            self.services.animation_service  # ИСПРАВЛЕНО: добавлен animation_service
        )
        
        logger.info("YoVPN Bot инициализирован")
    
    async def start(self):
        """Запуск бота с автоматическим восстановлением при конфликтах"""
        max_retries = 10
        base_delay = 5.0  # Базовая задержка в секундах
        max_delay = 60.0  # Максимальная задержка в секундах
        
        for attempt in range(max_retries):
            try:
                logger.info("🚀 Запуск YoVPN Bot...")
                
                # Запускаем фоновые задачи
                await self.services.start_background_tasks()
                
                # Запускаем бота
                await self.dp.start_polling(
                    self.bot,
                    allowed_updates=["message", "callback_query"]
                )
                
                # Если polling завершился без ошибок, выходим
                break
                
            except TelegramConflictError as e:
                # Вычисляем задержку с экспоненциальным отступом и джиттером
                delay = min(base_delay * (2 ** attempt), max_delay)
                jitter = random.uniform(0, delay * 0.3)  # Добавляем случайность ±30%
                total_delay = delay + jitter
                
                bot_info = await self.bot.get_me()
                logger.warning(
                    f"⚠️ TelegramConflictError: {e}\n"
                    f"💡 Обнаружен конфликт с другим экземпляром бота (ID: {bot_info.id})\n"
                    f"🔄 Попытка {attempt + 1}/{max_retries}\n"
                    f"⏳ Ожидание {total_delay:.2f} секунд перед повторной попыткой...\n"
                    f"\n📋 Возможные причины конфликта:\n"
                    f"   1. Другой экземпляр бота запущен на этом или другом сервере\n"
                    f"   2. Бот запущен в нескольких Docker контейнерах\n"
                    f"   3. Предыдущий экземпляр не был корректно остановлен\n"
                    f"\n🔧 Рекомендации:\n"
                    f"   - Проверьте: docker ps | grep bot\n"
                    f"   - Проверьте: ps aux | grep 'bot/main.py'\n"
                    f"   - Убедитесь, что бот не запущен на других серверах\n"
                )
                
                if attempt < max_retries - 1:
                    # Останавливаем фоновые задачи перед повторной попыткой
                    await self.services.stop_background_tasks()
                    
                    # Ждем перед повторной попыткой
                    await asyncio.sleep(total_delay)
                else:
                    logger.error(
                        f"❌ Превышено максимальное количество попыток ({max_retries})\n"
                        f"🚫 Не удалось устранить конфликт с другим экземпляром бота\n"
                        f"💡 Необходимо вручную остановить все запущенные экземпляры"
                    )
                    raise
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при запуске бота: {e}")
                raise
    
    async def stop(self):
        """Остановка бота"""
        try:
            logger.info("🛑 Остановка YoVPN Bot...")
            
            # Останавливаем фоновые задачи
            await self.services.stop_background_tasks()
            
            # Закрываем сессию бота
            await self.bot.session.close()
            
            logger.info("✅ Бот успешно остановлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при остановке бота: {e}")

async def main():
    """Главная функция"""
    # Проверяем, не запущен ли уже другой экземпляр
    if not acquire_lock():
        logger.error("🚫 Запуск отменен: обнаружен конфликт с другим экземпляром бота")
        logger.error("💡 Решение проблемы:")
        logger.error("   1. Остановите все запущенные экземпляры бота")
        logger.error("   2. Проверьте Docker контейнеры: docker ps | grep bot")
        logger.error("   3. Проверьте процессы: ps aux | grep 'bot/main.py'")
        logger.error("   4. Убедитесь, что бот не запущен на другом сервере с тем же токеном")
        sys.exit(1)
    
    bot = YoVPNBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await bot.stop()
        release_lock()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 До свидания!")
        release_lock()
    except Exception as e:
        logger.error(f"💥 Фатальная ошибка: {e}")
        release_lock()
        sys.exit(1)
