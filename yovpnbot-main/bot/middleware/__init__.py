"""
Middleware для бота
Промежуточное ПО для обработки запросов
"""

from .services_middleware import ServicesMiddleware
from .logging_middleware import LoggingMiddleware
from .rate_limit_middleware import RateLimitMiddleware

def register_middleware(dp, services):
    """
    Регистрация всех middleware
    
    Args:
        dp: Диспетчер бота
        services: Объект BotServices (создается ОДИН РАЗ в main.py)
    """
    # Добавляем middleware для сервисов с готовыми сервисами
    # ВАЖНО: Передаем готовые сервисы, чтобы избежать повторной инициализации
    services_middleware = ServicesMiddleware(services)
    dp.message.middleware(services_middleware)
    dp.callback_query.middleware(services_middleware)
    
    # Добавляем middleware для rate limiting (ПОСЛЕ сервисов)
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
    
    # Добавляем middleware для логирования
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())