"""
Сервис для улучшения пользовательского опыта
Включает немедленный отклик, прогресс-индикаторы, fallback для emoji
"""

import asyncio
import time
import logging
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum
import random

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    """Типы ответов пользователю"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    LOADING = "loading"

@dataclass
class ErrorCode:
    """Стандартизованная структура ошибок"""
    code: str
    message: str
    user_message: str
    action_required: str
    severity: str = "error"

class UXService:
    """Сервис для улучшения пользовательского опыта"""
    
    def __init__(self, bot=None):
        self.bot = bot
        self.typing_timeout = 5  # секунд
        self.progress_update_interval = 2  # секунд
        
        # Fallback emoji наборы
        self.emoji_fallbacks = {
            ResponseType.SUCCESS: ["🔥", "👍", "❤️", "🎉", "✅", "✨"],
            ResponseType.ERROR: ["❌", "⚠️", "🚫", "💥", "😞"],
            ResponseType.WARNING: ["⚠️", "🔶", "📢", "👀"],
            ResponseType.INFO: ["ℹ️", "📋", "💡", "🔍"],
            ResponseType.LOADING: ["⏳", "🔄", "⏰", "⏱️"]
        }
        
        # Стандартизованные коды ошибок
        self.error_codes = {
            "E001": ErrorCode(
                code="E001",
                message="User not found in database",
                user_message="Пользователь не найден. Попробуйте перезапустить бота командой /start",
                action_required="Restart bot with /start command"
            ),
            "E002": ErrorCode(
                code="E002", 
                message="Insufficient balance",
                user_message="Недостаточно средств на балансе. Пополните баланс для продолжения",
                action_required="Top up balance"
            ),
            "E003": ErrorCode(
                code="E003",
                message="Marzban API unavailable",
                user_message="Сервис временно недоступен. Попробуйте позже",
                action_required="Retry in a few minutes"
            ),
            "E004": ErrorCode(
                code="E004",
                message="Invalid payment amount",
                user_message="Некорректная сумма платежа. Выберите сумму из предложенных",
                action_required="Select valid amount"
            ),
            "E005": ErrorCode(
                code="E005",
                message="Sticker not found",
                user_message="Анимация недоступна, но операция выполнена",
                action_required="None"
            )
        }
        
        # Кэш для быстрого отклика
        self.response_cache = {}
        self.cache_ttl = 300  # 5 минут

    def get_random_emoji(self, response_type: ResponseType) -> str:
        """Получить случайный emoji для типа ответа"""
        emojis = self.emoji_fallbacks.get(response_type, ["📱"])
        return random.choice(emojis)
    
    @property
    def ResponseType(self):
        """Доступ к ResponseType enum"""
        return ResponseType

    async def send_immediate_ack(self, chat_id: int, callback_query_id: str = None, 
                               message: str = "Выполняю...") -> bool:
        """Немедленный отклик (0.1-0.3s)"""
        try:
            if callback_query_id:
                # Для callback query - быстрый ответ
                self.bot.answer_callback_query(
                    callback_query_id=callback_query_id,
                    text=message,
                    show_alert=False
                )
            
            # Показать typing indicator
            await self.show_typing_indicator(chat_id)
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки немедленного отклика: {e}")
            return False

    async def show_typing_indicator(self, chat_id: int) -> None:
        """Показать индикатор печати"""
        try:
            if self.bot:
                # Для синхронного бота используем send_chat_action
                self.bot.send_chat_action(chat_id, 'typing')
        except Exception as e:
            logger.error(f"Ошибка показа typing indicator: {e}")

    async def send_progress_update(self, chat_id: int, message_id: int, 
                                 progress: int, total: int, 
                                 current_step: str = "") -> bool:
        """Отправить обновление прогресса"""
        try:
            percentage = int((progress / total) * 100) if total > 0 else 0
            
            # Создаем прогресс-бар
            progress_bar = self.create_progress_bar(percentage)
            
            text = f"""
{self.get_random_emoji(ResponseType.LOADING)} <b>Выполняю операцию...</b>

{progress_bar} {percentage}%

📋 <b>Текущий этап:</b> {current_step}
⏱️ <b>Прогресс:</b> {progress}/{total}
"""
            
            if self.bot:
                self.bot.edit_message_text(
                    text=text,
                    chat_id=chat_id,
                    message_id=message_id,
                    parse_mode='HTML'
                )
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки прогресса: {e}")
            return False

    def create_progress_bar(self, percentage: int, length: int = 10) -> str:
        """Создать текстовый прогресс-бар"""
        filled = int((percentage / 100) * length)
        empty = length - filled
        
        bar = "█" * filled + "░" * empty
        return f"[{bar}]"

    async def send_success_response(self, chat_id: int, message_id: int = None,
                                  title: str = "Готово!", 
                                  details: str = "",
                                  show_log_button: bool = False) -> bool:
        """Отправить ответ об успехе"""
        try:
            emoji = self.get_random_emoji(ResponseType.SUCCESS)
            
            text = f"""
{emoji} <b>{title}</b>

