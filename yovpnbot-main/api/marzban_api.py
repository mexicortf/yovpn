"""
Marzban API Client
Асинхронный клиент для работы с Marzban API
"""

import aiohttp
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import json

logger = logging.getLogger(__name__)


@dataclass
class SubscriptionData:
    """Данные подписки"""
    username: str
    status: str
    expire_date: Optional[datetime]
    data_limit: int
    used_traffic: int
    subscription_url: str
    links: List[str]


class MarzbanAPI:
    """
    Асинхронный клиент для работы с Marzban API
    
    Методы:
    - create_subscription: создать подписку
    - get_subscription: получить информацию о подписке
    - delete_subscription: удалить подписку
    - extend_subscription: продлить подписку
    - update_subscription: обновить подписку
    """
    
    def __init__(self, api_url: str, api_token: str, timeout: int = 30):
        """
        Инициализация клиента
        
        Args:
            api_url: URL Marzban API
            api_token: Токен для авторизации
            timeout: Таймаут запросов в секундах
        """
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Кэш для запросов
        self._cache: Dict[str, tuple[datetime, any]] = {}
        self._cache_ttl = 60  # Время жизни кэша в секундах
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать сессию"""
        if self._session is None or self._session.closed:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'YoVPN-Bot/1.0'
            }
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout
            )
        return self._session
    
    async def close(self):
        """Закрыть сессию"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _get_from_cache(self, key: str) -> Optional[any]:
        """Получить данные из кэша"""
        if key in self._cache:
            timestamp, data = self._cache[key]
            if (datetime.now() - timestamp).seconds < self._cache_ttl:
                return data
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: any):
        """Сохранить данные в кэш"""
        self._cache[key] = (datetime.now(), data)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        use_cache: bool = False
    ) -> Optional[Dict]:
        """
        Выполнить запрос к API
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Данные для отправки
            use_cache: Использовать кэширование
            
        Returns:
            Ответ API или None при ошибке
        """
        url = f"{self.api_url}{endpoint}"
        cache_key = f"{method}:{url}"
        
        # Проверяем кэш для GET запросов
        if method == 'GET' and use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                logger.debug(f"Возвращаем из кэша: {endpoint}")
                return cached_data
        
        try:
            session = await self._get_session()
            
            logger.debug(f"Выполняем запрос: {method} {url}")
            
            async with session.request(
                method,
                url,
                json=data if data else None
            ) as response:
                logger.debug(f"{method} {url} - Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Сохраняем в кэш для GET запросов
                    if method == 'GET' and use_cache:
                        self._set_cache(cache_key, result)
                    
                    return result
                
                elif response.status == 404:
                    logger.info(f"Ресурс не найден: {endpoint}")
                    return None
                
                elif response.status in [401, 403]:
                    logger.error(f"Ошибка авторизации: {response.status}")
                    error_text = await response.text()
                    logger.error(f"Ответ: {error_text}")
                    return None
                
                else:
                    error_text = await response.text()
                    logger.warning(f"Ошибка API {endpoint}: {response.status} - {error_text}")
                    return None
        
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка соединения с API: {e}")
            return None
        
        except asyncio.TimeoutError:
            logger.error(f"Таймаут запроса к {endpoint}")
            return None
        
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к {endpoint}: {e}")
            return None
    
    async def create_subscription(
        self,
        username: str,
        days: int = 30,
        data_limit: int = 0,
        proxies: Optional[Dict] = None
    ) -> Optional[SubscriptionData]:
        """
        Создать новую подписку
        
        Args:
            username: Username пользователя
            days: Количество дней
            data_limit: Лимит трафика в байтах (0 = безлимит)
            proxies: Настройки прокси
            
        Returns:
            SubscriptionData или None при ошибке
        """
        import uuid
        
        # Очищаем username
        clean_username = username.lstrip('@')
        
        # Вычисляем дату окончания
        expire_date = datetime.now() + timedelta(days=days)
        expire_timestamp = int(expire_date.timestamp())
        
        # Генерируем UUID
        user_uuid = str(uuid.uuid4())
        
        # Настройки прокси по умолчанию
        if proxies is None:
            proxies = {
                "vless": {
                    "id": user_uuid,
                    "flow": "xtls-rprx-vision"
                }
            }
        
        # Данные для создания
        user_data = {
            "username": clean_username,
            "expire": expire_timestamp,
            "data_limit": data_limit,
            "status": "active",
            "proxies": proxies
        }
        
        logger.info(f"Создаем подписку для {clean_username} на {days} дней")
        
        result = await self._make_request('POST', '/api/user', data=user_data)
        
        if result:
            return self._parse_subscription_data(result)
        
        return None
    
    async def get_subscription(self, username: str, use_cache: bool = True) -> Optional[SubscriptionData]:
        """
        Получить информацию о подписке
        
        Args:
            username: Username пользователя
            use_cache: Использовать кэширование
            
        Returns:
            SubscriptionData или None если не найдена
        """
        clean_username = username.lstrip('@')
        logger.info(f"Получаем информацию о подписке: {clean_username}")
        
        result = await self._make_request('GET', f'/api/user/{clean_username}', use_cache=use_cache)
        
        if result:
            return self._parse_subscription_data(result)
        
        return None
    
    async def delete_subscription(self, username: str) -> bool:
        """
        Удалить подписку
        
        Args:
            username: Username пользователя
            
        Returns:
            True если успешно удалено
        """
        clean_username = username.lstrip('@')
        logger.info(f"Удаляем подписку: {clean_username}")
        
        result = await self._make_request('DELETE', f'/api/user/{clean_username}')
        
        # Удаляем из кэша
        cache_key = f"GET:{self.api_url}/api/user/{clean_username}"
        if cache_key in self._cache:
            del self._cache[cache_key]
        
        return result is not None
    
    async def extend_subscription(self, username: str, days: int) -> Optional[SubscriptionData]:
        """
        Продлить подписку
        
        Args:
            username: Username пользователя
            days: Количество дней для продления
            
        Returns:
            SubscriptionData или None при ошибке
        """
        # Получаем текущую подписку
        subscription = await self.get_subscription(username, use_cache=False)
        
        if not subscription:
            logger.error(f"Подписка не найдена: {username}")
            return None
        
        # Вычисляем новую дату окончания
        if subscription.expire_date:
            # Если подписка еще активна, продлеваем от текущей даты окончания
            if subscription.expire_date > datetime.now():
                new_expire = subscription.expire_date + timedelta(days=days)
            else:
                # Если истекла, продлеваем от текущей даты
                new_expire = datetime.now() + timedelta(days=days)
        else:
            # Если не было даты окончания, устанавливаем
            new_expire = datetime.now() + timedelta(days=days)
        
        expire_timestamp = int(new_expire.timestamp())
        
        # Обновляем подписку
        update_data = {
            "expire": expire_timestamp,
            "status": "active"
        }
        
        logger.info(f"Продлеваем подписку {username} на {days} дней до {new_expire}")
        
        result = await self._make_request('PUT', f'/api/user/{username.lstrip("@")}', data=update_data)
        
        if result:
            return self._parse_subscription_data(result)
        
        return None
    
    async def update_subscription(self, username: str, updates: Dict) -> Optional[SubscriptionData]:
        """
        Обновить подписку
        
        Args:
            username: Username пользователя
            updates: Словарь с обновлениями
            
        Returns:
            SubscriptionData или None при ошибке
        """
        clean_username = username.lstrip('@')
        logger.info(f"Обновляем подписку {clean_username}: {updates}")
        
        result = await self._make_request('PUT', f'/api/user/{clean_username}', data=updates)
        
        if result:
            return self._parse_subscription_data(result)
        
        return None
    
    def _parse_subscription_data(self, data: Dict) -> SubscriptionData:
        """Парсинг данных подписки из ответа API"""
        # Парсим дату окончания
        expire_date = None
        expire = data.get('expire')
        if expire:
            try:
                if isinstance(expire, str):
                    expire_date = datetime.fromisoformat(expire.replace('Z', '+00:00'))
                else:
                    expire_date = datetime.fromtimestamp(expire)
            except (ValueError, TypeError) as e:
                logger.warning(f"Ошибка парсинга даты истечения: {e}")
        
        return SubscriptionData(
            username=data.get('username', ''),
            status=data.get('status', 'inactive'),
            expire_date=expire_date,
            data_limit=data.get('data_limit', 0),
            used_traffic=data.get('used_traffic', 0),
            subscription_url=data.get('subscription_url', ''),
            links=data.get('links', [])
        )
    
    async def get_all_subscriptions(self) -> List[SubscriptionData]:
        """
        Получить все подписки
        
        Returns:
            Список подписок
        """
        result = await self._make_request('GET', '/api/users')
        
        if result and isinstance(result, list):
            return [self._parse_subscription_data(user) for user in result]
        
        return []
    
    async def check_api_availability(self) -> bool:
        """
        Проверить доступность API
        
        Returns:
            True если API доступен
        """
        try:
            # Пробуем получить системную информацию
            result = await self._make_request('GET', '/api/system')
            if result:
                logger.info("✅ Marzban API доступен")
                return True
            
            # Пробуем альтернативный endpoint
            result = await self._make_request('GET', '/api/admin/token')
            if result is not None:  # Может вернуть ошибку авторизации, но это значит что API работает
                logger.info("✅ Marzban API доступен")
                return True
            
            logger.warning("❌ Marzban API недоступен")
            return False
        
        except Exception as e:
            logger.error(f"❌ Ошибка проверки API: {e}")
            return False
