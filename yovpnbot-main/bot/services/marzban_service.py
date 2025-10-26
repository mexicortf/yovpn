"""
Сервис Marzban
Интеграция с панелью управления Marzban для управления VPN-пользователями
"""

import logging
import aiohttp
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class MarzbanService:
    """
    Сервис для работы с Marzban API
    
    Отвечает за:
    - Создание и управление VPN-пользователями
    - Генерацию конфигураций VLESS
    - Управление подписками и доступом
    - Интеграцию с панелью Marzban
    """
    
    def __init__(self, api_url: str = "", admin_token: str = ""):
        """
        Инициализация сервиса
        
        Args:
            api_url: URL API Marzban
            admin_token: Токен администратора
        """
        self.api_url = api_url.rstrip('/')
        self.admin_token = admin_token
        self.session = None
        self._available = False
        
        logger.info(f"✅ MarzbanService инициализирован: {self.api_url}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить HTTP сессию"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.admin_token}',
                    'Content-Type': 'application/json'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def check_api_availability(self) -> bool:
        """
        Проверить доступность Marzban API
        
        Returns:
            bool: Доступен ли API
        """
        if not self.api_url:
            logger.warning("⚠️ Marzban API URL не настроен")
            self._available = False
            return False
        
        if not self.admin_token:
            logger.warning("⚠️ Marzban admin token не настроен")
            self._available = False
            return False
        
        try:
            session = await self._get_session()
            api_endpoint = f"{self.api_url}/api/system"
            
            logger.info(f"🔄 Проверка доступности Marzban API: {api_endpoint}")
            
            async with session.get(api_endpoint) as response:
                if response.status == 200:
                    self._available = True
                    logger.info("✅ Marzban API доступен")
                    return True
                elif response.status == 401:
                    logger.error("❌ Ошибка авторизации Marzban API: неверный токен")
                    logger.error(f"🔑 Проверьте MARZBAN_ADMIN_TOKEN в .env")
                    self._available = False
                    return False
                elif response.status == 404:
                    # Попробуем без /api префикса
                    alt_endpoint = f"{self.api_url}/system"
                    logger.info(f"🔄 Пробуем альтернативный эндпоинт: {alt_endpoint}")
                    
                    async with session.get(alt_endpoint) as alt_response:
                        if alt_response.status == 200:
                            self._available = True
                            logger.info("✅ Marzban API доступен (альтернативный эндпоинт)")
                            return True
                        else:
                            error_text = await alt_response.text()
                            logger.error(f"❌ Marzban API недоступен: HTTP {alt_response.status}")
                            logger.error(f"📄 Ответ: {error_text[:200]}")
                            self._available = False
                            return False
                else:
                    error_text = await response.text()
                    logger.warning(f"⚠️ Marzban API недоступен: HTTP {response.status}")
                    logger.warning(f"📄 Ответ: {error_text[:200]}")
                    self._available = False
                    return False
                    
        except aiohttp.ClientConnectorError as e:
            logger.error(f"❌ Не удалось подключиться к Marzban API: {e}")
            logger.error(f"🌐 Проверьте, что URL доступен: {self.api_url}")
            self._available = False
            return False
        except aiohttp.ClientTimeout as e:
            logger.error(f"❌ Таймаут при подключении к Marzban API: {e}")
            logger.error(f"⏱️ Сервер может быть перегружен или недоступен")
            self._available = False
            return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка проверки Marzban API: {e}")
            logger.error(f"🔍 URL: {self.api_url}")
            import traceback
            logger.error(traceback.format_exc())
            self._available = False
            return False
    
    async def create_user(self, username: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Создать пользователя в Marzban
        
        Args:
            username: Имя пользователя
            user_data: Данные пользователя (expire, data_limit, status, days)
        
        Returns:
            Optional[Dict]: Данные созданного пользователя
        """
        if not self._available:
            logger.warning("⚠️ Marzban API недоступен, пропускаем создание пользователя")
            return None
        
        try:
            session = await self._get_session()
            
            # Генерируем UUID для VLESS
            vless_uuid = user_data.get('vless_id', self._generate_uuid())
            
            # Рассчитываем дату истечения на основе дней
            import time
            from datetime import datetime, timedelta
            
            days = user_data.get('days', 0)
            if days > 0:
                expire_timestamp = int((datetime.now() + timedelta(days=days)).timestamp())
            else:
                expire_timestamp = user_data.get('expire', 0)  # 0 = без ограничений
            
            # Данные для создания пользователя с VLESS TCP REALITY
            payload = {
                "username": username,
                "proxies": {
                    "vless": {
                        "id": vless_uuid,
                        "flow": "xtls-rprx-vision"
                    }
                },
                "inbounds": {
                    "vless": [
                        "VLESS TCP REALITY",
                        "VLESS GRPC REALITY"
                    ]
                },
                "expire": expire_timestamp,
                "data_limit": user_data.get('data_limit', 0),  # 0 = безлимит
                "data_limit_reset_strategy": "no_reset",
                "status": user_data.get('status', 'active'),
                "note": user_data.get('note', f"Создан через YoVPN Bot - {days} дней")
            }
            
            logger.info(f"🔄 Создание пользователя {username} с параметрами: days={days}, expire={expire_timestamp}")
            logger.debug(f"Payload: {payload}")
            
            async with session.post(f"{self.api_url}/user", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Пользователь {username} создан в Marzban (VLESS TCP REALITY)")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка создания пользователя {username}: HTTP {response.status}")
                    logger.error(f"Детали ошибки: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Ошибка создания пользователя в Marzban: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def update_user(self, username: str, updates: Dict[str, Any]) -> bool:
        """
        Обновить пользователя в Marzban
        
        Args:
            username: Имя пользователя
            updates: Обновления
        
        Returns:
            bool: Успешность обновления
        """
        if not self._available:
            logger.warning("⚠️ Marzban API недоступен, пропускаем обновление пользователя")
            return False
        
        try:
            session = await self._get_session()
            
            async with session.put(f"{self.api_url}/user/{username}", json=updates) as response:
                if response.status == 200:
                    logger.info(f"✅ Пользователь {username} обновлен в Marzban")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка обновления пользователя {username}: {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Ошибка обновления пользователя в Marzban: {e}")
            return False
    
    async def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Получить данные пользователя из Marzban
        
        Args:
            username: Имя пользователя
        
        Returns:
            Optional[Dict]: Данные пользователя
        """
        if not self._available:
            logger.warning("⚠️ Marzban API недоступен, пропускаем получение пользователя")
            return None
        
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.api_url}/user/{username}") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.debug(f"✅ Получены данные пользователя {username}")
                    return result
                elif response.status == 404:
                    logger.warning(f"⚠️ Пользователь {username} не найден в Marzban")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка получения пользователя {username}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя из Marzban: {e}")
            return None
    
    async def delete_user(self, username: str) -> bool:
        """
        Удалить пользователя из Marzban
        
        Args:
            username: Имя пользователя
        
        Returns:
            bool: Успешность удаления
        """
        if not self._available:
            logger.warning("⚠️ Marzban API недоступен, пропускаем удаление пользователя")
            return False
        
        try:
            session = await self._get_session()
            
            async with session.delete(f"{self.api_url}/user/{username}") as response:
                if response.status == 200:
                    logger.info(f"✅ Пользователь {username} удален из Marzban")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка удаления пользователя {username}: {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Ошибка удаления пользователя из Marzban: {e}")
            return False
    
    async def get_user_config(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Получить конфигурацию пользователя
        
        Args:
            username: Имя пользователя
        
        Returns:
            Optional[Dict]: Конфигурация пользователя
        """
        user_data = await self.get_user(username)
        if not user_data:
            return None
        
        try:
            # Генерируем VLESS конфигурацию
            vless_config = self._generate_vless_config(user_data)
            
            return {
                'username': username,
                'vless_url': vless_config['url'],
                'subscription_url': f"{self.api_url}/sub/{username}",
                'expire': user_data.get('expire', 0),
                'status': user_data.get('status', 'inactive'),
                'data_limit': user_data.get('data_limit', 0),
                'used_traffic': user_data.get('used_traffic', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации конфигурации для {username}: {e}")
            return None
    
    async def get_user_subscription(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Получить subscription URL для пользователя
        Alias для get_user_config для совместимости с API
        
        Args:
            username: Имя пользователя
        
        Returns:
            Optional[Dict]: Данные подписки с subscription_url
        """
        return await self.get_user_config(username)
    
    def _generate_vless_config(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Сгенерировать VLESS конфигурацию
        
        Args:
            user_data: Данные пользователя
        
        Returns:
            Dict: VLESS конфигурация
        """
        # В реальной системе здесь была бы генерация настоящей конфигурации
        # Пока возвращаем демо-конфигурацию
        username = user_data.get('username', 'demo')
        
        return {
            'url': f"vless://{username}@demo-server.com:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=demo.com&pbk=demo-key&sid=demo-sid&fp=chrome&type=tcp&headerType=none#{username}",
            'config': f"vless://{username}@demo-server.com:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=demo.com&pbk=demo-key&sid=demo-sid&fp=chrome&type=tcp&headerType=none#{username}"
        }
    
    def _generate_uuid(self) -> str:
        """Сгенерировать UUID для пользователя"""
        import uuid
        return str(uuid.uuid4())
    
    async def get_system_stats(self) -> Optional[Dict[str, Any]]:
        """
        Получить статистику системы Marzban
        
        Returns:
            Optional[Dict]: Статистика системы
        """
        if not self._available:
            return None
        
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.api_url}/system") as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    logger.error(f"❌ Ошибка получения статистики Marzban: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики Marzban: {e}")
            return None
    
    async def close(self):
        """Закрыть HTTP сессию"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("🔌 HTTP сессия Marzban закрыта")
    
    def is_available(self) -> bool:
        """Проверить доступность API"""
        return self._available