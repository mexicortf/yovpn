#!/usr/bin/env python3
"""
Сервис для анимационных эффектов и стикеров
"""

import logging
import time
import asyncio
from typing import Optional, List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class AnimationType(Enum):
    """Типы анимаций"""
    LOADING = "loading"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PROGRESS = "progress"

class StickerService:
    """Сервис для работы со стикерами и анимациями"""
    
    def __init__(self, bot=None):
        self.bot = bot
        # Временно отключаем стикеры из-за неправильных ID
        # В реальной версии нужно использовать валидные ID стикеров
        self.stickers = {
            'loading': [],  # Пустой список - стикеры отключены
            'success': [],
            'error': [],
            'server': [],
            'security': [],
            'network': [],
            'celebration': []
        }
        
        # Эмодзи для прогресс-баров
        self.progress_emojis = {
            'empty': '⬜',
            'filled': '⬛',
            'half': '🟫'
        }
    
    def set_bot(self, bot):
        """Установить экземпляр бота"""
        self.bot = bot
    
    def get_sticker(self, category: str, index: int = 0) -> Optional[str]:
        """Получить стикер по категории"""
        if category in self.stickers and len(self.stickers[category]) > index:
            return self.stickers[category][index]
        return None
    
    def send_sticker(self, chat_id: int, category: str, index: int = 0) -> bool:
        """Отправить стикер"""
        if not self.bot:
            logger.warning("Бот не установлен, стикер не отправлен")
            return False
        
        sticker_id = self.get_sticker(category, index)
        if not sticker_id:
            # Если стикер не найден, отправляем эмодзи вместо стикера
            emoji_map = {
                'loading': '🔄',
                'success': '✅',
                'error': '❌',
                'server': '🖥️',
                'security': '🔐',
                'network': '🌐',
                'celebration': '🎉'
            }
            emoji = emoji_map.get(category, '📱')
            try:
                self.bot.send_message(chat_id, emoji)
                return True
            except Exception as e:
                logger.error(f"Ошибка отправки эмодзи: {e}")
                return False
        
        try:
            self.bot.send_sticker(chat_id, sticker_id)
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки стикера: {e}")
            return False
    
    def create_progress_bar(self, current: int, total: int, width: int = 10) -> str:
        """Создать прогресс-бар из эмодзи"""
        if total <= 0:
            return self.progress_emojis['empty'] * width
        
        filled = int((current / total) * width)
        empty = width - filled
        
        bar = self.progress_emojis['filled'] * filled + self.progress_emojis['empty'] * empty
        percentage = int((current / total) * 100)
        
        return f"{bar} {percentage}%"
    
    def create_loading_animation(self, chat_id: int, steps: List[Dict[str, Any]], 
                               delay: float = 1.0) -> List[int]:
        """Создать анимацию загрузки с несколькими шагами"""
        if not self.bot:
            logger.warning("Бот не установлен, анимация не создана")
            return []
        
        message_ids = []
        
        try:
            for i, step in enumerate(steps):
                # Отправляем стикер если указан
                if step.get('sticker'):
                    self.send_sticker(chat_id, step['sticker'])
                    time.sleep(0.5)
                
                # Отправляем текстовое сообщение
                text = step.get('text', '')
                if step.get('progress'):
                    progress = self.create_progress_bar(
                        step['progress']['current'], 
                        step['progress']['total']
                    )
                    text = f"{text}\n\n{progress}"
                
                message = self.bot.send_message(chat_id, text, parse_mode='HTML')
                message_ids.append(message.message_id)
                
                # Задержка между шагами
                if i < len(steps) - 1:  # Не ждем после последнего шага
                    time.sleep(delay)
            
            return message_ids
            
        except Exception as e:
            logger.error(f"Ошибка создания анимации загрузки: {e}")
            return []
    
    def animate_creation_process(self, chat_id: int, username: str) -> List[int]:
        """Анимировать процесс создания пользователя"""
        steps = [
            {
                'sticker': 'loading',
                'text': f"🔄 <b>Инициализация подключения</b>\n\n{self.create_progress_bar(1, 5)}"
            },
            {
                'sticker': 'server',
                'text': f"🖥️ <b>Готовим инфраструктуру</b>\n\nПодключаемся к серверам...\n{self.create_progress_bar(2, 5)}"
            },
            {
                'sticker': 'security',
                'text': f"🔐 <b>Настраиваем протокол</b>\n\nСоздаем безопасное соединение...\n{self.create_progress_bar(3, 5)}"
            },
            {
                'sticker': 'network',
                'text': f"🌐 <b>Генерируем ключи</b>\n\nСоздаем уникальные ключи доступа...\n{self.create_progress_bar(4, 5)}"
            },
            {
                'sticker': 'success',
                'text': f"✅ <b>Подключение готово!</b>\n\nПользователь @{username} успешно создан\n{self.create_progress_bar(5, 5)}"
            }
        ]
        
        return self.create_loading_animation(chat_id, steps, delay=1.5)
    
    def animate_payment_process(self, chat_id: int, amount: float) -> List[int]:
        """Анимировать процесс платежа"""
        steps = [
            {
                'sticker': 'loading',
                'text': f"💳 <b>Обработка платежа</b>\n\nСумма: {amount} ₽\n{self.create_progress_bar(1, 3)}"
            },
            {
                'sticker': 'security',
                'text': f"🔒 <b>Проверка безопасности</b>\n\nВалидация данных...\n{self.create_progress_bar(2, 3)}"
            },
            {
                'sticker': 'success',
                'text': f"✅ <b>Платеж успешен!</b>\n\nСредства зачислены на баланс\n{self.create_progress_bar(3, 3)}"
            }
        ]
        
        return self.create_loading_animation(chat_id, steps, delay=1.0)
    
    def animate_subscription_activation(self, chat_id: int, days: int) -> List[int]:
        """Анимировать активацию подписки"""
        steps = [
            {
                'sticker': 'loading',
                'text': f"🔄 <b>Активация подписки</b>\n\nПериод: {days} дней\n{self.create_progress_bar(1, 3)}"
            },
            {
                'sticker': 'network',
                'text': f"🌐 <b>Настройка доступа</b>\n\nПодключаем к VPN серверам...\n{self.create_progress_bar(2, 3)}"
            },
            {
                'sticker': 'celebration',
                'text': f"🎉 <b>Подписка активирована!</b>\n\nДоступ к VPN активен на {days} дней\n{self.create_progress_bar(3, 3)}"
            }
        ]
        
        return self.create_loading_animation(chat_id, steps, delay=1.2)
    
    def send_celebration(self, chat_id: int, message: str = "🎉 Поздравляем!") -> bool:
        """Отправить праздничное сообщение со стикерами"""
        if not self.bot:
            return False
        
        try:
            # Отправляем несколько праздничных стикеров
            for i in range(3):
                self.send_sticker(chat_id, 'celebration', i % 2)
                time.sleep(0.3)
            
            # Отправляем текстовое сообщение
            self.bot.send_message(chat_id, message, parse_mode='HTML')
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки празднования: {e}")
            return False
    
    def send_error_animation(self, chat_id: int, error_message: str) -> bool:
        """Отправить анимацию ошибки"""
        if not self.bot:
            return False
        
        try:
            # Отправляем стикер ошибки
            self.send_sticker(chat_id, 'error')
            
            # Отправляем сообщение об ошибке
            self.bot.send_message(
                chat_id, 
                f"❌ <b>Ошибка</b>\n\n{error_message}", 
                parse_mode='HTML'
            )
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки анимации ошибки: {e}")
            return False