#!/usr/bin/env python3
"""
Сервис для работы с пользователями
"""

import os
import json
import threading
import logging
from typing import Optional, Dict, List
from datetime import datetime

from ..models.user import User
from ..config import config

logger = logging.getLogger(__name__)

class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self):
        self.data_file = config.DATA_FILE
        self.data_lock = threading.Lock()
        self._load_data()
    
    def _load_data(self) -> Dict:
        """Загрузка данных из файла"""
        if not os.path.exists(self.data_file):
            return {"users": {}}
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            return {"users": {}}
    
    def _save_data(self, data: Dict) -> bool:
        """Сохранение данных в файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
            return False
    
    def _sanitize_username(self, username: Optional[str], fallback_name: Optional[str]) -> str:
        """Нормализация username"""
        if username:
            return username.lstrip('@')
        return (fallback_name or "user").lower().replace(" ", "_")
    
    def ensure_user_record(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> User:
        """Гарантированно создает запись пользователя"""
        with self.data_lock:
            data = self._load_data()
            users = data.setdefault("users", {})
            
            user_key = str(user_id)
            
            if user_key not in users:
                # Создаем нового пользователя
                user = User(
                    user_id=user_id,
                    username=self._sanitize_username(username, first_name)
                )
                users[user_key] = user.to_dict()
                self._save_data(data)
                logger.info(f"Создан новый пользователь: {user_id}")
            else:
                # Загружаем существующего пользователя
                user = User.from_dict(users[user_key])
            
            return user
    
    def get_user_record(self, user_id: int) -> Optional[User]:
        """Получение записи пользователя"""
        with self.data_lock:
            data = self._load_data()
            users = data.get("users", {})
            user_key = str(user_id)
            
            if user_key in users:
                return User.from_dict(users[user_key])
            return None
    
    def update_user_record(self, user_id: int, updates: Dict) -> bool:
        """Обновление записи пользователя"""
        with self.data_lock:
            data = self._load_data()
            users = data.get("users", {})
            user_key = str(user_id)
            
            if user_key not in users:
                return False
            
            # Обновляем данные
            user_data = users[user_key]
            user_data.update(updates)
            user_data['updated_at'] = datetime.now().isoformat()
            
            # Сохраняем
            return self._save_data(data)
    
    def credit_balance(self, user_id: int, amount_rub: int, reason: str = "") -> bool:
        """Зачисление средств на баланс"""
        with self.data_lock:
            data = self._load_data()
            users = data.get("users", {})
            user_key = str(user_id)
            
            if user_key not in users:
                return False
            
            user_data = users[user_key]
            current_balance = user_data.get('balance_rub', 0)
            user_data['balance_rub'] = max(0, current_balance + amount_rub)
            user_data['updated_at'] = datetime.now().isoformat()
            
            success = self._save_data(data)
            if success:
                logger.info(f"Зачисление {amount_rub} ₽ пользователю {user_id}. Причина: {reason}")
            return success
    
    def find_user_id_by_username(self, username: str) -> Optional[int]:
        """Поиск пользователя по username"""
        with self.data_lock:
            data = self._load_data()
            users = data.get("users", {})
            
            clean_username = username.lstrip('@')
            
            for user_id, user_data in users.items():
                if user_data.get('username') == clean_username:
                    return int(user_id)
            return None
    
    def record_referral(self, referrer_user_id: int, referred_user_id: int) -> bool:
        """Запись реферальной связи"""
        if referrer_user_id == referred_user_id:
            return False
        
        with self.data_lock:
            data = self._load_data()
            users = data.get("users", {})
            
            referrer_key = str(referrer_user_id)
            referred_key = str(referred_user_id)
            
            if referrer_key not in users or referred_key not in users:
                return False
            
            referred_user = users[referred_key]
            
            # Проверяем, что пользователь еще не имеет реферера
            if referred_user.get('referred_by'):
                return False
            
            # Устанавливаем связь
            referred_user['referred_by'] = referrer_user_id
            referred_user['updated_at'] = datetime.now().isoformat()
            
            # Добавляем в список рефералов
            referrer_user = users[referrer_key]
            referrals = referrer_user.get('referrals', [])
            if referred_user_id not in referrals:
                referrals.append(referred_user_id)
                referrer_user['referrals'] = referrals
                referrer_user['updated_at'] = datetime.now().isoformat()
            
            # Начисляем бонус (12 ₽ = 10 ₽ + 2 ₽ бонус)
            ref_bonus = 12
            current_balance = referrer_user.get('balance_rub', 0)
            referrer_user['balance_rub'] = max(0, current_balance + ref_bonus)
            referrer_user['updated_at'] = datetime.now().isoformat()
            
            success = self._save_data(data)
            if success:
                logger.info(f"Реферал: {referrer_user_id} получил {ref_bonus} ₽ за {referred_user_id}")
            return success
    
    def get_all_users(self) -> List[User]:
        """Получение всех пользователей"""
        with self.data_lock:
            data = self._load_data()
            users = data.get("users", {})
            
            return [User.from_dict(user_data) for user_data in users.values()]
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Получение статистики пользователя"""
        user = self.get_user_record(user_id)
        if not user:
            return {}
        
        return {
            'user_id': user.user_id,
            'username': user.username,
            'balance': user.balance_rub,  # Для совместимости с daily_payment_service
            'balance_rub': user.balance_rub,
            'days_remaining': user.days_from_balance(),
            'referrals_count': len(user.referrals),
            'referral_income': len(user.referrals) * 12,
            'referred_by': user.referred_by,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }
    
    def update_user_balance(self, user_id: int, new_balance: float) -> bool:
        """Обновить баланс пользователя"""
        with self.data_lock:
            data = self._load_data()
            users = data.get("users", {})
            user_key = str(user_id)
            
            if user_key not in users:
                return False
            
            users[user_key]['balance_rub'] = max(0, new_balance)
            users[user_key]['updated_at'] = datetime.now().isoformat()
            
            return self._save_data(data)
    
    def add_balance(self, user_id: int, amount: float) -> bool:
        """Добавить средства на баланс пользователя"""
        with self.data_lock:
            data = self._load_data()
            users = data.get("users", {})
            user_key = str(user_id)
            
            if user_key not in users:
                return False
            
            current_balance = users[user_key].get('balance_rub', 0)
            users[user_key]['balance_rub'] = current_balance + amount
            users[user_key]['updated_at'] = datetime.now().isoformat()
            
            return self._save_data(data)
    
    def get_balance(self, user_id: int) -> float:
        """Получить баланс пользователя"""
        user = self.get_user_record(user_id)
        if not user:
            return 0.0
        return user.balance_rub
    
    def days_from_balance(self, user_id: int) -> int:
        """Вычислить количество дней доступа исходя из баланса (4 рубля в день)"""
        balance = self.get_balance(user_id)
        return int(balance / 4)  # 4 рубля в день