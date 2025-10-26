"""
Упрощенный сервис безопасности (без cryptography)
"""

import re
import hashlib
import hmac
import secrets
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class SecurityService:
    """Упрощенный сервис безопасности"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self.sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'key["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'secret["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'api_key["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'access_token["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
            r'bearer["\']?\s*[:=]\s*["\']?([^"\'\s]+)',
        ]
        
        # Паттерны для маскирования
        self.mask_patterns = [
            (r'eyJ[A-Za-z0-9+/=]+', '***JWT_TOKEN***'),  # JWT токены
            (r'sk-[A-Za-z0-9]{48}', '***API_KEY***'),    # OpenAI API ключи
            (r'[A-Za-z0-9]{32,}', '***LONG_TOKEN***'),   # Длинные токены
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***'),  # Email
            (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '***.***.***.***'),  # IP адреса
        ]
        
        # Опасные команды для shell
        self.dangerous_commands = [
            'rm', 'del', 'format', 'fdisk', 'mkfs',
            'shutdown', 'reboot', 'halt', 'poweroff',
            'sudo', 'su', 'chmod', 'chown',
            'wget', 'curl', 'nc', 'netcat',
            'python', 'perl', 'ruby', 'node',
            'bash', 'sh', 'cmd', 'powershell'
        ]
        
        # Rate limiting
        self.rate_limits = {}
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 1000

    def mask_sensitive_data(self, text: str) -> str:
        """Маскировать чувствительные данные в тексте"""
        if not text:
            return text
        
        masked_text = text
        
        # Применяем паттерны маскирования
        for pattern, replacement in self.mask_patterns:
            masked_text = re.sub(pattern, replacement, masked_text, flags=re.IGNORECASE)
        
        # Маскируем данные из конфигурации
        for pattern in self.sensitive_patterns:
            masked_text = re.sub(pattern, r'\1=***MASKED***', masked_text, flags=re.IGNORECASE)
        
        return masked_text

    def sanitize_log_message(self, message: str) -> str:
        """Очистить сообщение лога от чувствительных данных"""
        if not message:
            return message
        
        # Маскируем чувствительные данные
        sanitized = self.mask_sensitive_data(message)
        
        # Удаляем потенциально опасные символы
        sanitized = re.sub(r'[<>"\']', '', sanitized)
        
        return sanitized

    def validate_input(self, input_data: str, input_type: str = "general") -> bool:
        """Валидация пользовательского ввода"""
        if not input_data:
            return False
        
        # Проверяем на SQL инъекции
        sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set',
            r'exec\s*\(',
            r'execute\s*\(',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                logger.warning(f"Обнаружена SQL инъекция: {input_data[:50]}...")
                return False
        
        # Проверяем на XSS
        xss_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                logger.warning(f"Обнаружена XSS атака: {input_data[:50]}...")
                return False
        
        # Проверяем на path traversal
        if '../' in input_data or '..\\' in input_data:
            logger.warning(f"Обнаружена path traversal атака: {input_data[:50]}...")
            return False
        
        # Проверяем на command injection
        for cmd in self.dangerous_commands:
            if cmd in input_data.lower():
                logger.warning(f"Обнаружена попытка выполнения команды: {cmd}")
                return False
        
        return True

    def validate_callback_data(self, callback_data: str) -> bool:
        """Валидация callback data от Telegram"""
        if not callback_data:
            return False
        
        # Проверяем длину
        if len(callback_data) > 64:
            return False
        
        # Проверяем на допустимые символы
        if not re.match(r'^[a-zA-Z0-9_\-]+$', callback_data):
            return False
        
        # Проверяем на подозрительные паттерны
        suspicious_patterns = [
            r'\.\.',
            r'<script',
            r'javascript:',
            r'eval\(',
            r'exec\(',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, callback_data, re.IGNORECASE):
                logger.warning(f"Подозрительный callback data: {callback_data}")
                return False
        
        return True

    def check_rate_limit(self, user_id: int, action: str = "general") -> bool:
        """Проверка rate limiting"""
        current_time = datetime.now()
        key = f"{user_id}:{action}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Очищаем старые записи
        minute_ago = current_time - timedelta(minutes=1)
        hour_ago = current_time - timedelta(hours=1)
        
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key]
            if timestamp > minute_ago
        ]
        
        # Проверяем лимиты
        requests_last_minute = len([
            t for t in self.rate_limits[key]
            if t > minute_ago
        ])
        
        requests_last_hour = len([
            t for t in self.rate_limits[key]
            if t > hour_ago
        ])
        
        if requests_last_minute >= self.max_requests_per_minute:
            logger.warning(f"Rate limit exceeded (minute): {user_id}")
            return False
        
        if requests_last_hour >= self.max_requests_per_hour:
            logger.warning(f"Rate limit exceeded (hour): {user_id}")
            return False
        
        # Добавляем текущий запрос
        self.rate_limits[key].append(current_time)
        return True

    def generate_secure_token(self, length: int = 32) -> str:
        """Генерация безопасного токена"""
        return secrets.token_urlsafe(length)

    def hash_password(self, password: str) -> str:
        """Хеширование пароля (упрощенная версия)"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return f"{salt}:{password_hash}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Проверка пароля (упрощенная версия)"""
        try:
            salt, hash_part = password_hash.split(':')
            password_hash_check = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
            return hmac.compare_digest(hash_part, password_hash_check)
        except Exception:
            return False

    def generate_hmac_signature(self, data: str) -> str:
        """Генерация HMAC подписи"""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def verify_hmac_signature(self, data: str, signature: str) -> bool:
        """Проверка HMAC подписи"""
        expected_signature = self.generate_hmac_signature(data)
        return hmac.compare_digest(signature, expected_signature)

    def sanitize_filename(self, filename: str) -> str:
        """Очистка имени файла"""
        if not filename:
            return "unnamed"
        
        # Удаляем опасные символы
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Ограничиваем длину
        if len(filename) > 255:
            filename = filename[:255]
        
        # Удаляем точки в начале и конце
        filename = filename.strip('.')
        
        return filename or "unnamed"

    def validate_json_input(self, json_data: str) -> bool:
        """Валидация JSON ввода"""
        try:
            data = json.loads(json_data)
            
            # Проверяем на циклические ссылки
            if self._has_circular_reference(data):
                return False
            
            # Проверяем глубину
            if self._get_depth(data) > 10:
                return False
            
            return True
        except json.JSONDecodeError:
            return False

    def _has_circular_reference(self, obj, visited=None):
        """Проверка на циклические ссылки"""
        if visited is None:
            visited = set()
        
        if id(obj) in visited:
            return True
        
        if isinstance(obj, dict):
            visited.add(id(obj))
            for value in obj.values():
                if self._has_circular_reference(value, visited):
                    return True
            visited.remove(id(obj))
        elif isinstance(obj, list):
            visited.add(id(obj))
            for item in obj:
                if self._has_circular_reference(item, visited):
                    return True
            visited.remove(id(obj))
        
        return False

    def _get_depth(self, obj, current_depth=0):
        """Получение глубины объекта"""
        if current_depth > 10:
            return current_depth
        
        if isinstance(obj, dict):
            return max(
                (self._get_depth(value, current_depth + 1) for value in obj.values()),
                default=current_depth
            )
        elif isinstance(obj, list):
            return max(
                (self._get_depth(item, current_depth + 1) for item in obj),
                default=current_depth
            )
        else:
            return current_depth

    def log_security_event(self, event_type: str, user_id: int, details: str = ""):
        """Логирование события безопасности"""
        sanitized_details = self.sanitize_log_message(details)
        
        logger.warning(
            f"SECURITY_EVENT: {event_type} | USER: {user_id} | "
            f"DETAILS: {sanitized_details} | TIME: {datetime.now().isoformat()}"
        )

    def check_suspicious_activity(self, user_id: int, action: str, data: str = "") -> bool:
        """Проверка подозрительной активности"""
        # Проверяем rate limiting
        if not self.check_rate_limit(user_id, action):
            self.log_security_event("RATE_LIMIT_EXCEEDED", user_id, f"Action: {action}")
            return False
        
        # Проверяем валидацию ввода
        if not self.validate_input(data, action):
            self.log_security_event("INVALID_INPUT", user_id, f"Action: {action}, Data: {data[:100]}")
            return False
        
        return True

    def get_security_headers(self) -> Dict[str, str]:
        """Получение заголовков безопасности"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }