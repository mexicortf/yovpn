"""
Сервис пользователей
Управление пользователями, их данными и статистикой
"""

import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from .cache_service import get_cache

logger = logging.getLogger(__name__)
cache = get_cache()

class UserService:
    """
    Сервис для работы с пользователями
    
    Отвечает за:
    - Создание и обновление пользователей
    - Управление балансом и подписками
    - Статистику и аналитику
    - Сохранение данных в файл
    """
    
    def __init__(self, data_file: str = "data.json"):
        """
        Инициализация сервиса
        
        Args:
            data_file: Путь к файлу с данными
        """
        # Создаем путь к файлу данных
        if not Path(data_file).is_absolute():
            # Если путь относительный, создаем в директории data
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            self.data_file = data_dir / data_file
        else:
            self.data_file = Path(data_file)
        
        # Убеждаемся, что родительская директория существует
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.users = self._load_users()
        logger.info(f"✅ UserService инициализирован, загружено {len(self.users)} пользователей")
        logger.info(f"📁 Файл данных: {self.data_file.absolute()}")
    
    def _load_users(self) -> Dict[int, Dict[str, Any]]:
        """
        Загрузить пользователей из файла
        
        Returns:
            Dict: Словарь пользователей
        """
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки пользователей: {e}")
            return {}
    
    def _save_users(self):
        """
        Сохранить пользователей в файл и инвалидировать кэш
        """
        try:
            # Убеждаемся, что директория существует
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Сначала записываем во временный файл
            temp_file = self.data_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            
            # Затем атомарно переименовываем
            temp_file.replace(self.data_file)
            
            # Инвалидируем кэш пользователей
            cache.delete_pattern("user:")
            cache.delete_pattern("user_stats:")
            
            logger.debug("💾 Пользователи сохранены, кэш инвалидирован")
        except PermissionError as e:
            logger.error(f"❌ Ошибка доступа при сохранении пользователей: {e}")
            logger.error(f"📁 Проверьте права доступа к: {self.data_file.absolute()}")
        except OSError as e:
            logger.error(f"❌ Ошибка файловой системы при сохранении пользователей: {e}")
            logger.error(f"📁 Путь: {self.data_file.absolute()}")
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка сохранения пользователей: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def create_or_update_user(self, user_id: int, username: Optional[str], first_name: str) -> Dict[str, Any]:
        """
        Создать или обновить пользователя
        
        Args:
            user_id: ID пользователя
            username: Имя пользователя в Telegram
            first_name: Имя пользователя
        
        Returns:
            Dict: Данные пользователя (с ключом 'is_new' для новых пользователей)
        """
        is_new_user = user_id not in self.users
        
        if is_new_user:
            # Создаем нового пользователя с приветственным бонусом 15₽
            self.users[user_id] = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'balance': 15.0,  # Стартовый бонус
                'subscription_active': False,
                'subscription_days': 0,
                'total_payments': 0.0,
                'referrals': [],
                'referral_code': f"ref_{user_id}",
                'created_at': self._get_current_timestamp(),
                'last_activity': self._get_current_timestamp(),
                'settings': {
                    'notifications': True,
                    'auto_renewal': True,
                    'language': 'ru'
                },
                'is_new': True  # Флаг нового пользователя
            }
            logger.info(f"👤 Создан новый пользователь: {first_name} (ID: {user_id}) с балансом 15₽")
        else:
            # Обновляем существующего пользователя
            self.users[user_id].update({
                'username': username,
                'first_name': first_name,
                'last_activity': self._get_current_timestamp()
            })
            logger.debug(f"👤 Обновлен пользователь: {first_name} (ID: {user_id})")
        
        self._save_users()
        user_data = self.users[user_id].copy()
        user_data['is_new'] = is_new_user
        return user_data
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить данные пользователя (с кэшированием)
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Optional[Dict]: Данные пользователя или None
        """
        # Проверяем кэш
        cache_key = f"user:{user_id}"
        cached_user = cache.get(cache_key)
        if cached_user is not None:
            return cached_user
        
        # Получаем из БД
        user = self.users.get(user_id)
        
        # Сохраняем в кэш
        if user:
            cache.set(cache_key, user, ttl=60)  # Кэш на 1 минуту
        
        return user
    
    async def get_or_create_user(self, user_id: int, username: Optional[str] = None, first_name: str = "Пользователь") -> Dict[str, Any]:
        """
        Получить пользователя или создать нового, если его нет
        
        Args:
            user_id: ID пользователя
            username: Имя пользователя в Telegram
            first_name: Имя пользователя
        
        Returns:
            Dict: Данные пользователя
        """
        user = await self.get_user(user_id)
        if not user:
            user = await self.create_or_update_user(user_id, username, first_name)
            logger.info(f"👤 Пользователь {user_id} создан автоматически")
        return user
    
    async def update_user_balance(self, user_id: int, amount: float, operation: str = "add") -> bool:
        """
        Обновить баланс пользователя
        
        Args:
            user_id: ID пользователя
            amount: Сумма
            operation: Операция (add, subtract, set)
        
        Returns:
            bool: Успешность операции
        """
        if user_id not in self.users:
            logger.warning(f"⚠️ Пользователь {user_id} не найден")
            return False
        
        user = self.users[user_id]
        current_balance = user.get('balance', 0.0)
        
        if operation == "add":
            new_balance = current_balance + amount
        elif operation == "subtract":
            new_balance = max(0, current_balance - amount)
        elif operation == "set":
            new_balance = amount
        else:
            logger.error(f"❌ Неизвестная операция: {operation}")
            return False
        
        user['balance'] = round(new_balance, 2)
        self._save_users()
        
        logger.info(f"💰 Баланс пользователя {user_id}: {current_balance} → {new_balance}")
        return True
    
    async def get_user_balance(self, user_id: int) -> float:
        """
        Получить баланс пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            float: Баланс пользователя
        """
        user = await self.get_user(user_id)
        return user.get('balance', 0.0) if user else 0.0
    
    async def calculate_days_from_balance(self, user_id: int, daily_cost: float = 4.0) -> int:
        """
        Рассчитать количество дней из баланса
        
        Args:
            user_id: ID пользователя
            daily_cost: Стоимость дня
        
        Returns:
            int: Количество дней
        """
        balance = await self.get_user_balance(user_id)
        return int(balance / daily_cost)
    
    async def activate_subscription(self, user_id: int, days: int) -> bool:
        """
        Активировать подписку пользователя
        
        Args:
            user_id: ID пользователя
            days: Количество дней
        
        Returns:
            bool: Успешность активации
        """
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        user['subscription_active'] = True
        user['subscription_days'] = days
        user['subscription_started'] = self._get_current_timestamp()
        
        self._save_users()
        logger.info(f"✅ Подписка активирована для пользователя {user_id}: {days} дней")
        return True
    
    async def deactivate_subscription(self, user_id: int) -> bool:
        """
        Деактивировать подписку пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            bool: Успешность деактивации
        """
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        user['subscription_active'] = False
        user['subscription_days'] = 0
        
        self._save_users()
        logger.info(f"❌ Подписка деактивирована для пользователя {user_id}")
        return True
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Получить статистику пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Dict: Статистика пользователя
        """
        user = await self.get_user(user_id)
        if not user:
            return {}
        
        return {
            'balance': user.get('balance', 0.0),
            'subscription_active': user.get('subscription_active', False),
            'subscription_days': user.get('subscription_days', 0),
            'total_payments': user.get('total_payments', 0.0),
            'referrals_count': len(user.get('referrals', [])),
            'created_at': user.get('created_at'),
            'last_activity': user.get('last_activity')
        }
    
    async def add_referral(self, user_id: int, referred_user_id: int) -> bool:
        """
        Добавить реферала
        
        Args:
            user_id: ID пользователя, который пригласил
            referred_user_id: ID приглашенного пользователя
        
        Returns:
            bool: Успешность добавления
        """
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        referrals = user.get('referrals', [])
        
        if referred_user_id not in referrals:
            referrals.append(referred_user_id)
            user['referrals'] = referrals
            self._save_users()
            
            # Начисляем бонус за реферала
            await self.update_user_balance(user_id, 20.0, "add")
            
            logger.info(f"🎁 Добавлен реферал: {user_id} → {referred_user_id}")
            return True
        
        return False
    
    def _get_current_timestamp(self) -> str:
        """Получить текущую временную метку"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def get_all_users(self) -> Dict[int, Dict[str, Any]]:
        """
        Получить всех пользователей
        
        Returns:
            Dict: Все пользователи
        """
        return self.users.copy()
    
    async def get_users_count(self) -> int:
        """
        Получить количество пользователей
        
        Returns:
            int: Количество пользователей
        """
        return len(self.users)