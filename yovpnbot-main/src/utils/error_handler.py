#!/usr/bin/env python3
"""
Централизованный обработчик ошибок
"""

import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps
import telebot
from telebot import types

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Централизованный обработчик ошибок"""
    
    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.admin_chat_id = None  # ID чата администратора для уведомлений
    
    def set_admin_chat_id(self, chat_id: int):
        """Установить ID чата администратора для уведомлений об ошибках"""
        self.admin_chat_id = chat_id
    
    def handle_error(self, error: Exception, context: str = "", user_id: Optional[int] = None):
        """Обработка ошибки с логированием и уведомлением"""
        error_msg = f"Ошибка в {context}: {str(error)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Отправляем уведомление администратору
        if self.admin_chat_id:
            try:
                admin_message = f"🚨 <b>Ошибка в боте</b>\n\n"
                admin_message += f"<b>Контекст:</b> {context}\n"
                admin_message += f"<b>Ошибка:</b> {str(error)}\n"
                if user_id:
                    admin_message += f"<b>Пользователь:</b> {user_id}\n"
                admin_message += f"<b>Время:</b> {traceback.format_exc()}"
                
                self.bot.send_message(
                    self.admin_chat_id,
                    admin_message,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление администратору: {e}")
    
    def send_user_error(self, chat_id: int, error_type: str = "general"):
        """Отправка понятного сообщения об ошибке пользователю"""
        error_messages = {
            "general": "❌ Произошла ошибка. Попробуйте позже или обратитесь в поддержку.",
            "api": "⚠️ Сервис временно недоступен. Попробуйте через несколько минут.",
            "network": "🌐 Проблемы с сетью. Проверьте подключение к интернету.",
            "auth": "🔐 Ошибка авторизации. Обратитесь к администратору.",
            "data": "📊 Ошибка обработки данных. Попробуйте еще раз.",
            "marzban": "🔧 Проблема с VPN сервисом. Обратитесь в поддержку."
        }
        
        message = error_messages.get(error_type, error_messages["general"])
        
        try:
            self.bot.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение об ошибке пользователю: {e}")
    
    def error_decorator(self, context: str = "", user_friendly_error: str = "general"):
        """Декоратор для обработки ошибок в функциях"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Определяем user_id если возможно
                    user_id = None
                    if args and hasattr(args[0], 'from_user'):
                        user_id = args[0].from_user.id
                    elif args and hasattr(args[0], 'chat'):
                        user_id = args[0].chat.id
                    
                    # Обрабатываем ошибку
                    self.handle_error(e, context, user_id)
                    
                    # Отправляем понятное сообщение пользователю
                    if user_id:
                        self.send_user_error(user_id, user_friendly_error)
                    
                    return None
            return wrapper
        return decorator
    
    def handle_marzban_error(self, error: Exception, username: str, user_id: Optional[int] = None):
        """Специальная обработка ошибок Marzban API"""
        error_msg = f"Ошибка Marzban API для пользователя {username}: {str(error)}"
        logger.error(error_msg)
        
        # Определяем тип ошибки
        if "SSL" in str(error) or "certificate" in str(error).lower():
            error_type = "ssl"
        elif "timeout" in str(error).lower():
            error_type = "timeout"
        elif "connection" in str(error).lower():
            error_type = "connection"
        else:
            error_type = "marzban"
        
        # Логируем с контекстом
        self.handle_error(error, f"Marzban API (user: {username})", user_id)
        
        # Отправляем уведомление администратору
        if self.admin_chat_id:
            try:
                admin_message = f"🔧 <b>Ошибка Marzban API</b>\n\n"
                admin_message += f"<b>Пользователь:</b> {username} (ID: {user_id})\n"
                admin_message += f"<b>Тип ошибки:</b> {error_type}\n"
                admin_message += f"<b>Ошибка:</b> {str(error)}"
                
                self.bot.send_message(
                    self.admin_chat_id,
                    admin_message,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление об ошибке Marzban: {e}")
    
    def handle_user_data_error(self, error: Exception, user_id: int, operation: str):
        """Обработка ошибок работы с данными пользователя"""
        error_msg = f"Ошибка данных пользователя {user_id} при {operation}: {str(error)}"
        logger.error(error_msg)
        
        self.handle_error(error, f"User Data ({operation})", user_id)
        
        # Отправляем уведомление пользователю
        self.send_user_error(user_id, "data")

# Глобальный обработчик ошибок (будет инициализирован в main)
error_handler: Optional[ErrorHandler] = None

def get_error_handler() -> ErrorHandler:
    """Получить глобальный обработчик ошибок"""
    global error_handler
    if error_handler is None:
        raise RuntimeError("ErrorHandler не инициализирован")
    return error_handler

def init_error_handler(bot: telebot.TeleBot, admin_chat_id: Optional[int] = None):
    """Инициализация глобального обработчика ошибок"""
    global error_handler
    error_handler = ErrorHandler(bot)
    if admin_chat_id:
        error_handler.set_admin_chat_id(admin_chat_id)