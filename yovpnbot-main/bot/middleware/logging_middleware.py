"""
Middleware для логирования
Логирование всех запросов и ответов
"""

import logging
import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для логирования запросов
    
    Логирует все входящие сообщения и callback запросы
    """
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
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
        # Засекаем время начала обработки
        start_time = time.time()
        
        # Получаем информацию о пользователе
        user_id = event.from_user.id
        username = event.from_user.username
        first_name = event.from_user.first_name or "Пользователь"
        
        # Логируем входящее событие
        if isinstance(event, Message):
            logger.info(
                f"📨 Сообщение от {first_name} (@{username}): {event.text[:50]}..."
                if event.text else f"📨 Сообщение от {first_name} (@{username}): [медиа]"
            )
        elif isinstance(event, CallbackQuery):
            logger.info(
                f"🔘 Callback от {first_name} (@{username}): {event.data}"
            )
        
        try:
            # Вызываем следующий обработчик
            result = await handler(event, data)
            
            # Вычисляем время обработки
            processing_time = time.time() - start_time
            
            # Логируем успешную обработку
            logger.info(
                f"✅ Обработано за {processing_time:.3f}s: {first_name} (@{username})"
            )
            
            return result
            
        except Exception as e:
            # Вычисляем время до ошибки
            processing_time = time.time() - start_time
            
            # Логируем ошибку
            logger.error(
                f"❌ Ошибка за {processing_time:.3f}s: {first_name} (@{username}): {e}"
            )
            
            # Пробрасываем ошибку дальше
            raise