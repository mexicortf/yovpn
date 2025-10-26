#!/usr/bin/env python3
"""
Сервис для микровзаимодействий и обратной связи
"""

import logging
import time
from typing import Optional, Dict, Any, List
from telebot import types

logger = logging.getLogger(__name__)

class InteractionService:
    """Сервис для микровзаимодействий и обратной связи"""
    
    def __init__(self, bot=None):
        self.bot = bot
        self.pending_actions = {}  # Хранение ожидающих действий
    
    def set_bot(self, bot):
        """Установить экземпляр бота"""
        self.bot = bot
    
    def answer_callback_query(self, callback_query_id: str, text: str = None, 
                            show_alert: bool = False, url: str = None) -> bool:
        """Ответить на callback query с улучшенной обратной связью"""
        if not self.bot:
            return False
        
        try:
            self.bot.answer_callback_query(
                callback_query_id=callback_query_id,
                text=text,
                show_alert=show_alert,
                url=url
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка ответа на callback query: {e}")
            return False
    
    def show_loading_feedback(self, callback_query_id: str, action: str = "Загрузка...") -> bool:
        """Показать обратную связь о загрузке"""
        return self.answer_callback_query(
            callback_query_id=callback_query_id,
            text=f"🔄 {action}",
            show_alert=False
        )
    
    def show_success_feedback(self, callback_query_id: str, message: str = "Готово!") -> bool:
        """Показать обратную связь об успехе"""
        return self.answer_callback_query(
            callback_query_id=callback_query_id,
            text=f"✅ {message}",
            show_alert=False
        )
    
    def show_error_feedback(self, callback_query_id: str, message: str = "Ошибка!") -> bool:
        """Показать обратную связь об ошибке"""
        return self.answer_callback_query(
            callback_query_id=callback_query_id,
            text=f"❌ {message}",
            show_alert=True
        )
    
    def show_warning_feedback(self, callback_query_id: str, message: str = "Внимание!") -> bool:
        """Показать обратную связь с предупреждением"""
        return self.answer_callback_query(
            callback_query_id=callback_query_id,
            text=f"⚠️ {message}",
            show_alert=True
        )
    
    def show_info_feedback(self, callback_query_id: str, message: str = "Информация") -> bool:
        """Показать информационную обратную связь"""
        return self.answer_callback_query(
            callback_query_id=callback_query_id,
            text=f"ℹ️ {message}",
            show_alert=False
        )
    
    def create_typing_indicator(self, chat_id: int, duration: float = 2.0) -> bool:
        """Показать индикатор печати"""
        if not self.bot:
            return False
        
        try:
            self.bot.send_chat_action(chat_id, 'typing')
            time.sleep(duration)
            return True
        except Exception as e:
            logger.error(f"Ошибка показа индикатора печати: {e}")
            return False
    
    def create_loading_message(self, chat_id: int, text: str, 
                             progress: int = 0, total: int = 100) -> Optional[int]:
        """Создать сообщение загрузки с прогрессом"""
        if not self.bot:
            return None
        
        try:
            # Создаем прогресс-бар
            if total > 0:
                percentage = int((progress / total) * 100)
                bar_length = 10
                filled = int((progress / total) * bar_length)
                empty = bar_length - filled
                
                progress_bar = "⬛" * filled + "⬜" * empty
                progress_text = f"\n\n{progress_bar} {percentage}%"
            else:
                progress_text = ""
            
            message_text = f"🔄 {text}{progress_text}"
            
            message = self.bot.send_message(
                chat_id=chat_id,
                text=message_text,
                parse_mode='HTML'
            )
            
            return message.message_id
            
        except Exception as e:
            logger.error(f"Ошибка создания сообщения загрузки: {e}")
            return None
    
    def update_loading_message(self, chat_id: int, message_id: int, text: str,
                              progress: int = 0, total: int = 100) -> bool:
        """Обновить сообщение загрузки"""
        if not self.bot:
            return False
        
        try:
            # Создаем прогресс-бар
            if total > 0:
                percentage = int((progress / total) * 100)
                bar_length = 10
                filled = int((progress / total) * bar_length)
                empty = bar_length - filled
                
                progress_bar = "⬛" * filled + "⬜" * empty
                progress_text = f"\n\n{progress_bar} {percentage}%"
            else:
                progress_text = ""
            
            message_text = f"🔄 {text}{progress_text}"
            
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=message_text,
                parse_mode='HTML'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления сообщения загрузки: {e}")
            return False
    
    def create_confirmation_dialog(self, chat_id: int, title: str, message: str,
                                 confirm_action: str, cancel_action: str = "cancel") -> bool:
        """Создать диалог подтверждения"""
        if not self.bot:
            return False
        
        try:
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            
            keyboard.add(
                types.InlineKeyboardButton(
                    "✅ Подтвердить", 
                    callback_data=f"confirm_{confirm_action}",
                    color_indicator="🟢"
                ),
                types.InlineKeyboardButton(
                    "❌ Отмена", 
                    callback_data=f"cancel_{cancel_action}",
                    color_indicator="🔴"
                )
            )
            
            self.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ <b>{title}</b>\n\n{message}",
                parse_mode='HTML',
                reply_markup=keyboard
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания диалога подтверждения: {e}")
            return False
    
    def create_success_animation(self, chat_id: int, message: str) -> bool:
        """Создать анимацию успеха"""
        if not self.bot:
            return False
        
        try:
            # Отправляем несколько сообщений для создания анимации
            messages = [
                "🎉",
                "🎊",
                "✨",
                f"✅ {message}"
            ]
            
            for i, msg in enumerate(messages):
                if i < len(messages) - 1:
                    self.bot.send_message(chat_id, msg)
                    time.sleep(0.5)
                else:
                    self.bot.send_message(chat_id, msg, parse_mode='HTML')
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания анимации успеха: {e}")
            return False
    
    def create_error_animation(self, chat_id: int, message: str) -> bool:
        """Создать анимацию ошибки"""
        if not self.bot:
            return False
        
        try:
            # Отправляем анимацию ошибки
            messages = [
                "❌",
                "⚠️",
                f"💥 {message}"
            ]
            
            for i, msg in enumerate(messages):
                if i < len(messages) - 1:
                    self.bot.send_message(chat_id, msg)
                    time.sleep(0.3)
                else:
                    self.bot.send_message(chat_id, msg, parse_mode='HTML')
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания анимации ошибки: {e}")
            return False
    
    def create_celebration_animation(self, chat_id: int, message: str) -> bool:
        """Создать праздничную анимацию"""
        if not self.bot:
            return False
        
        try:
            # Отправляем праздничную анимацию
            messages = [
                "🎉",
                "🎊",
                "✨",
                "🌟",
                "🎈",
                f"🎊 {message} 🎊"
            ]
            
            for i, msg in enumerate(messages):
                if i < len(messages) - 1:
                    self.bot.send_message(chat_id, msg)
                    time.sleep(0.4)
                else:
                    self.bot.send_message(chat_id, msg, parse_mode='HTML')
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания праздничной анимации: {e}")
            return False
    
    def create_loading_sequence(self, chat_id: int, steps: List[Dict[str, Any]], 
                               delay: float = 1.0) -> List[int]:
        """Создать последовательность загрузки"""
        if not self.bot:
            return []
        
        message_ids = []
        
        try:
            for i, step in enumerate(steps):
                # Создаем сообщение загрузки
                message_id = self.create_loading_message(
                    chat_id=chat_id,
                    text=step.get('text', 'Загрузка...'),
                    progress=step.get('progress', 0),
                    total=step.get('total', 100)
                )
                
                if message_id:
                    message_ids.append(message_id)
                
                # Задержка между шагами
                if i < len(steps) - 1:
                    time.sleep(delay)
            
            return message_ids
            
        except Exception as e:
            logger.error(f"Ошибка создания последовательности загрузки: {e}")
            return []
    
    def cleanup_messages(self, chat_id: int, message_ids: List[int]) -> bool:
        """Удалить сообщения (очистка после анимации)"""
        if not self.bot:
            return False
        
        try:
            for message_id in message_ids:
                try:
                    self.bot.delete_message(chat_id, message_id)
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение {message_id}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки сообщений: {e}")
            return False