"""
Сервис кэширования
Управление кэшем для оптимизации запросов к БД и API
"""

import logging
import time
from typing import Optional, Any, Dict, Callable
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

class CacheService:
    """
    Сервис для кэширования данных
    
    Отвечает за:
    - Кэширование результатов запросов
    - Инвалидация устаревших данных
    - Оптимизацию повторяющихся запросов
    - Уменьшение нагрузки на БД и API
    """
    
    def __init__(self, default_ttl: int = 300):
        """
        Инициализация сервиса кэширования
        
        Args:
            default_ttl: Время жизни кэша по умолчанию (в секундах)
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
        logger.info(f"✅ CacheService инициализирован (TTL: {default_ttl}s)")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Генерировать ключ кэша
        
        Args:
            prefix: Префикс ключа
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
        
        Returns:
            str: Уникальный ключ кэша
        """
        args_str = '_'.join(str(arg) for arg in args)
        kwargs_str = '_'.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        
        parts = [prefix]
        if args_str:
            parts.append(args_str)
        if kwargs_str:
            parts.append(kwargs_str)
        
        return ':'.join(parts)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша
        
        Args:
            key: Ключ кэша
        
        Returns:
            Optional[Any]: Значение из кэша или None
        """
        if key not in self._cache:
            self._stats['misses'] += 1
            return None
        
        entry = self._cache[key]
        
        # Проверяем срок действия
        if entry['expires_at'] < time.time():
            # Удаляем устаревшую запись
            del self._cache[key]
            self._stats['misses'] += 1
            logger.debug(f"🗑️ Кэш устарел: {key}")
            return None
        
        self._stats['hits'] += 1
        logger.debug(f"✅ Попадание в кэш: {key}")
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Установить значение в кэш
        
        Args:
            key: Ключ кэша
            value: Значение для кэширования
            ttl: Время жизни (в секундах), если None - используется default_ttl
        """
        if ttl is None:
            ttl = self.default_ttl
        
        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        
        self._stats['sets'] += 1
        logger.debug(f"💾 Сохранено в кэш: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str):
        """
        Удалить значение из кэша
        
        Args:
            key: Ключ кэша
        """
        if key in self._cache:
            del self._cache[key]
            self._stats['deletes'] += 1
            logger.debug(f"🗑️ Удалено из кэша: {key}")
    
    def delete_pattern(self, pattern: str):
        """
        Удалить все ключи, соответствующие паттерну
        
        Args:
            pattern: Паттерн для поиска ключей
        """
        keys_to_delete = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_delete:
            del self._cache[key]
            self._stats['deletes'] += 1
        
        if keys_to_delete:
            logger.info(f"🗑️ Удалено {len(keys_to_delete)} записей по паттерну: {pattern}")
    
    def clear(self):
        """
        Очистить весь кэш
        """
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"🗑️ Кэш полностью очищен ({count} записей)")
    
    def cleanup_expired(self):
        """
        Удалить все устаревшие записи
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry['expires_at'] < current_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"🧹 Удалено {len(expired_keys)} устаревших записей")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику кэша
        
        Returns:
            Dict: Статистика кэша
        """
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'sets': self._stats['sets'],
            'deletes': self._stats['deletes'],
            'hit_rate': round(hit_rate, 2),
            'total_entries': len(self._cache),
            'total_requests': total_requests
        }
    
    def cached(self, key_prefix: str, ttl: Optional[int] = None):
        """
        Декоратор для кэширования результатов функций
        
        Args:
            key_prefix: Префикс ключа кэша
            ttl: Время жизни кэша
        
        Returns:
            Decorator: Декоратор
        """
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Генерируем ключ
                cache_key = self._generate_key(key_prefix, *args, **kwargs)
                
                # Пытаемся получить из кэша
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Вызываем функцию
                result = await func(*args, **kwargs)
                
                # Сохраняем в кэш
                self.set(cache_key, result, ttl)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Генерируем ключ
                cache_key = self._generate_key(key_prefix, *args, **kwargs)
                
                # Пытаемся получить из кэша
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Вызываем функцию
                result = func(*args, **kwargs)
                
                # Сохраняем в кэш
                self.set(cache_key, result, ttl)
                
                return result
            
            # Определяем, асинхронная ли функция
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    async def start_cleanup_task(self, interval: int = 300):
        """
        Запустить фоновую задачу очистки устаревших данных
        
        Args:
            interval: Интервал очистки (в секундах)
        """
        logger.info(f"🔄 Запущена задача очистки кэша (интервал: {interval}s)")
        
        while True:
            await asyncio.sleep(interval)
            self.cleanup_expired()


# Глобальный экземпляр кэша
_cache_instance = None

def get_cache() -> CacheService:
    """
    Получить глобальный экземпляр кэша
    
    Returns:
        CacheService: Экземпляр сервиса кэширования
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance
