"""
Модели базы данных для YoVPN Bot
Используется MySQL (общая с Marzban)
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .db import Base


class UserStatus(enum.Enum):
    """Статусы пользователя"""
    ACTIVE = "active"
    BLOCKED = "blocked"
    INACTIVE = "inactive"


class SubscriptionStatus(enum.Enum):
    """Статусы подписки"""
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"
    LIMITED = "limited"


class TransactionType(enum.Enum):
    """Типы транзакций"""
    DEPOSIT = "deposit"  # Пополнение
    WITHDRAW = "withdraw"  # Списание
    BONUS = "bonus"  # Бонус
    REFUND = "refund"  # Возврат
    REFERRAL = "referral"  # Реферальный бонус


class User(Base):
    """
    Модель пользователя
    Хранит информацию о пользователях Telegram бота
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tg_id = Column(Integer, unique=True, index=True, nullable=False, comment="Telegram ID пользователя")
    username = Column(String(255), nullable=True, comment="Username в Telegram")
    first_name = Column(String(255), nullable=True, comment="Имя пользователя")
    last_name = Column(String(255), nullable=True, comment="Фамилия пользователя")
    
    # Баланс и статус
    balance = Column(Float, default=0.0, nullable=False, comment="Баланс пользователя в рублях")
    is_blocked = Column(Boolean, default=False, nullable=False, comment="Заблокирован ли пользователь")
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False, comment="Статус пользователя")
    
    # Дополнительная информация
    language = Column(String(10), default="ru", nullable=False, comment="Язык интерфейса")
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Кто пригласил пользователя")
    referral_count = Column(Integer, default=0, nullable=False, comment="Количество рефералов")
    referral_level = Column(Integer, default=0, nullable=False, comment="Уровень в реферальной иерархии")
    referral_earnings = Column(Float, default=0.0, nullable=False, comment="Заработок с рефералов")
    
    # Проверка подписки на канал
    channel_subscribed = Column(Boolean, default=False, nullable=False, comment="Подписан ли на канал @yodevelop")
    channel_check_at = Column(DateTime(timezone=True), nullable=True, comment="Последняя проверка подписки")
    
    # Флаги
    bonus_given = Column(Boolean, default=False, nullable=False, comment="Выдан ли приветственный бонус")
    first_start_completed = Column(Boolean, default=False, nullable=False, comment="Завершена ли первая настройка")
    activation_step = Column(Integer, default=0, nullable=False, comment="Шаг активации (0-3)")
    selected_platform = Column(String(50), nullable=True, comment="Выбранная платформа (iOS/Android/etc)")
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Дата регистрации")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Дата последнего обновления")
    last_activity = Column(DateTime(timezone=True), nullable=True, comment="Последняя активность")
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    referrer = relationship("User", remote_side=[id], backref="referrals")

    def __repr__(self):
        return f"<User(id={self.id}, tg_id={self.tg_id}, username={self.username}, balance={self.balance})>"


class Subscription(Base):
    """
    Модель подписки
    Хранит информацию о VPN подписках пользователей
    """
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="ID пользователя")
    
    # Информация о подписке
    marzban_username = Column(String(255), unique=True, nullable=False, comment="Username в Marzban")
    marzban_id = Column(String(255), nullable=True, comment="ID пользователя в Marzban")
    
    # Период действия
    start_date = Column(DateTime(timezone=True), nullable=False, comment="Дата начала подписки")
    end_date = Column(DateTime(timezone=True), nullable=True, comment="Дата окончания подписки")
    
    # Статус
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False, comment="Статус подписки")
    is_active = Column(Boolean, default=True, nullable=False, comment="Активна ли подписка")
    
    # Трафик
    data_limit = Column(Integer, default=0, nullable=False, comment="Лимит трафика в байтах (0 = безлимит)")
    used_traffic = Column(Integer, default=0, nullable=False, comment="Использованный трафик в байтах")
    
    # Конфигурация
    subscription_url = Column(Text, nullable=True, comment="URL подписки")
    config_data = Column(Text, nullable=True, comment="Данные конфигурации (JSON)")
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Дата создания")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Дата обновления")
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status={self.status}, marzban_username={self.marzban_username})>"


class Transaction(Base):
    """
    Модель транзакции
    Хранит историю финансовых операций пользователей
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="ID пользователя")
    
    # Информация о транзакции
    amount = Column(Float, nullable=False, comment="Сумма транзакции в рублях")
    type = Column(Enum(TransactionType), nullable=False, comment="Тип транзакции")
    description = Column(Text, nullable=True, comment="Описание транзакции")
    
    # Дополнительная информация
    balance_before = Column(Float, nullable=False, comment="Баланс до транзакции")
    balance_after = Column(Float, nullable=False, comment="Баланс после транзакции")
    
    # Связь с платежной системой
    payment_id = Column(String(255), nullable=True, comment="ID платежа в платежной системе")
    payment_method = Column(String(50), nullable=True, comment="Метод оплаты (card, crypto, etc)")
    
    # Временная метка
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Дата создания")
    
    # Relationships
    user = relationship("User", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, type={self.type})>"


class Settings(Base):
    """
    Модель настроек
    Хранит глобальные настройки бота и системы
    """
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False, comment="Ключ настройки")
    value = Column(Text, nullable=True, comment="Значение настройки")
    description = Column(Text, nullable=True, comment="Описание настройки")
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Дата создания")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Дата обновления")

    def __repr__(self):
        return f"<Settings(key={self.key}, value={self.value})>"


# Создаем важные настройки по умолчанию
DEFAULT_SETTINGS = {
    "maintenance_mode": "false",  # Режим техобслуживания
    "webapp_enabled": "true",  # WebApp режим включен
    "welcome_bonus": "12",  # Приветственный бонус (3 дня * 4 руб)
    "daily_price": "4",  # Цена за день в рублях
    "referral_bonus": "8",  # Бонус за реферала (2 дня * 4 руб)
    "min_deposit": "40",  # Минимальное пополнение (10 дней * 4 руб)
    "support_username": "@YoVPNSupport",  # Username поддержки
    "channel_username": "@YoVPN",  # Username канала
}
