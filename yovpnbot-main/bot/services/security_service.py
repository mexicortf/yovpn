"""
Сервис безопасности
Управление rate limiting, валидацией и защитой от спама
"""

import logging
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityService:
    """
    Сервис для обеспечения безопасности бота
    
    Отвечает за:
    - Rate limiting (ограничение частоты запросов)
    - Валидацию пользовательского ввода
    - Защиту от спама и злоупотреблений
    - Обнаружение подозрительной активности
    """
    
    def __init__(self, rate_limit_rpm: int = 60, rate_limit_rph: int = 1000):
        """
        Инициализация сервиса безопасности
        
        Args:
            rate_limit_rpm: Лимит запросов в минуту
            rate_limit_rph: Лимит запросов в час
        """
        self.rate_limit_rpm = rate_limit_rpm
        self.rate_limit_rph = rate_limit_rph
        
        # Хранилище для отслеживания запросов
        self._user_requests: Dict[int, list] = defaultdict(list)
        self._blocked_users: Dict[int, datetime] = {}
        self._suspicious_activity: Dict[int, int] = defaultdict(int)
        
        logger.info(f"✅ SecurityService инициализирован (RPM: {rate_limit_rpm}, RPH: {rate_limit_rph})")
    
    def check_rate_limit(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Проверить rate limit для пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Tuple[bool, Optional[str]]: (Разрешено ли, Сообщение об ошибке если не разрешено)
        """
        current_time = time.time()
        
        # Проверяем, не заблокирован ли пользователь
        if user_id in self._blocked_users:
            unblock_time = self._blocked_users[user_id]
            if datetime.now() < unblock_time:
                remaining_time = int((unblock_time - datetime.now()).total_seconds())
                return False, f"⚠️ Вы временно заблокированы. Осталось: {remaining_time} сек."
            else:
                # Разблокируем пользователя
                del self._blocked_users[user_id]
                logger.info(f"🔓 Пользователь {user_id} разблокирован")
        
        # Получаем историю запросов
        requests = self._user_requests[user_id]
        
        # Удаляем старые запросы (старше 1 часа)
        requests = [req_time for req_time in requests if current_time - req_time < 3600]
        self._user_requests[user_id] = requests
        
        # Проверяем лимит запросов в час
        if len(requests) >= self.rate_limit_rph:
            logger.warning(f"⚠️ Пользователь {user_id} превысил лимит запросов в час")
            self._block_user(user_id, minutes=60)
            return False, "❌ Вы превысили лимит запросов в час. Попробуйте через 1 час."
        
        # Проверяем лимит запросов в минуту
        recent_requests = [req_time for req_time in requests if current_time - req_time < 60]
        if len(recent_requests) >= self.rate_limit_rpm:
            logger.warning(f"⚠️ Пользователь {user_id} превысил лимит запросов в минуту")
            self._block_user(user_id, minutes=5)
            return False, "❌ Слишком много запросов. Пожалуйста, подождите 5 минут."
        
        # Добавляем текущий запрос
        self._user_requests[user_id].append(current_time)
        
        return True, None
    
    def _block_user(self, user_id: int, minutes: int = 5):
        """
        Заблокировать пользователя на указанное время
        
        Args:
            user_id: ID пользователя
            minutes: Количество минут блокировки
        """
        unblock_time = datetime.now() + timedelta(minutes=minutes)
        self._blocked_users[user_id] = unblock_time
        
        # Увеличиваем счетчик подозрительной активности
        self._suspicious_activity[user_id] += 1
        
        logger.warning(f"🚫 Пользователь {user_id} заблокирован на {minutes} минут")
    
    def is_user_blocked(self, user_id: int) -> bool:
        """
        Проверить, заблокирован ли пользователь
        
        Args:
            user_id: ID пользователя
        
        Returns:
            bool: Заблокирован ли пользователь
        """
        if user_id not in self._blocked_users:
            return False
        
        if datetime.now() >= self._blocked_users[user_id]:
            del self._blocked_users[user_id]
            return False
        
        return True
    
    def validate_user_input(self, text: str, max_length: int = 1000) -> Tuple[bool, Optional[str]]:
        """
        Валидация пользовательского ввода
        
        Args:
            text: Текст для валидации
            max_length: Максимальная длина текста
        
        Returns:
            Tuple[bool, Optional[str]]: (Валидно ли, Сообщение об ошибке если не валидно)
        """
        if not text or not text.strip():
            return False, "❌ Текст не может быть пустым"
        
        if len(text) > max_length:
            return False, f"❌ Текст слишком длинный (максимум {max_length} символов)"
        
        # Проверяем на спам-паттерны
        spam_patterns = [
            'http://', 'https://', 'www.', '.com', '.ru', '.net',
            'telegram.me', 't.me', '@', 'bit.ly'
        ]
        
        suspicious_count = sum(1 for pattern in spam_patterns if pattern.lower() in text.lower())
        if suspicious_count >= 3:
            return False, "❌ Обнаружен подозрительный контент"
        
        return True, None
    
    def validate_amount(self, amount: float, min_amount: float = 1.0, max_amount: float = 10000.0) -> Tuple[bool, Optional[str]]:
        """
        Валидация суммы платежа
        
        Args:
            amount: Сумма
            min_amount: Минимальная сумма
            max_amount: Максимальная сумма
        
        Returns:
            Tuple[bool, Optional[str]]: (Валидно ли, Сообщение об ошибке если не валидно)
        """
        if amount < min_amount:
            return False, f"❌ Минимальная сумма: {min_amount} ₽"
        
        if amount > max_amount:
            return False, f"❌ Максимальная сумма: {max_amount} ₽"
        
        return True, None
    
    def validate_user_id(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Валидация ID пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Tuple[bool, Optional[str]]: (Валидно ли, Сообщение об ошибке если не валидно)
        """
        if not isinstance(user_id, int):
            return False, "❌ ID должен быть числом"
        
        if user_id <= 0:
            return False, "❌ ID должен быть положительным числом"
        
        if user_id > 9999999999:  # Максимальный ID Telegram
            return False, "❌ Неверный формат ID"
        
        return True, None
    
    def detect_suspicious_activity(self, user_id: int) -> bool:
        """
        Обнаружить подозрительную активность
        
        Args:
            user_id: ID пользователя
        
        Returns:
            bool: Обнаружена ли подозрительная активность
        """
        # Проверяем количество блокировок
        if self._suspicious_activity[user_id] >= 5:
            logger.warning(f"🚨 Обнаружена подозрительная активность от пользователя {user_id}")
            return True
        
        return False
    
    def get_security_stats(self) -> Dict[str, any]:
        """
        Получить статистику безопасности
        
        Returns:
            Dict: Статистика безопасности
        """
        current_time = datetime.now()
        
        # Считаем активных пользователей
        active_users = len([
            user_id for user_id, requests in self._user_requests.items()
            if any(current_time.timestamp() - req_time < 3600 for req_time in requests)
        ])
        
        # Считаем заблокированных пользователей
        blocked_users = len([
            user_id for user_id, unblock_time in self._blocked_users.items()
            if current_time < unblock_time
        ])
        
        # Считаем пользователей с подозрительной активностью
        suspicious_users = len([
            user_id for user_id, count in self._suspicious_activity.items()
            if count >= 3
        ])
        
        return {
            'active_users': active_users,
            'blocked_users': blocked_users,
            'suspicious_users': suspicious_users,
            'total_tracked_users': len(self._user_requests),
            'rate_limit_rpm': self.rate_limit_rpm,
            'rate_limit_rph': self.rate_limit_rph
        }
    
    def reset_user_limits(self, user_id: int):
        """
        Сбросить лимиты пользователя
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self._user_requests:
            del self._user_requests[user_id]
        
        if user_id in self._blocked_users:
            del self._blocked_users[user_id]
        
        if user_id in self._suspicious_activity:
            del self._suspicious_activity[user_id]
        
        logger.info(f"🔄 Лимиты пользователя {user_id} сброшены")
    
    def cleanup_old_data(self):
        """
        Очистить старые данные
        """
        current_time = time.time()
        
        # Удаляем старые запросы
        for user_id in list(self._user_requests.keys()):
            requests = [req_time for req_time in self._user_requests[user_id] if current_time - req_time < 3600]
            if requests:
                self._user_requests[user_id] = requests
            else:
                del self._user_requests[user_id]
        
        # Удаляем истекшие блокировки
        for user_id in list(self._blocked_users.keys()):
            if datetime.now() >= self._blocked_users[user_id]:
                del self._blocked_users[user_id]
        
        logger.debug("🧹 Очистка старых данных безопасности завершена")
