"""
Упрощенный сервис валидации входных данных (без pydantic)
"""

import re
import logging
from typing import Optional, Union, List, Dict, Any

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Исключение валидации"""
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ValidationService:
    """Упрощенный сервис валидации входных данных"""
    
    def __init__(self):
        self.validation_rules = {
            'username': r'^[a-zA-Z0-9_]{1,32}$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'ip_address': r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
            'port': r'^(?:[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$',
            'user_id': r'^[1-9][0-9]*$',
            'amount': r'^[0-9]+(\.[0-9]{1,2})?$'
        }
    
    def validate_payment_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация запроса на платеж"""
        try:
            amount = data.get('amount', 0)
            payment_method = data.get('payment_method', '')
            user_id = data.get('user_id', 0)
            
            # Валидация суммы
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise ValidationError("Сумма должна быть положительным числом", "E004")
            
            if amount < 4:
                raise ValidationError("Минимальная сумма платежа: 4 рубля", "E004")
            
            if amount % 4 != 0:
                raise ValidationError("Сумма должна быть кратна 4 рублям (стоимость дня)", "E004")
            
            # Валидация способа оплаты
            valid_methods = ['card', 'sbp', 'bank', 'wallet']
            if payment_method not in valid_methods:
                raise ValidationError(f"Некорректный способ оплаты. Доступные: {', '.join(valid_methods)}", "E004")
            
            # Валидация ID пользователя
            if not isinstance(user_id, int) or user_id <= 0:
                raise ValidationError("ID пользователя должен быть положительным числом", "E004")
            
            return {
                'amount': int(amount),
                'payment_method': payment_method,
                'user_id': user_id,
                'currency': data.get('currency', 'RUB')
            }
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Ошибка валидации платежа: {e}")
            raise ValidationError(f"Некорректные данные платежа: {str(e)}", "E004")
    
    def validate_user_registration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация регистрации пользователя"""
        try:
            user_id = data.get('user_id', 0)
            username = data.get('username')
            first_name = data.get('first_name')
            
            # Валидация ID пользователя
            if not isinstance(user_id, int) or user_id <= 0:
                raise ValidationError("ID пользователя должен быть положительным числом", "E001")
            
            # Валидация имени пользователя
            if username is not None:
                username = username.lstrip('@')
                if not re.match(r'^[a-zA-Z0-9_]{1,32}$', username):
                    raise ValidationError("Имя пользователя может содержать только буквы, цифры и подчеркивания", "E001")
            
            # Валидация имен
            if first_name is not None:
                first_name = re.sub(r'[<>"\']', '', first_name)
                if len(first_name.strip()) == 0:
                    first_name = None
            
            return {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'language_code': data.get('language_code', 'ru')
            }
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Ошибка валидации регистрации: {e}")
            raise ValidationError(f"Некорректные данные пользователя: {str(e)}", "E001")
    
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
        
        return str(error)