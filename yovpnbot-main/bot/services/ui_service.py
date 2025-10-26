"""
Сервис UI
Создание интерфейсов, клавиатур и форматирование сообщений
"""

import logging
from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from assets.emojis.interface import EMOJI, get_emoji_combination, create_progress_bar, format_balance, format_days

logger = logging.getLogger(__name__)

class UIService:
    """
    Сервис для создания пользовательского интерфейса
    
    Отвечает за:
    - Создание клавиатур и кнопок
    - Форматирование сообщений
    - Создание прогресс-баров
    - Управление навигацией
    """
    
    def __init__(self):
        """Инициализация сервиса"""
        logger.info("✅ UIService инициализирован")
    
    def get_current_time(self) -> str:
        """Получить текущее время в формате строки"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """
        Создать клавиатуру главного меню с современным дизайном 2025-2026
        
        Особенности:
        - Яркие эмодзи для визуальной привлекательности
        - Интуитивно понятная структура
        - Акцент на основных действиях
        
        Returns:
            InlineKeyboardMarkup: Клавиатура главного меню
        """
        keyboard = [
            # Основные действия (крупные кнопки)
            [
                InlineKeyboardButton(
                    text=f"🔐 Мои подписки",
                    callback_data="my_subscriptions"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"💎 Пополнить баланс",
                    callback_data="top_up"
                )
            ],
            # Дополнительные функции (две в ряд)
            [
                InlineKeyboardButton(
                    text=f"🎁 Рефералы",
                    callback_data="referrals"
                ),
                InlineKeyboardButton(
                    text=f"📊 Статистика",
                    callback_data="stats"
                )
            ],
            # Настройки и поддержка
            [
                InlineKeyboardButton(
                    text=f"⚙️ Настройки",
                    callback_data="settings"
                ),
                InlineKeyboardButton(
                    text=f"🆘 Поддержка",
                    callback_data="support"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    def create_subscription_menu_keyboard(self, has_active_subscription: bool = False) -> InlineKeyboardMarkup:
        """
        Создать клавиатуру меню подписки
        
        Args:
            has_active_subscription: Есть ли активная подписка
        
        Returns:
            InlineKeyboardMarkup: Клавиатура меню подписки
        """
        if has_active_subscription:
            keyboard = [
                [
                    InlineKeyboardButton(
                        text=f"{EMOJI['vpn']} Настроить VPN",
                        callback_data="setup_vpn"
                    ),
                    InlineKeyboardButton(
                        text=f"{EMOJI['link']} Скопировать ссылку",
                        callback_data="copy_config"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"{EMOJI['qr']} QR-код",
                        callback_data="show_qr"
                    ),
                    InlineKeyboardButton(
                        text=f"{EMOJI['info']} Инструкция",
                        callback_data="instructions"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"{EMOJI['back']} Назад",
                        callback_data="main_menu"
                    )
                ]
            ]
        else:
            keyboard = [
                [
                    InlineKeyboardButton(
                        text=f"{EMOJI['payment']} Активировать подписку",
                        callback_data="activate_subscription"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"{EMOJI['back']} Назад",
                        callback_data="main_menu"
                    )
                ]
            ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    def create_payment_keyboard(self, amounts: List[float] = None) -> InlineKeyboardMarkup:
        """
        Создать клавиатуру для выбора суммы платежа (UX 2025-2026)
        
        Особенности:
        - Популярные суммы выделены
        - Показываем эквивалент в днях
        - Визуально привлекательные эмодзи
        
        Args:
            amounts: Список сумм для отображения
        
        Returns:
            InlineKeyboardMarkup: Клавиатура платежей
        """
        if amounts is None:
            amounts = [40, 80, 120, 200, 400]
        
        keyboard = []
        
        # Эмодзи для разных диапазонов сумм
        emoji_map = {
            40: "🥉",   # Бронза
            80: "🥈",   # Серебро
            120: "🥇",  # Золото
            200: "💎",  # Платина
            400: "👑"   # Премиум
        }
        
        # Создаем кнопки для каждой суммы
        for i in range(0, len(amounts), 2):
            row = []
            for j in range(2):
                if i + j < len(amounts):
                    amount = amounts[i + j]
                    days = int(amount / 4)
                    emoji = emoji_map.get(amount, "💰")
                    
                    # Особый текст для популярных сумм
                    if amount == 120:
                        text = f"{emoji} {amount:.0f}₽ 🔥 ({days}д)"  # Популярный выбор
                    else:
                        text = f"{emoji} {amount:.0f}₽ ({days}д)"
                    
                    row.append(InlineKeyboardButton(
                        text=text,
                        callback_data=f"pay_{amount}"
                    ))
            keyboard.append(row)
        
        # Добавляем кнопку "Другая сумма"
        keyboard.append([
            InlineKeyboardButton(
                text=f"✏️ Ввести свою сумму",
                callback_data="pay_custom"
            )
        ])
        
        # Добавляем кнопку "Назад"
        keyboard.append([
            InlineKeyboardButton(
                text=f"⬅️ Назад",
                callback_data="main_menu"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    def create_payment_methods_keyboard(self) -> InlineKeyboardMarkup:
        """
        Создать клавиатуру способов оплаты
        
        Returns:
            InlineKeyboardMarkup: Клавиатура способов оплаты
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['card']} Банковская карта",
                    callback_data="pay_method_card"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['payment']} ЮMoney",
                    callback_data="pay_method_yoomoney"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['coins']} Криптовалюта",
                    callback_data="pay_method_crypto"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['back']} Назад",
                    callback_data="top_up"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    def create_settings_keyboard(self) -> InlineKeyboardMarkup:
        """
        Создать клавиатуру настроек
        
        Returns:
            InlineKeyboardMarkup: Клавиатура настроек
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['notification']} Уведомления",
                    callback_data="settings_notifications"
                ),
                InlineKeyboardButton(
                    text=f"{EMOJI['refresh']} Автопродление",
                    callback_data="settings_auto_renewal"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['info']} О боте",
                    callback_data="about_bot"
                ),
                InlineKeyboardButton(
                    text=f"{EMOJI['support']} Поддержка",
                    callback_data="support"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['back']} Назад",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    def create_back_keyboard(self, callback_data: str = "main_menu") -> InlineKeyboardMarkup:
        """
        Создать клавиатуру с кнопкой "Назад"
        
        Args:
            callback_data: Callback data для кнопки "Назад"
        
        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой "Назад"
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{EMOJI['back']} Назад",
                    callback_data=callback_data
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    def format_user_balance_message(self, balance: float, days: int, subscription_active: bool) -> str:
        """
        Форматировать сообщение с балансом пользователя
        
        Args:
            balance: Баланс пользователя
            days: Количество дней
            subscription_active: Активна ли подписка
        
        Returns:
            str: Отформатированное сообщение
        """
        status_emoji = EMOJI['active'] if subscription_active else EMOJI['inactive']
        status_text = "Активна" if subscription_active else "Неактивна"
        
        message = f"""
💰 <b>Ваш баланс</b>

{format_balance(balance)}
📅 {format_days(days)}
📊 <b>Подписка:</b> {status_emoji} {status_text}

<b>Что вы можете сделать:</b>
• 💳 Пополнить баланс
• 📱 Активировать подписку
• 📊 Посмотреть статистику
        """
        
        return message.strip()
    
    def format_subscription_info(self, subscription_data: Dict[str, Any]) -> str:
        """
        Форматировать информацию о подписке
        
        Args:
            subscription_data: Данные подписки
        
        Returns:
            str: Отформатированная информация
        """
        status = subscription_data.get('status', 'inactive')
        days = subscription_data.get('days', 0)
        expire = subscription_data.get('expire', 0)
        
        status_emoji = EMOJI['active'] if status == 'active' else EMOJI['inactive']
        status_text = "Активна" if status == 'active' else "Неактивна"
        
        message = f"""
📱 <b>Информация о подписке</b>

📊 <b>Статус:</b> {status_emoji} {status_text}
📅 <b>Дней:</b> {format_days(days)}
💰 <b>Стоимость:</b> 4 ₽ в день
🔄 <b>Продление:</b> Автоматическое

<b>Доступные действия:</b>
• 🔗 Скопировать конфигурацию
• 📱 Показать QR-код
• ⚙️ Настроить VPN
        """
        
        return message.strip()
    
    def format_payment_options(self, amount: float) -> str:
        """
        Форматировать опции платежа
        
        Args:
            amount: Сумма платежа
        
        Returns:
            str: Отформатированные опции
        """
        days = int(amount / 4)
        
        message = f"""
💳 <b>Пополнение баланса</b>

💰 <b>Сумма:</b> {amount:.0f} ₽
📅 <b>Дней доступа:</b> {format_days(days)}
🔄 <b>Активация:</b> Мгновенная

<b>Выберите способ оплаты:</b>
        """
        
        return message.strip()
    
    def create_progress_message(self, current: int, total: int, text: str = "Загрузка") -> str:
        """
        Создать сообщение с прогресс-баром
        
        Args:
            current: Текущее значение
            total: Максимальное значение
            text: Текст сообщения
        
        Returns:
            str: Сообщение с прогресс-баром
        """
        progress_bar = create_progress_bar(current, total)
        percentage = int((current / total) * 100) if total > 0 else 0
        
        message = f"""
{EMOJI['loading']} <b>{text}</b>

{progress_bar}
📊 <b>Прогресс:</b> {percentage}%
        """
        
        return message.strip()
    
    def create_error_message(self, error_code: str, error_description: str) -> str:
        """
        Создать сообщение об ошибке
        
        Args:
            error_code: Код ошибки
            error_description: Описание ошибки
        
        Returns:
            str: Сообщение об ошибке
        """
        message = f"""
❌ <b>Произошла ошибка</b>

🔢 <b>Код:</b> {error_code}
📋 <b>Описание:</b> {error_description}

<b>Что делать:</b>
• 🔄 Попробуйте еще раз
• 🆘 Обратитесь в поддержку
• ⏰ Подождите несколько минут
        """
        
        return message.strip()
    
    def create_success_message(self, title: str, description: str) -> str:
        """
        Создать сообщение об успехе
        
        Args:
            title: Заголовок
            description: Описание
        
        Returns:
            str: Сообщение об успехе
        """
        message = f"""
✅ <b>{title}</b>

{description}

<b>Что дальше?</b> Выберите действие ниже 👇
        """
        
        return message.strip()
    
    def create_button_with_emoji(self, text: str, emoji: str, callback_data: str) -> InlineKeyboardButton:
        """
        Создать кнопку с эмодзи
        
        Args:
            text: Текст кнопки
            emoji: Эмодзи
            callback_data: Callback data
        
        Returns:
            InlineKeyboardButton: Кнопка с эмодзи
        """
        return InlineKeyboardButton(
            text=f"{emoji} {text}",
            callback_data=callback_data
        )
    
    def create_navigation_keyboard(self, buttons: List[Dict[str, str]]) -> InlineKeyboardMarkup:
        """
        Создать клавиатуру навигации
        
        Args:
            buttons: Список кнопок с текстом и callback_data
        
        Returns:
            InlineKeyboardMarkup: Клавиатура навигации
        """
        keyboard = []
        
        for i in range(0, len(buttons), 2):
            row = []
            for j in range(2):
                if i + j < len(buttons):
                    button = buttons[i + j]
                    row.append(InlineKeyboardButton(
                        text=button['text'],
                        callback_data=button['callback_data']
                    ))
            keyboard.append(row)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)