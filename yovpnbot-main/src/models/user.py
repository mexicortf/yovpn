#!/usr/bin/env python3
"""
Модель пользователя для бота YOVPN
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class User:
    """Модель пользователя"""
    user_id: int
    username: str
    balance_rub: int = 0
    bonus_given: bool = False
    first_start_completed: bool = False
    referred_by: Optional[int] = None
    referrals: List[int] = None
    device: Optional[str] = None
    app_link: Optional[str] = None
    vless_link: Optional[str] = None
    subscription_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.referrals is None:
            self.referrals = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для сохранения в JSON"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'balance_rub': self.balance_rub,
            'bonus_given': self.bonus_given,
            'first_start_completed': self.first_start_completed,
            'referred_by': self.referred_by,
            'referrals': self.referrals,
            'device': self.device,
            'app_link': self.app_link,
            'vless_link': self.vless_link,
            'subscription_url': self.subscription_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Создание объекта из словаря"""
        # Обработка дат
        created_at = None
        updated_at = None
        
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                created_at = datetime.now()
        
        if data.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(data['updated_at'])
            except (ValueError, TypeError):
                updated_at = datetime.now()
        
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            balance_rub=data.get('balance_rub', 0),
            bonus_given=data.get('bonus_given', False),
            first_start_completed=data.get('first_start_completed', False),
            referred_by=data.get('referred_by'),
            referrals=data.get('referrals', []),
            device=data.get('device'),
            app_link=data.get('app_link'),
            vless_link=data.get('vless_link'),
            subscription_url=data.get('subscription_url'),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def update_balance(self, amount: int, reason: str = ""):
        """Обновление баланса пользователя"""
        self.balance_rub = max(0, self.balance_rub + amount)
        self.updated_at = datetime.now()
    
    def add_referral(self, referred_user_id: int):
        """Добавление реферала"""
        if referred_user_id not in self.referrals:
            self.referrals.append(referred_user_id)
            self.updated_at = datetime.now()
    
    def days_from_balance(self) -> int:
        """Вычисление дней доступа из баланса (4 рубля = 1 день)"""
        try:
            return self.balance_rub // 4
        except (TypeError, ValueError):
            return 0