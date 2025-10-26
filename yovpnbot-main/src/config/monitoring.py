"""
Конфигурация мониторинга и безопасности
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class MonitoringConfig:
    """Конфигурация мониторинга"""
    
    # Sentry
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.1
    
    # Prometheus
    prometheus_port: int = 8000
    prometheus_enabled: bool = True
    
    # Логирование
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: Optional[str] = None
    log_rotation: str = "daily"
    log_retention_days: int = 30
    
    # Rate limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 1000
    rate_limit_burst_size: int = 10
    
    # Безопасность
    max_request_size: int = 1024 * 1024  # 1MB
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    session_timeout: int = 3600  # 1 час
    
    # Уведомления
    admin_telegram_id: Optional[int] = None
    error_notification_enabled: bool = True
    security_alert_enabled: bool = True
    
    @classmethod
    def from_env(cls) -> 'MonitoringConfig':
        """Создать конфигурацию из переменных окружения"""
        return cls(
            sentry_dsn=os.getenv('SENTRY_DSN'),
            sentry_environment=os.getenv('SENTRY_ENVIRONMENT', 'development'),
            sentry_traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
            
            prometheus_port=int(os.getenv('PROMETHEUS_PORT', '8000')),
            prometheus_enabled=os.getenv('PROMETHEUS_ENABLED', 'true').lower() == 'true',
            
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_format=os.getenv('LOG_FORMAT', 'json'),
            log_file=os.getenv('LOG_FILE'),
            log_rotation=os.getenv('LOG_ROTATION', 'daily'),
            log_retention_days=int(os.getenv('LOG_RETENTION_DAYS', '30')),
            
            rate_limit_requests_per_minute=int(os.getenv('RATE_LIMIT_RPM', '60')),
            rate_limit_requests_per_hour=int(os.getenv('RATE_LIMIT_RPH', '1000')),
            rate_limit_burst_size=int(os.getenv('RATE_LIMIT_BURST', '10')),
            
            max_request_size=int(os.getenv('MAX_REQUEST_SIZE', str(1024 * 1024))),
            max_file_size=int(os.getenv('MAX_FILE_SIZE', str(10 * 1024 * 1024))),
            session_timeout=int(os.getenv('SESSION_TIMEOUT', '3600')),
            
            admin_telegram_id=int(os.getenv('ADMIN_TELEGRAM_ID')) if os.getenv('ADMIN_TELEGRAM_ID') else None,
            error_notification_enabled=os.getenv('ERROR_NOTIFICATION_ENABLED', 'true').lower() == 'true',
            security_alert_enabled=os.getenv('SECURITY_ALERT_ENABLED', 'true').lower() == 'true'
        )

@dataclass
class SecurityConfig:
    """Конфигурация безопасности"""
    
    # Секретные ключи
    secret_key: str
    jwt_secret: str
    encryption_key: str
    
    # CORS
    allowed_origins: list
    allowed_methods: list
    allowed_headers: list
    
    # CSRF
    csrf_secret: str
    csrf_timeout: int = 3600
    
    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    
    # Шифрование
    encryption_algorithm: str = "AES-256-GCM"
    
    # Валидация
    max_username_length: int = 32
    max_message_length: int = 4096
    max_callback_data_length: int = 64
    
    # Паттерны безопасности
    dangerous_patterns: list = None
    blocked_extensions: list = None
    
    def __post_init__(self):
        if self.dangerous_patterns is None:
            self.dangerous_patterns = [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'<iframe[^>]*>',
                r'<object[^>]*>',
                r'<embed[^>]*>',
                r'\.\./',
                r'\.\.\\',
                r'union\s+select',
                r'drop\s+table',
                r'delete\s+from',
                r'insert\s+into',
                r'update\s+set',
                r'exec\s*\(',
                r'eval\s*\('
            ]
        
        if self.blocked_extensions is None:
            self.blocked_extensions = [
                '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
                '.vbs', '.js', '.jar', '.sh', '.ps1', '.py'
            ]
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Создать конфигурацию из переменных окружения"""
        import secrets
        
        return cls(
            secret_key=os.getenv('SECRET_KEY', secrets.token_hex(32)),
            jwt_secret=os.getenv('JWT_SECRET', secrets.token_hex(32)),
            encryption_key=os.getenv('ENCRYPTION_KEY', secrets.token_hex(32)),
            
            allowed_origins=os.getenv('ALLOWED_ORIGINS', '*').split(','),
            allowed_methods=os.getenv('ALLOWED_METHODS', 'GET,POST,PUT,DELETE').split(','),
            allowed_headers=os.getenv('ALLOWED_HEADERS', 'Content-Type,Authorization').split(','),
            
            csrf_secret=os.getenv('CSRF_SECRET', secrets.token_hex(32)),
            csrf_timeout=int(os.getenv('CSRF_TIMEOUT', '3600')),
            
            jwt_algorithm=os.getenv('JWT_ALGORITHM', 'HS256'),
            jwt_expiration=int(os.getenv('JWT_EXPIRATION', '3600')),
            
            encryption_algorithm=os.getenv('ENCRYPTION_ALGORITHM', 'AES-256-GCM'),
            
            max_username_length=int(os.getenv('MAX_USERNAME_LENGTH', '32')),
            max_message_length=int(os.getenv('MAX_MESSAGE_LENGTH', '4096')),
            max_callback_data_length=int(os.getenv('MAX_CALLBACK_DATA_LENGTH', '64'))
        )

def setup_logging(config: MonitoringConfig) -> None:
    """Настройка логирования"""
    import structlog
    from structlog.stdlib import LoggerFactory
    
    # Настройка structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Настройка уровня логирования
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def setup_sentry(config: MonitoringConfig) -> None:
    """Настройка Sentry"""
    if config.sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        
        sentry_sdk.init(
            dsn=config.sentry_dsn,
            environment=config.sentry_environment,
            traces_sample_rate=config.sentry_traces_sample_rate,
            integrations=[
                sentry_logging,
                RedisIntegration(),
                SqlalchemyIntegration()
            ],
            send_default_pii=False,  # Не отправлять персональные данные
            max_breadcrumbs=50,
            attach_stacktrace=True,
            release=os.getenv('RELEASE_VERSION', 'unknown')
        )

def setup_prometheus(config: MonitoringConfig) -> Optional[Any]:
    """Настройка Prometheus метрик"""
    if not config.prometheus_enabled:
        return None
    
    try:
        from prometheus_client import start_http_server, Counter, Histogram, Gauge
        
        # Метрики
        request_count = Counter(
            'bot_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status']
        )
        
        request_duration = Histogram(
            'bot_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint']
        )
        
        active_users = Gauge(
            'bot_active_users',
            'Number of active users'
        )
        
        error_count = Counter(
            'bot_errors_total',
            'Total number of errors',
            ['error_type', 'error_code']
        )
        
        # Запуск HTTP сервера для метрик
        start_http_server(config.prometheus_port)
        
        return {
            'request_count': request_count,
            'request_duration': request_duration,
            'active_users': active_users,
            'error_count': error_count
        }
        
    except ImportError:
        logging.warning("Prometheus client не установлен, метрики отключены")
        return None