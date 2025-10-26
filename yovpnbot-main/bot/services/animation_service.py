"""
Сервис анимаций и эффектов
Управление анимированными эффектами сообщений и стикерами
"""

import logging
from typing import Optional, Dict, Any
from aiogram import Bot
from aiogram.types import Message

from assets.animations.effects import MESSAGE_EFFECTS, get_effect_id, get_usage_example, get_fallback_emoji

logger = logging.getLogger(__name__)

class AnimationService:
    """
    Сервис для работы с анимациями и эффектами
    
    Отвечает за:
    - Отправку сообщений с анимированными эффектами
    - Управление стикерами и GIF
    - Создание прогресс-баров
    - Fallback на эмодзи при ошибках
    """
    
    def __init__(self, bot: Bot):
        """
        Инициализация сервиса
        
        Args:
            bot: Экземпляр бота
        """
        self.bot = bot
        self.stickers = {
            'loading': [],
            'success': [],
            'error': [],
            'server': [],
            'security': [],
            'network': [],
            'celebration': []
        }
        
        logger.info("✅ AnimationService инициализирован")
    
    async def show_loading_animation(self, message: Message) -> None:
        """
        Показать современную анимацию загрузки с прогресс-баром
        Стиль: система подключается к серверам
        
        Args:
            message: Сообщение для редактирования
        """
        import asyncio
        
        steps = [
            {"text": "🔄 <b>Инициализация системы...</b>", "delay": 0.8},
            {"text": "🔐 <b>Настройка шифрования...</b>\n\n███▒▒▒▒▒▒▒ 30%", "delay": 0.9},
            {"text": "🌐 <b>Подключение к серверам...</b>\n\n██████▒▒▒▒ 60%", "delay": 0.9},
            {"text": "🛡️ <b>Активация защиты...</b>\n\n█████████▒ 90%", "delay": 0.8},
            {"text": "✅ <b>Система готова к работе!</b>\n\n██████████ 100%", "delay": 1.0}
        ]
        
        loading_msg = await message.answer(steps[0]["text"], parse_mode='HTML')
        
        for i, step in enumerate(steps[1:], 1):
            await asyncio.sleep(steps[i-1]["delay"])
            try:
                await loading_msg.edit_text(step["text"], parse_mode='HTML')
            except Exception as e:
                logger.debug(f"Ошибка редактирования анимации: {e}")
        
        await asyncio.sleep(steps[-1]["delay"])
        await loading_msg.delete()
    
    async def send_welcome_message(self, message: Message, user_name: str, balance: float = 0.0, subscription_days: int = 0, is_new: bool = False) -> Message:
        """
        Отправить приветственное сообщение с эффектом
        Использует централизованную систему текстов
        
        Args:
            message: Сообщение для ответа
            user_name: Имя пользователя
            balance: Баланс пользователя
            subscription_days: Дни доступа
            is_new: Новый ли пользователь
        
        Returns:
            Message: Отправленное сообщение
        """
        try:
            from bot.utils.texts import get_welcome_text, get_new_user_welcome_text
            from bot.keyboards.menu_kb import MenuKeyboards
            
            if is_new:
                welcome_text = get_new_user_welcome_text(user_name)
            else:
                welcome_text = get_welcome_text(user_name, balance, subscription_days)
            
            return await self.reply_with_effect(
                message,
                welcome_text,
                'heart',
                reply_markup=MenuKeyboards.get_main_menu(),
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Ошибка отправки приветствия: {e}")
            # Fallback на старый текст
            welcome_text = f"<b>✨ Привет, {user_name}!</b>\n\nДобро пожаловать в YoVPN!"
            return await message.reply(welcome_text, parse_mode='HTML')
    
    async def send_subscription_activated(self, message: Message, days: int) -> Message:
        """
        Отправить сообщение об активации подписки
        
        Args:
            message: Сообщение для ответа
            days: Количество дней подписки
        
        Returns:
            Message: Отправленное сообщение
        """
        activation_text = f"""
🎉 <b>Подписка активирована!</b>

✅ <b>Статус:</b> Активна
📅 <b>Срок:</b> {days} дней
💰 <b>Стоимость:</b> 4 ₽ в день
🔄 <b>Продление:</b> Автоматическое

<b>Следующие шаги:</b>
1. 📱 Настройте VPN на устройстве
2. 🔗 Скопируйте конфигурацию
3. 🚀 Наслаждайтесь безопасным интернетом!

<b>Нужна помощь?</b> Обратитесь в поддержку 👇
        """
        
        return await self.reply_with_effect(
            message,
            activation_text,
            'fire',
            reply_markup=self._get_subscription_menu_keyboard(),
            parse_mode='HTML'
        )
    
    async def send_payment_success(self, message: Message, amount: float, days: int) -> Message:
        """
        Отправить сообщение об успешной оплате
        
        Args:
            message: Сообщение для ответа
            amount: Сумма оплаты
            days: Количество дней
        
        Returns:
            Message: Отправленное сообщение
        """
        payment_text = f"""
💰 <b>Платеж успешно обработан!</b>

✅ <b>Сумма:</b> {amount:.2f} ₽
📅 <b>Добавлено дней:</b> {days}
💳 <b>Статус:</b> Подтвержден
🔄 <b>Обновление:</b> Мгновенное

<b>Ваш баланс пополнен!</b>
Теперь вы можете активировать подписку или продолжить использование VPN.

<b>Что дальше?</b> Выберите действие 👇
        """
        
        return await self.reply_with_effect(
            message,
            payment_text,
            'confetti',
            reply_markup=self._get_payment_success_keyboard(),
            parse_mode='HTML'
        )
    
    async def send_loading_message(self, message: Message, text: str) -> Message:
        """
        Отправить сообщение загрузки с эффектом
        
        Args:
            message: Сообщение для ответа
            text: Текст сообщения
        
        Returns:
            Message: Отправленное сообщение
        """
        return await self.reply_with_effect(
            message,
            text,
            'loading',
            parse_mode='HTML'
        )
    
    async def send_error_message(self, message: Message, error_text: str, is_critical: bool = False) -> Message:
        """
        Отправить сообщение об ошибке
        
        Args:
            message: Сообщение для ответа
            error_text: Текст ошибки
            is_critical: Критическая ли ошибка
        
        Returns:
            Message: Отправленное сообщение
        """
        effect = 'poop' if is_critical else 'thumbs_down'
        
        return await self.reply_with_effect(
            message,
            error_text,
            effect,
            parse_mode='HTML'
        )
    
    async def reply_with_effect(self, message: Message, text: str, effect_name: str, **kwargs) -> Message:
        """
        Ответить на сообщение с анимированным эффектом
        
        Args:
            message: Сообщение для ответа
            text: Текст ответа
            effect_name: Название эффекта
            **kwargs: Дополнительные параметры
        
        Returns:
            Message: Отправленное сообщение
        """
        # Устанавливаем parse_mode по умолчанию, если не указан
        if 'parse_mode' not in kwargs:
            kwargs['parse_mode'] = 'HTML'
        
        try:
            effect_id = get_effect_id(effect_name)
            
            if effect_id:
                # Сначала пробуем отправить с эффектом
                try:
                    kwargs_with_effect = kwargs.copy()
                    kwargs_with_effect['message_effect_id'] = effect_id
                    return await message.reply(text, **kwargs_with_effect)
                except Exception as effect_error:
                    # Если эффект не работает, добавляем fallback эмодзи и отправляем без эффекта
                    fallback_emoji = get_fallback_emoji(effect_name)
                    enhanced_text = f"{fallback_emoji} {text}" if fallback_emoji else text
                    logger.debug(f"Эффект '{effect_name}' недоступен, используем fallback эмодзи")
                    return await message.reply(enhanced_text, **kwargs)
            else:
                # Если эффект не найден, добавляем fallback эмодзи
                fallback_emoji = get_fallback_emoji(effect_name)
                enhanced_text = f"{fallback_emoji} {text}" if fallback_emoji else text
                logger.debug(f"Эффект '{effect_name}' не найден, используем fallback эмодзи")
                return await message.reply(enhanced_text, **kwargs)
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения с эффектом: {e}")
            # Fallback на обычное сообщение
            return await message.reply(text, **kwargs)
    
    async def send_message_with_effect(self, chat_id: int, text: str, effect_name: str, **kwargs) -> Message:
        """
        Отправить сообщение с анимированным эффектом
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
            effect_name: Название эффекта
            **kwargs: Дополнительные параметры
        
        Returns:
            Message: Отправленное сообщение
        """
        # Устанавливаем parse_mode по умолчанию, если не указан
        if 'parse_mode' not in kwargs:
            kwargs['parse_mode'] = 'HTML'
        
        try:
            effect_id = get_effect_id(effect_name)
            
            if effect_id:
                # Сначала пробуем отправить с эффектом
                try:
                    kwargs_with_effect = kwargs.copy()
                    kwargs_with_effect['message_effect_id'] = effect_id
                    return await self.bot.send_message(chat_id, text, **kwargs_with_effect)
                except Exception as effect_error:
                    # Если эффект не работает, добавляем fallback эмодзи и отправляем без эффекта
                    fallback_emoji = get_fallback_emoji(effect_name)
                    enhanced_text = f"{fallback_emoji} {text}" if fallback_emoji else text
                    logger.debug(f"Эффект '{effect_name}' недоступен, используем fallback эмодзи")
                    return await self.bot.send_message(chat_id, enhanced_text, **kwargs)
            else:
                # Если эффект не найден, добавляем fallback эмодзи
                fallback_emoji = get_fallback_emoji(effect_name)
                enhanced_text = f"{fallback_emoji} {text}" if fallback_emoji else text
                logger.debug(f"Эффект '{effect_name}' не найден, используем fallback эмодзи")
                return await self.bot.send_message(chat_id, enhanced_text, **kwargs)
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения с эффектом: {e}")
            # Fallback на обычное сообщение
            return await self.bot.send_message(chat_id, text, **kwargs)
    
    def _get_main_menu_keyboard(self):
        """Получить клавиатуру главного меню"""
        try:
            from bot.keyboards.menu_kb import MenuKeyboards
            return MenuKeyboards.get_main_menu()
        except Exception:
            # Fallback на встроенную клавиатуру
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            return InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="📱 Мои подписки", callback_data="my_subscriptions"),
                    InlineKeyboardButton(text="💳 Пополнить", callback_data="top_up")
                ],
                [
                    InlineKeyboardButton(text="🎁 Рефералы", callback_data="referrals"),
                    InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
                ],
                [
                    InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
                    InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")
                ]
            ])
    
    def _get_subscription_menu_keyboard(self):
        """Получить клавиатуру меню подписки"""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 Настроить VPN", callback_data="setup_vpn"),
                InlineKeyboardButton(text="🔗 Скопировать ссылку", callback_data="copy_config")
            ],
            [
                InlineKeyboardButton(text="📊 QR-код", callback_data="show_qr"),
                InlineKeyboardButton(text="📋 Инструкция", callback_data="instructions")
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
            ]
        ])
    
    def _get_payment_success_keyboard(self):
        """Получить клавиатуру после успешной оплаты"""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 Активировать подписку", callback_data="activate_subscription"),
                InlineKeyboardButton(text="💰 Мой баланс", callback_data="my_balance")
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
            ]
        ])
    
    def get_available_effects(self) -> Dict[str, Any]:
        """
        Получить список доступных эффектов
        
        Returns:
            Dict: Словарь с эффектами
        """
        return MESSAGE_EFFECTS
    
    def get_effect_info(self, effect_name: str) -> Dict[str, Any]:
        """
        Получить информацию об эффекте
        
        Args:
            effect_name: Название эффекта
        
        Returns:
            Dict: Информация об эффекте
        """
        return get_usage_example(effect_name)