{details}

✨ <i>Операция выполнена успешно</i>
"""
            
            if message_id and self.bot:
                # Редактируем существующее сообщение
                self.bot.edit_message_text(
                    text=text,
                    chat_id=chat_id,
                    message_id=message_id,
                    parse_mode='HTML'
                )
            elif self.bot:
                # Отправляем новое сообщение
                self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='HTML'
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки успешного ответа: {e}")
            return False

    async def send_error_response(self, chat_id: int, error_code: str,
                                message_id: int = None,
                                show_log_button: bool = True) -> bool:
        """Отправить ответ об ошибке"""
        try:
            error_info = self.error_codes.get(error_code)
            if not error_info:
                error_info = ErrorCode(
                    code="E999",
                    message="Unknown error",
                    user_message="Произошла неизвестная ошибка",
                    action_required="Contact support"
                )
            
            emoji = self.get_random_emoji(ResponseType.ERROR)
            
            text = f"""
{emoji} <b>Ошибка {error_info.code}</b>

{error_info.user_message}

🔧 <b>Что делать:</b> {error_info.action_required}
"""
            
            if show_log_button:
                text += "\n\n📋 Нажмите кнопку ниже для получения подробного лога"
            
            if message_id and self.bot:
                # Редактируем существующее сообщение
                self.bot.edit_message_text(
                    text=text,
                    chat_id=chat_id,
                    message_id=message_id,
                    parse_mode='HTML'
                )
            elif self.bot:
                # Отправляем новое сообщение
                self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='HTML'
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки ответа об ошибке: {e}")
            return False

    async def execute_with_progress(self, chat_id: int, operation: Callable,
                                  total_steps: int, operation_name: str = "Операция") -> Any:
        """Выполнить операцию с показом прогресса"""
        try:
            # Отправляем начальное сообщение
            initial_message = self.bot.send_message(
                chat_id=chat_id,
                text=f"{self.get_random_emoji(ResponseType.LOADING)} <b>Начинаю {operation_name.lower()}...</b>",
                parse_mode='HTML'
            )
            
            result = None
            for step in range(total_steps):
                # Обновляем прогресс
                await self.send_progress_update(
                    chat_id=chat_id,
                    message_id=initial_message.message_id,
                    progress=step + 1,
                    total=total_steps,
                    current_step=f"Шаг {step + 1} из {total_steps}"
                )
                
                # Небольшая задержка для демонстрации прогресса
                await asyncio.sleep(0.5)
            
            # Выполняем операцию
            result = await operation()
            
            # Показываем успешный результат
            await self.send_success_response(
                chat_id=chat_id,
                message_id=initial_message.message_id,
                title=f"{operation_name} завершена!",
                details="Все этапы выполнены успешно"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка выполнения операции с прогрессом: {e}")
            await self.send_error_response(
                chat_id=chat_id,
                error_code="E999",
                message_id=initial_message.message_id if 'initial_message' in locals() else None
            )
            raise

    def mask_sensitive_data(self, data: str) -> str:
        """Маскировать чувствительные данные в логах"""
        if not data:
            return data
            
        # Маскируем токены, пароли, ключи
        import re
        
        # Токены (длинные строки)
        data = re.sub(r'[A-Za-z0-9]{20,}', '***MASKED***', data)
        
        # Email адреса
        data = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', data)
        
        # IP адреса
        data = re.sub(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '***.***.***.***', data)
        
        return data

    def log_operation(self, operation: str, user_id: int, details: str = "", 
                     success: bool = True, error_code: str = None):
        """Логировать операцию с маскированием чувствительных данных"""
        masked_details = self.mask_sensitive_data(details)
        
        log_level = logging.INFO if success else logging.ERROR
        status = "SUCCESS" if success else "FAILED"
        
        logger.log(
            log_level,
            f"OPERATION: {operation} | USER: {user_id} | STATUS: {status} | "
            f"DETAILS: {masked_details} | ERROR_CODE: {error_code or 'N/A'}"
        )

    def get_cached_response(self, key: str) -> Optional[Any]:
        """Получить кэшированный ответ"""
        if key in self.response_cache:
            cached_data, timestamp = self.response_cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                del self.response_cache[key]
        return None

    def cache_response(self, key: str, data: Any) -> None:
        """Кэшировать ответ"""
        self.response_cache[key] = (data, time.time())

    async def handle_long_operation(self, chat_id: int, operation: Callable,
                                  operation_name: str = "Операция") -> Any:
        """Обработать долгую операцию с уведомлениями"""
        try:
            # Немедленный отклик
            await self.send_immediate_ack(chat_id, message="Начинаю выполнение...")
            
            # Выполняем операцию в фоне
            result = await operation()
            
            # Уведомляем об успехе
            await self.send_success_response(
                chat_id=chat_id,
                title=f"{operation_name} завершена!",
                details="Результат готов к использованию"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка в долгой операции: {e}")
            await self.send_error_response(chat_id, "E999")
            raise