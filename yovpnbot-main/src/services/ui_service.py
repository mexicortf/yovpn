#!/usr/bin/env python3
"""
Сервис для улучшенного UI и навигации
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from telebot import types

logger = logging.getLogger(__name__)

class UIService:
    """Сервис для создания улучшенного пользовательского интерфейса"""
    
    def __init__(self):
        # Эмодзи для кнопок с цветовой индикацией
        self.button_emojis = {
            # Основные действия
            'main_menu': '🏠',
            'back': '⬅️',
            'home': '🏠',
            'refresh': '🔄',
            
            # Подписки
            'subscription': '📋',
            'subscription_active': '🟢',
            'subscription_inactive': '🔴',
            'subscription_expired': '⏰',
            'add_subscription': '➕',
            'extend_subscription': '⏰',
            
            # Баланс и платежи
            'balance': '💰',
            'balance_low': '⚠️',
            'balance_critical': '🚨',
            'top_up': '💳',
            'payment_history': '📊',
            'coupon': '🎫',
            
            # Рефералы
            'referral': '👥',
            'invite': '📤',
            'share': '📤',
            'qr_code': '📱',
            
            # Настройки и помощь
            'settings': '⚙️',
            'help': '❓',
            'support': '🆘',
            'about': 'ℹ️',
            'info': 'ℹ️',
            
            # Действия
            'copy': '📋',
            'download': '⬇️',
            'upload': '⬆️',
            'edit': '✏️',
            'delete': '🗑️',
            'confirm': '✅',
            'cancel': '❌',
            
            # Статусы
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'loading': '🔄',
            'check': '✔️',
            
            # VPN и сеть
            'vpn': '🔒',
            'network': '🌐',
            'server': '🖥️',
            'key': '🔑',
            'link': '🔗',
            
            # Время и дата
            'time': '⏰',
            'calendar': '📅',
            'clock': '🕐',
            
            # Деньги
            'money': '💵',
            'coin': '🪙',
            'dollar': '💲',
            'ruble': '₽',
            
            # Устройства
            'phone': '📱',
            'computer': '💻',
            'tablet': '📱',
            'device': '📱'
        }
        
        # Группы кнопок для логической группировки
        self.button_groups = {
            'subscription': ['subscription', 'add_subscription', 'extend_subscription'],
            'balance': ['balance', 'top_up', 'payment_history', 'coupon'],
            'referral': ['referral', 'invite', 'share', 'qr_code'],
            'navigation': ['main_menu', 'back', 'home', 'refresh'],
            'actions': ['copy', 'download', 'confirm', 'cancel'],
            'support': ['help', 'support', 'about', 'settings']
        }
    
    def create_button(self, text: str, callback_data: str = None, url: str = None, 
                     emoji: str = None, color_indicator: str = None) -> types.InlineKeyboardButton:
        """Создать кнопку с улучшенным дизайном"""
        # Добавляем эмодзи если указан
        if emoji:
            button_text = f"{emoji} {text}"
        elif callback_data and callback_data in self.button_emojis:
            button_text = f"{self.button_emojis[callback_data]} {text}"
        else:
            button_text = text
        
        # Добавляем цветовой индикатор
        if color_indicator:
            button_text = f"{color_indicator} {button_text}"
        
        # Создаем кнопку
        if url:
            return types.InlineKeyboardButton(button_text, url=url)
        elif callback_data:
            return types.InlineKeyboardButton(button_text, callback_data=callback_data)
        else:
            return types.InlineKeyboardButton(button_text, callback_data="noop")
    
    def create_main_menu_keyboard(self, user_stats: Dict, has_subscription: bool = False) -> types.InlineKeyboardMarkup:
        """Создать главное меню с улучшенной навигацией"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # Группа подписок
        if has_subscription:
            keyboard.add(
                self.create_button("Мои подписки", "my_subscriptions", emoji="🟢"),
                self.create_button("Продлить", "extend_subscription", emoji="⏰")
            )
        else:
            keyboard.add(
                self.create_button("Активировать", "activate_subscription", emoji="🟢"),
                self.create_button("Мои подписки", "my_subscriptions", emoji="📋")
            )
        
        # Группа баланса
        balance = user_stats.get('balance', 0)
        balance_emoji = "🚨" if balance < 4 else "⚠️" if balance < 12 else "💰"
        
        keyboard.add(
            self.create_button("Баланс", "balance", emoji=balance_emoji),
            self.create_button("Пополнить", "top_up_balance", emoji="💳")
        )
        
        # Группа рефералов
        keyboard.add(
            self.create_button("Пригласить друга", "invite_friend", emoji="👥"),
            self.create_button("Мои рефералы", "my_referrals", emoji="📊")
        )
        
        # Группа поддержки
        keyboard.add(
            self.create_button("Помощь", "help", emoji="❓"),
            self.create_button("О сервисе", "about_service", emoji="ℹ️")
        )
        
        return keyboard
    
    def create_subscription_keyboard(self, subscription_info: Dict) -> types.InlineKeyboardMarkup:
        """Создать клавиатуру для управления подпиской"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        status = subscription_info.get('status', 'inactive')
        
        if status == 'active':
            # Активная подписка
            keyboard.add(
                self.create_button("Продлить", "extend_subscription", emoji="⏰"),
                self.create_button("Настройки", "subscription_settings", emoji="⚙️")
            )
            keyboard.add(
                self.create_button("Скопировать ссылку", "copy_subscription_link", emoji="📋"),
                self.create_button("QR-код", "show_subscription_qr", emoji="📱")
            )
        else:
            # Неактивная подписка
            keyboard.add(
                self.create_button("Активировать", "activate_subscription", emoji="🟢"),
                self.create_button("Пополнить баланс", "top_up_balance", emoji="💳")
            )
        
        keyboard.add(
            self.create_button("Назад", "back_to_main", emoji="⬅️")
        )
        
        return keyboard
    
    def create_balance_keyboard(self, balance: float) -> types.InlineKeyboardMarkup:
        """Создать клавиатуру для управления балансом"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # Быстрые суммы для пополнения
        quick_amounts = [20, 50, 100, 200]  # 5, 12, 25, 50 дней
        
        for amount in quick_amounts:
            days = int(amount / 4)
            keyboard.add(
                self.create_button(f"{amount} ₽ ({days} дн.)", f"quick_top_up_{amount}", emoji="💳")
            )
        
        keyboard.add(
            self.create_button("Другая сумма", "custom_top_up", emoji="✏️"),
            self.create_button("История платежей", "payment_history", emoji="📊")
        )
        
        keyboard.add(
            self.create_button("Активировать купон", "activate_coupon", emoji="🎫")
        )
        
        keyboard.add(
            self.create_button("Назад", "back_to_main", emoji="⬅️")
        )
        
        return keyboard
    
    def create_referral_keyboard(self, referral_link: str) -> types.InlineKeyboardMarkup:
        """Создать клавиатуру для реферальной системы"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        keyboard.add(
            self.create_button("Поделиться", "share_referral", emoji="📤"),
            self.create_button("QR-код", "show_referral_qr", emoji="📱")
        )
        
        keyboard.add(
            self.create_button("Скопировать ссылку", "copy_referral_link", emoji="📋"),
            self.create_button("Статистика", "referral_stats", emoji="📊")
        )
        
        keyboard.add(
            self.create_button("Назад", "back_to_main", emoji="⬅️")
        )
        
        return keyboard
    
    def create_copy_keyboard(self, text: str, copy_type: str) -> types.InlineKeyboardMarkup:
        """Создать клавиатуру для копирования текста"""
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        
        # Кнопка копирования (отправляем текст в отдельном сообщении)
        keyboard.add(
            self.create_button("📋 Скопировать", f"copy_{copy_type}", emoji="📋")
        )
        
        # Кнопка QR-кода
        keyboard.add(
            self.create_button("📱 Показать QR-код", f"qr_{copy_type}", emoji="📱")
        )
        
        keyboard.add(
            self.create_button("Назад", "back_to_previous", emoji="⬅️")
        )
        
        return keyboard
    
    def create_confirmation_keyboard(self, action: str, confirm_text: str = "Подтвердить", 
                                   cancel_text: str = "Отмена") -> types.InlineKeyboardMarkup:
        """Создать клавиатуру подтверждения"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        keyboard.add(
            self.create_button(confirm_text, f"confirm_{action}", emoji="✅", color_indicator="🟢"),
            self.create_button(cancel_text, f"cancel_{action}", emoji="❌", color_indicator="🔴")
        )
        
        return keyboard
    
    def create_pagination_keyboard(self, current_page: int, total_pages: int, 
                                 base_callback: str) -> types.InlineKeyboardMarkup:
        """Создать клавиатуру пагинации"""
        keyboard = types.InlineKeyboardMarkup(row_width=5)
        
        # Кнопки навигации
        nav_buttons = []
        
        # Первая страница
        if current_page > 1:
            nav_buttons.append(
                self.create_button("⏮️", f"{base_callback}_page_1")
            )
        
        # Предыдущая страница
        if current_page > 1:
            nav_buttons.append(
                self.create_button("◀️", f"{base_callback}_page_{current_page - 1}")
            )
        
        # Текущая страница
        nav_buttons.append(
            self.create_button(f"{current_page}/{total_pages}", "noop")
        )
        
        # Следующая страница
        if current_page < total_pages:
            nav_buttons.append(
                self.create_button("▶️", f"{base_callback}_page_{current_page + 1}")
            )
        
        # Последняя страница
        if current_page < total_pages:
            nav_buttons.append(
                self.create_button("⏭️", f"{base_callback}_page_{total_pages}")
            )
        
        keyboard.add(*nav_buttons)
        
        return keyboard
    
    def format_balance_message(self, balance: float, days_remaining: int) -> str:
        """Форматировать сообщение о балансе"""
        if balance < 4:
            status_emoji = "🚨"
            status_text = "Критически низкий баланс!"
        elif balance < 12:
            status_emoji = "⚠️"
            status_text = "Низкий баланс"
        else:
            status_emoji = "💰"
            status_text = "Баланс в норме"
        
        return f"""
{status_emoji} <b>Ваш баланс</b>

💰 <b>Сумма:</b> {balance} ₽
📅 <b>Доступно дней:</b> {days_remaining}
💳 <b>Стоимость:</b> 4 ₽/день

{status_text}
"""
    
    def format_subscription_message(self, subscription_info: Dict) -> str:
        """Форматировать сообщение о подписке"""
        status = subscription_info.get('status', 'inactive')
        days_remaining = subscription_info.get('days_remaining', 0)
        
        if status == 'active':
            status_emoji = "🟢"
            status_text = "Активна"
        elif status == 'expired':
            status_emoji = "🔴"
            status_text = "Истекла"
        else:
            status_emoji = "⚪"
            status_text = "Неактивна"
        
        return f"""
📋 <b>Моя подписка</b>

{status_emoji} <b>Статус:</b> {status_text}
📅 <b>Дней осталось:</b> {days_remaining}
🌐 <b>Трафик:</b> Безлимит
💳 <b>Стоимость:</b> 4 ₽/день

ℹ️ Подписка продлевается автоматически при наличии средств на балансе.
"""
    
    def create_loading_message(self, text: str, progress: int = 0, total: int = 100) -> str:
        """Создать сообщение загрузки с прогресс-баром"""
        if total > 0:
            percentage = int((progress / total) * 100)
            bar_length = 10
            filled = int((progress / total) * bar_length)
            empty = bar_length - filled
            
            progress_bar = "⬛" * filled + "⬜" * empty
            progress_text = f"\n\n{progress_bar} {percentage}%"
        else:
            progress_text = ""
        
        return f"🔄 {text}{progress_text}"
    
    def create_button_with_emoji(self, text: str, callback_data: str, button_type: str = "info") -> types.InlineKeyboardButton:
        """Создать кнопку с эмодзи"""
        emoji = self.button_emojis.get(button_type, "ℹ️")
        return types.InlineKeyboardButton(f"{emoji} {text}", callback_data=callback_data)