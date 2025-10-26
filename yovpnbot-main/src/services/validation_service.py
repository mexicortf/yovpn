"""
Сервис валидации входных данных
Использует pydantic для строгой валидации всех пользовательских данных
"""

import re
import logging
from typing import Optional, Union, List, Dict, Any
from pydantic import BaseModel, validator, Field
from enum import Enum

logger = logging.getLogger(__name__)

class PaymentMethod(str, Enum):
    """Способы оплаты"""
    CARD = "card"
    SBP = "sbp"
    BANK = "bank"
    WALLET = "wallet"

class UserRole(str, Enum):
    """Роли пользователей"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class ValidationError(Exception):
    """Исключение валидации"""
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class PaymentRequest(BaseModel):
    """Валидация запроса на платеж"""
    amount: int = Field(..., gt=0, le=10000, description="Сумма платежа в рублях")
    payment_method: PaymentMethod
    user_id: int = Field(..., gt=0)
    currency: str = Field(default="RUB", regex="^[A-Z]{3}$")
    
    @validator('amount')
    def validate_amount(cls, v):
        """Валидация суммы платежа"""
        if v < 4:
            raise ValueError("Минимальная сумма платежа: 4 рубля")
        if v % 4 != 0:
            raise ValueError("Сумма должна быть кратна 4 рублям (стоимость дня)")
        return v
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Валидация ID пользователя"""
        if v <= 0:
            raise ValueError("ID пользователя должен быть положительным числом")
        return v

