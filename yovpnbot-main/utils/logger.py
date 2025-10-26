"""
Logger Utility
Настройка логирования для приложения
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import os


class ColoredFormatter(logging.Formatter):
    """Цветной форматтер для консоли"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(
    name: str = "yovpn",
    level: str = "INFO",
    log_to_file: bool = False,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Настроить логгер
    
    Args:
        name: Имя логгера
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Писать ли логи в файл
        log_file: Путь к файлу логов
    
    Returns:
        Настроенный логгер
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()
    
    # Формат логов
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Консольный handler с цветами
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Файловый handler
    if log_to_file:
        if not log_file:
            # Создаем директорию для логов
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Генерируем имя файла с датой
            log_file = logs_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"📝 Logging to file: {log_file}")
    
    return logger


def get_logger(name: str = "yovpn") -> logging.Logger:
    """
    Получить логгер
    
    Args:
        name: Имя логгера
    
    Returns:
        Логгер
    """
    return logging.getLogger(name)


# Настраиваем главный логгер при импорте
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "0") == "1"
LOG_FILE = os.getenv("LOG_FILE")

main_logger = setup_logger(
    name="yovpn",
    level=LOG_LEVEL,
    log_to_file=LOG_TO_FILE,
    log_file=LOG_FILE
)


if __name__ == "__main__":
    # Тест логгера
    logger = get_logger()
    
    logger.debug("🐛 Debug message")
    logger.info("ℹ️ Info message")
    logger.warning("⚠️ Warning message")
    logger.error("❌ Error message")
    logger.critical("🚨 Critical message")
