"""
Middleware для rate limiting
Ограничение частоты запросов пользователей
"""

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты запросов
    
    Использует SecurityService для проверки rate limits
    """
    
    def __init__(self):
        """Инициализация middleware"""
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка middleware
        
        Args:
            handler: Обработчик события
            event: Событие (Message или CallbackQuery)
            data: Данные события
        
        Returns:
            Any: Результат обработки
        """
        user_id = event.from_user.id
        
        # Получаем сервисы из данных
        services = data.get("services")
        
        if not services:
            logger.warning("⚠️ Сервисы не найдены в middleware")
            return await handler(event, data)
        
        # Получаем SecurityService
        security_service = services.get_security_service()
        
        # Проверяем rate limit
        allowed, error_message = security_service.check_rate_limit(user_id)
        
        if not allowed:
            # Отправляем сообщение об ошибке
            if isinstance(event, Message):
                await event.reply(error_message)
            elif isinstance(event, CallbackQuery):
                await event.answer(error_message, show_alert=True)
            
            logger.warning(f"🚫 Rate limit для пользователя {user_id}: {error_message}")
            return
        
        # Продолжаем обработку
        return await handler(event, data)
