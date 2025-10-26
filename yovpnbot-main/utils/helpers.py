"""
Helper Functions
Вспомогательные функции для приложения
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re
import hashlib
import secrets
from decimal import Decimal


def format_currency(amount: float, currency: str = "₽") -> str:
    """
    Форматирование валюты
    
    Args:
        amount: Сумма
        currency: Символ валюты
    
    Returns:
        Отформатированная строка
    """
    return f"{amount:.2f} {currency}"


def format_date(date: Optional[datetime], format: str = "%d.%m.%Y") -> str:
    """
    Форматирование даты
    
    Args:
        date: Дата
        format: Формат даты
    
    Returns:
        Отформатированная дата или "-"
    """
    if not date:
        return "-"
    return date.strftime(format)


def format_datetime(date: Optional[datetime], format: str = "%d.%m.%Y %H:%M") -> str:
    """
    Форматирование даты и времени
    
    Args:
        date: Дата
        format: Формат
    
    Returns:
        Отформатированная дата и время или "-"
    """
    if not date:
        return "-"
    return date.strftime(format)


def format_traffic(bytes_value: int) -> str:
    """
    Форматирование трафика в читаемый вид
    
    Args:
        bytes_value: Количество байт
    
    Returns:
        Отформатированная строка (например: "1.5 GB")
    """
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = bytes_value
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def calculate_days_from_balance(balance: float, daily_price: float = 4.0) -> int:
    """
    Вычислить количество дней из баланса
    
    Args:
        balance: Баланс в рублях
        daily_price: Цена за день
    
    Returns:
        Количество дней
    """
    return int(balance // daily_price)


def calculate_price_for_days(days: int, daily_price: float = 4.0) -> float:
    """
    Вычислить стоимость за количество дней
    
    Args:
        days: Количество дней
        daily_price: Цена за день
    
    Returns:
        Стоимость
    """
    return days * daily_price


def days_until(date: datetime) -> int:
    """
    Вычислить количество дней до даты
    
    Args:
        date: Дата
    
    Returns:
        Количество дней
    """
    if not date:
        return 0
    
    now = datetime.now()
    if date < now:
        return 0
    
    return (date - now).days


def is_valid_telegram_username(username: str) -> bool:
    """
    Проверить валидность Telegram username
    
    Args:
        username: Username
    
    Returns:
        True если валидный
    """
    pattern = r'^@?[a-zA-Z0-9_]{5,32}$'
    return bool(re.match(pattern, username))


def clean_telegram_username(username: str) -> str:
    """
    Очистить Telegram username от @
    
    Args:
        username: Username
    
    Returns:
        Очищенный username
    """
    return username.lstrip('@')


def generate_unique_id(prefix: str = "") -> str:
    """
    Генерировать уникальный ID
    
    Args:
        prefix: Префикс для ID
    
    Returns:
        Уникальный ID
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = secrets.token_hex(4)
    return f"{prefix}{timestamp}{random_part}"


def hash_password(password: str) -> str:
    """
    Хэшировать пароль
    
    Args:
        password: Пароль
    
    Returns:
        Хэш пароля
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """
    Проверить пароль
    
    Args:
        password: Пароль
        hashed: Хэш пароля
    
    Returns:
        True если пароль верный
    """
    return hash_password(password) == hashed


def escape_html(text: str) -> str:
    """
    Экранировать HTML специальные символы
    
    Args:
        text: Текст
    
    Returns:
        Экранированный текст
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Обрезать строку до максимальной длины
    
    Args:
        text: Текст
        max_length: Максимальная длина
        suffix: Суффикс
    
    Returns:
        Обрезанная строка
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_bool(value: Any) -> bool:
    """
    Парсинг boolean значения
    
    Args:
        value: Значение
    
    Returns:
        Boolean
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'y', 'on')
    
    return bool(value)


if __name__ == "__main__":
    # Тесты
    print(format_currency(100.50))
    print(format_traffic(1536000000))
    print(calculate_days_from_balance(40))
    print(calculate_price_for_days(10))
    print(is_valid_telegram_username("@username"))
    print(clean_telegram_username("@username"))
    print(generate_unique_id("user_"))
