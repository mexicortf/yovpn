#!/usr/bin/env python3
"""
Сервис для копирования ссылок и генерации QR-кодов
"""

import logging
import qrcode
from io import BytesIO
from typing import Optional, Dict, Any
from telebot import types

logger = logging.getLogger(__name__)

class CopyService:
    """Сервис для работы с копированием и QR-кодами"""
    
    def __init__(self, bot=None):
        self.bot = bot
        self.qr_cache = {}  # Кэш для QR-кодов
    
    def set_bot(self, bot):
        """Установить экземпляр бота"""
        self.bot = bot
    
    def generate_qr_code(self, data: str, size: int = 10, border: int = 4) -> Optional[BytesIO]:
        """Генерировать QR-код для данных"""
        try:
            # Проверяем кэш
            cache_key = f"{data}_{size}_{border}"
            if cache_key in self.qr_cache:
                return self.qr_cache[cache_key]
            
            # Создаем QR-код
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Создаем изображение
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Сохраняем в BytesIO
            bio = BytesIO()
            img.save(bio, format='PNG')
            bio.seek(0)
            
            # Кэшируем
            self.qr_cache[cache_key] = bio
            
            return bio
            
        except Exception as e:
            logger.error(f"Ошибка генерации QR-кода: {e}")
            return None
    
    def send_qr_code(self, chat_id: int, data: str, caption: str = "QR-код") -> bool:
        """Отправить QR-код пользователю"""
        if not self.bot:
            logger.warning("Бот не установлен, QR-код не отправлен")
            return False
        
        try:
            qr_bio = self.generate_qr_code(data)
            if not qr_bio:
                return False
            
            # Отправляем QR-код как фото
            self.bot.send_photo(
                chat_id=chat_id,
                photo=qr_bio,
                caption=caption,
                parse_mode='HTML'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки QR-кода: {e}")
            return False
    
    def send_copyable_text(self, chat_id: int, text: str, title: str = "Скопируйте текст") -> bool:
        """Отправить текст для копирования"""
        if not self.bot:
            logger.warning("Бот не установлен, текст не отправлен")
            return False
        
        try:
            # Отправляем текст в отдельном сообщении для легкого копирования
            message = f"""
📋 <b>{title}</b>

<code>{text}</code>

💡 <i>Нажмите на текст выше, чтобы скопировать его</i>
"""
            
            self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки копируемого текста: {e}")
            return False
    
    def create_copy_keyboard(self, text: str, copy_type: str, 
                           show_qr: bool = True) -> types.InlineKeyboardMarkup:
        """Создать клавиатуру для копирования"""
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        
        # Кнопка копирования
        keyboard.add(
            types.InlineKeyboardButton(
                "📋 Скопировать текст", 
                callback_data=f"copy_text_{copy_type}"
            )
        )
        
        # Кнопка QR-кода (если нужна)
        if show_qr:
            keyboard.add(
                types.InlineKeyboardButton(
                    "📱 Показать QR-код", 
                    callback_data=f"show_qr_{copy_type}"
                )
            )
        
        # Кнопка назад
        keyboard.add(
            types.InlineKeyboardButton(
                "⬅️ Назад", 
                callback_data="back_to_previous"
            )
        )
        
        return keyboard
    
    def handle_copy_request(self, chat_id: int, text: str, copy_type: str) -> bool:
        """Обработать запрос на копирование"""
        try:
            if copy_type == "text":
                return self.send_copyable_text(chat_id, text, "Скопируйте текст")
            elif copy_type == "vless":
                return self.send_copyable_text(chat_id, text, "VLESS ссылка")
            elif copy_type == "subscription":
                return self.send_copyable_text(chat_id, text, "Subscription URL")
            elif copy_type == "referral":
                return self.send_copyable_text(chat_id, text, "Реферальная ссылка")
            else:
                return self.send_copyable_text(chat_id, text, "Скопируйте данные")
                
        except Exception as e:
            logger.error(f"Ошибка обработки запроса на копирование: {e}")
            return False
    
    def handle_qr_request(self, chat_id: int, data: str, qr_type: str) -> bool:
        """Обработать запрос на QR-код"""
        try:
            if qr_type == "vless":
                caption = "📱 <b>QR-код VLESS ссылки</b>\n\nОтсканируйте для быстрой настройки"
            elif qr_type == "subscription":
                caption = "📱 <b>QR-код Subscription URL</b>\n\nОтсканируйте для подписки"
            elif qr_type == "referral":
                caption = "📱 <b>QR-код реферальной ссылки</b>\n\nПоделитесь с друзьями"
            else:
                caption = "📱 <b>QR-код</b>\n\nОтсканируйте для использования"
            
            return self.send_qr_code(chat_id, data, caption)
            
        except Exception as e:
            logger.error(f"Ошибка обработки запроса на QR-код: {e}")
            return False
    
    def create_vless_copy_interface(self, chat_id: int, vless_link: str, 
                                  subscription_url: str = None) -> bool:
        """Создать интерфейс для копирования VLESS ссылок"""
        if not self.bot:
            return False
        
        try:
            # Отправляем VLESS ссылку
            self.send_copyable_text(chat_id, vless_link, "VLESS ссылка")
            
            # Создаем клавиатуру
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            
            keyboard.add(
                types.InlineKeyboardButton("📋 VLESS", callback_data="copy_vless"),
                types.InlineKeyboardButton("📱 QR VLESS", callback_data="qr_vless")
            )
            
            if subscription_url:
                keyboard.add(
                    types.InlineKeyboardButton("📋 Subscription", callback_data="copy_subscription"),
                    types.InlineKeyboardButton("📱 QR Subscription", callback_data="qr_subscription")
                )
            
            keyboard.add(
                types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_subscription")
            )
            
            # Отправляем клавиатуру
            self.bot.send_message(
                chat_id=chat_id,
                text="🔗 <b>Выберите действие с ссылками</b>",
                parse_mode='HTML',
                reply_markup=keyboard
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания интерфейса копирования: {e}")
            return False
    
    def create_referral_copy_interface(self, chat_id: int, referral_link: str) -> bool:
        """Создать интерфейс для копирования реферальной ссылки"""
        if not self.bot:
            return False
        
        try:
            # Отправляем реферальную ссылку
            self.send_copyable_text(chat_id, referral_link, "Реферальная ссылка")
            
            # Создаем клавиатуру
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            
            keyboard.add(
                types.InlineKeyboardButton("📋 Скопировать", callback_data="copy_referral"),
                types.InlineKeyboardButton("📱 QR-код", callback_data="qr_referral")
            )
            
            keyboard.add(
                types.InlineKeyboardButton("📤 Поделиться", callback_data="share_referral"),
                types.InlineKeyboardButton("📊 Статистика", callback_data="referral_stats")
            )
            
            keyboard.add(
                types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
            )
            
            # Отправляем клавиатуру
            self.bot.send_message(
                chat_id=chat_id,
                text="👥 <b>Реферальная ссылка</b>\n\nВыберите действие:",
                parse_mode='HTML',
                reply_markup=keyboard
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания интерфейса реферальной ссылки: {e}")
            return False