class UserRegistration(BaseModel):
    """Валидация регистрации пользователя"""
    user_id: int = Field(..., gt=0)
    username: Optional[str] = Field(None, max_length=32)
    first_name: Optional[str] = Field(None, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)
    language_code: str = Field(default="ru", regex="^[a-z]{2}(-[A-Z]{2})?$")
    
    @validator('username')
    def validate_username(cls, v):
        """Валидация имени пользователя"""
        if v is not None:
            # Удаляем @ если есть
            v = v.lstrip('@')
            # Проверяем на допустимые символы
            if not re.match(r'^[a-zA-Z0-9_]{1,32}$', v):
                raise ValueError("Имя пользователя может содержать только буквы, цифры и подчеркивания")
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Валидация имен"""
        if v is not None:
            # Удаляем опасные символы
            v = re.sub(r'[<>"\']', '', v)
            if len(v.strip()) == 0:
                return None
        return v

class ServerConfig(BaseModel):
    """Валидация конфигурации сервера"""
    server_name: str = Field(..., min_length=1, max_length=50)
    server_ip: str = Field(..., regex=r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    server_port: int = Field(..., ge=1, le=65535)
    protocol: str = Field(..., regex="^(vless|vmess|trojan)$")
    encryption: str = Field(default="none", regex="^(none|aes-128-gcm|chacha20-poly1305)$")
    
    @validator('server_ip')
    def validate_ip(cls, v):
        """Валидация IP адреса"""
        parts = v.split('.')
        if len(parts) != 4:
            raise ValueError("Неверный формат IP адреса")
        
        for part in parts:
            if not 0 <= int(part) <= 255:
                raise ValueError("Неверный формат IP адреса")
        
        return v

class SubscriptionRequest(BaseModel):
    """Валидация запроса на подписку"""
    user_id: int = Field(..., gt=0)
    duration_days: int = Field(..., ge=1, le=365)
    server_location: str = Field(..., min_length=2, max_length=50)
    auto_renew: bool = Field(default=False)
    
    @validator('duration_days')
    def validate_duration(cls, v):
        """Валидация длительности подписки"""
        if v < 1:
            raise ValueError("Минимальная длительность подписки: 1 день")
        if v > 365:
            raise ValueError("Максимальная длительность подписки: 365 дней")
        return v

class BalanceOperation(BaseModel):
    """Валидация операции с балансом"""
    user_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0, le=100000)
    operation_type: str = Field(..., regex="^(add|subtract|set)$")
    reason: str = Field(default="", max_length=200)
    
    @validator('amount')
    def validate_amount(cls, v):
        """Валидация суммы"""
        if v <= 0:
            raise ValueError("Сумма должна быть положительной")
        if v > 100000:
            raise ValueError("Максимальная сумма: 100,000 рублей")
        return round(v, 2)  # Округляем до 2 знаков

class ReferralRequest(BaseModel):
    """Валидация реферального запроса"""
    referrer_id: int = Field(..., gt=0)
    referred_id: int = Field(..., gt=0)
    referral_code: str = Field(..., min_length=6, max_length=20)
    
    @validator('referrer_id', 'referred_id')
    def validate_user_ids(cls, v):
        """Валидация ID пользователей"""
        if v <= 0:
            raise ValueError("ID пользователя должен быть положительным числом")
        return v
    
    @validator('referral_code')
    def validate_referral_code(cls, v):
        """Валидация реферального кода"""
        if not re.match(r'^[A-Z0-9]{6,20}$', v):
            raise ValueError("Реферальный код должен содержать только заглавные буквы и цифры")
        return v

class ValidationService:
    """Сервис валидации входных данных"""
    
    def __init__(self):
        self.validation_rules = {
            'username': r'^[a-zA-Z0-9_]{1,32}$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'ip_address': r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
            'port': r'^(?:[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$',
            'user_id': r'^[1-9][0-9]*$',
            'amount': r'^[0-9]+(\.[0-9]{1,2})?$'
        }
    
    def validate_payment_request(self, data: Dict[str, Any]) -> PaymentRequest:
        """Валидация запроса на платеж"""
        try:
            return PaymentRequest(**data)
        except Exception as e:
            logger.error(f"Ошибка валидации платежа: {e}")
            raise ValidationError(f"Некорректные данные платежа: {str(e)}", "E004")
    
    def validate_user_registration(self, data: Dict[str, Any]) -> UserRegistration:
        """Валидация регистрации пользователя"""
        try:
            return UserRegistration(**data)
        except Exception as e:
            logger.error(f"Ошибка валидации регистрации: {e}")
            raise ValidationError(f"Некорректные данные пользователя: {str(e)}", "E001")
    
    def validate_server_config(self, data: Dict[str, Any]) -> ServerConfig:
        """Валидация конфигурации сервера"""
        try:
            return ServerConfig(**data)
        except Exception as e:
            logger.error(f"Ошибка валидации сервера: {e}")
            raise ValidationError(f"Некорректная конфигурация сервера: {str(e)}", "E006")
    
    def validate_subscription_request(self, data: Dict[str, Any]) -> SubscriptionRequest:
        """Валидация запроса на подписку"""
        try:
            return SubscriptionRequest(**data)
        except Exception as e:
            logger.error(f"Ошибка валидации подписки: {e}")
            raise ValidationError(f"Некорректные данные подписки: {str(e)}", "E007")
    
    def validate_balance_operation(self, data: Dict[str, Any]) -> BalanceOperation:
        """Валидация операции с балансом"""
        try:
            return BalanceOperation(**data)
        except Exception as e:
            logger.error(f"Ошибка валидации баланса: {e}")
            raise ValidationError(f"Некорректные данные баланса: {str(e)}", "E002")
    
    def validate_referral_request(self, data: Dict[str, Any]) -> ReferralRequest:
        """Валидация реферального запроса"""
        try:
            return ReferralRequest(**data)
        except Exception as e:
            logger.error(f"Ошибка валидации реферала: {e}")
            raise ValidationError(f"Некорректные реферальные данные: {str(e)}", "E008")
    
    def sanitize_string(self, text: str, max_length: int = 1000) -> str:
        """Очистка строки от опасных символов"""
        if not text:
            return ""
        
        # Удаляем HTML теги
        text = re.sub(r'<[^>]+>', '', text)
        
        # Удаляем потенциально опасные символы
        text = re.sub(r'[<>"\']', '', text)
        
        # Ограничиваем длину
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text.strip()
    
    def validate_file_path(self, path: str) -> bool:
        """Валидация пути к файлу (защита от path traversal)"""
        if not path:
            return False
        
        # Проверяем на path traversal атаки
        dangerous_patterns = [
            r'\.\./',  # ../
            r'\.\.\\', # ..\
            r'/',      # абсолютный путь
            r'\\',     # Windows абсолютный путь
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, path):
                logger.warning(f"Попытка path traversal: {path}")
                return False
        
        return True
    
    def validate_callback_data(self, callback_data: str) -> bool:
        """Валидация callback data"""
        if not callback_data:
            return False
        
        # Проверяем длину
        if len(callback_data) > 64:
            return False
        
        # Проверяем на допустимые символы
        if not re.match(r'^[a-zA-Z0-9_\-]+$', callback_data):
            return False
        
        return True
    
    def validate_telegram_username(self, username: str) -> bool:
        """Валидация Telegram username"""
        if not username:
            return False
        
        # Удаляем @ если есть
        username = username.lstrip('@')
        
        # Проверяем формат
        if not re.match(r'^[a-zA-Z0-9_]{5,32}$', username):
            return False
        
        return True
    
    def validate_amount_range(self, amount: Union[int, float], 
                            min_amount: float = 0, 
                            max_amount: float = 100000) -> bool:
        """Валидация диапазона суммы"""
        try:
            amount = float(amount)
            return min_amount <= amount <= max_amount
        except (ValueError, TypeError):
            return False
    
    def get_validation_error_message(self, error: Exception) -> str:
        """Получить понятное сообщение об ошибке валидации"""
        if isinstance(error, ValidationError):
            return error.message
        
        # Обрабатываем pydantic ошибки
        if hasattr(error, 'errors'):
            error_messages = []
            for err in error.errors():
                field = err.get('loc', ['unknown'])[-1]
                message = err.get('msg', 'Invalid value')
                error_messages.append(f"{field}: {message}")
            return "; ".join(error_messages)
        
        return str(error)