"""
Обработчик команды /start
Современный дизайн с анимацией загрузки и единым стилем
"""

import asyncio
import logging
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

logger = logging.getLogger(__name__)


async def start_command(message: Message, **kwargs):
    """
    Обработчик команды /start - современная версия 2025-2026
    
    Особенности:
    - Красивая анимация загрузки для новых пользователей
    - Единый стиль с главным меню
    - Централизованные тексты
    - Плавные переходы и эффекты
    
    Args:
        message: Сообщение от пользователя
        **kwargs: Дополнительные данные, включая services из middleware
    """
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Пользователь"
    username = message.from_user.username
    
    logger.info(f"👋 Пользователь: ID={user_id}, Username=@{username}, Name={first_name}")
    
    # Получаем сервисы из middleware
    services = kwargs.get("services")
    if not services:
        logger.error("❌ Сервисы не найдены в middleware")
        await message.reply("❌ Ошибка инициализации. Попробуйте позже.")
        return
    
    try:
        user_service = services.get_user_service()
        animation_service = services.get_animation_service()
        
        # Проверяем, является ли пользователь новым
        existing_user = await user_service.get_user(user_id)
        is_new_user = existing_user is None
        
        if is_new_user:
            logger.info(f"🎉 Новый пользователь: {first_name} (ID: {user_id})")
            
            # 🎬 Показываем современную анимацию загрузки
            await animation_service.show_loading_animation(message)
            
            # Создаем пользователя (с автоматическим бонусом 15₽)
            user = await user_service.create_or_update_user(
                user_id=user_id,
                username=username,
                first_name=first_name
            )
            
            # Отправляем приветствие для нового пользователя
            await animation_service.send_welcome_message(
                message, 
                first_name, 
                balance=15.0, 
                subscription_days=3,
                is_new=True
            )
            
            logger.info(f"✅ Пользователь {first_name} зарегистрирован с бонусом 15₽")
        else:
            logger.info(f"👋 Возвращение пользователя: {first_name} (ID: {user_id})")
            
            # Обновляем данные существующего пользователя
            user = await user_service.create_or_update_user(
                user_id=user_id,
                username=username,
                first_name=first_name
            )
            
            # Получаем актуальную статистику
            stats = await user_service.get_user_stats(user_id)
            balance = stats.get('balance', 0.0)
            subscription_days = stats.get('subscription_days', 0)
            
            # Отправляем приветствие для существующего пользователя
            await animation_service.send_welcome_message(
                message, 
                first_name, 
                balance=balance, 
                subscription_days=subscription_days,
                is_new=False
            )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в команде /start: {e}")
        await message.reply(
            f"❌ Произошла ошибка при регистрации. "
            f"Попробуйте позже или обратитесь в поддержку."
        )


def register_start_handler(dp: Dispatcher):
    """
    Регистрация обработчика команды /start
    
    Args:
        dp: Диспетчер бота
    """
    dp.message.register(start_command, CommandStart())
    logger.info("✅ Обработчик команды /start зарегистрирован")
