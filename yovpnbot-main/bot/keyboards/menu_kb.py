"""
Современные клавиатуры для меню бота
Единый стиль с трендами 2025-2026
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


class MenuKeyboards:
    """
    Класс для создания всех клавиатур бота
    Современный минималистичный дизайн
    """
    
    @staticmethod
    def get_main_menu() -> InlineKeyboardMarkup:
        """
        Главное меню - современный дизайн с акцентом на основные действия
        
        Структура:
        - Крупные кнопки для основных действий (1 в ряд)
        - Дополнительные функции (2 в ряд)
        - Настройки и поддержка (2 в ряд)
        """
        keyboard = [
            # Основные действия - широкие кнопки
            [
                InlineKeyboardButton(
                    text="🔐 Мои подписки",
                    callback_data="my_subscriptions"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 Пополнить баланс",
                    callback_data="top_up"
                )
            ],
            # Дополнительные функции - 2 в ряд
            [
                InlineKeyboardButton(
                    text="🎁 Рефералы",
                    callback_data="referrals"
                ),
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="stats"
                )
            ],
            # Настройки и поддержка - 2 в ряд
            [
                InlineKeyboardButton(
                    text="⚙️ Настройки",
                    callback_data="settings"
                ),
                InlineKeyboardButton(
                    text="🆘 Поддержка",
                    callback_data="support"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def get_subscription_menu(has_active: bool = False) -> InlineKeyboardMarkup:
        """
        Меню подписок - адаптивное в зависимости от наличия активной подписки
        
        Args:
            has_active: Есть ли активная подписка
        """
        if has_active:
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="📱 Настроить VPN",
                        callback_data="setup_vpn"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔗 Скопировать ссылку",
                        callback_data="copy_config"
                    ),
                    InlineKeyboardButton(
                        text="📱 QR-код",
                        callback_data="show_qr"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📋 Инструкция",
                        callback_data="instructions"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏠 Главное меню",
                        callback_data="main_menu"
                    )
                ]
            ]
        else:
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="✨ Активировать подписку",
                        callback_data="activate_subscription"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="💎 Пополнить баланс",
                        callback_data="top_up"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏠 Главное меню",
                        callback_data="main_menu"
                    )
                ]
            ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def get_payment_amounts() -> InlineKeyboardMarkup:
        """
        Клавиатура выбора суммы пополнения
        С визуальными акцентами на популярных суммах
        """
        keyboard = [
            # Малые суммы
            [
                InlineKeyboardButton(
                    text="🥉 40₽ (10д)",
                    callback_data="pay_40"
                ),
                InlineKeyboardButton(
                    text="🥈 80₽ (20д)",
                    callback_data="pay_80"
                )
            ],
            # Популярная сумма - выделена
            [
                InlineKeyboardButton(
                    text="🥇 120₽ (30д) 🔥 ХИТ",
                    callback_data="pay_120"
                )
            ],
            # Большие суммы
            [
                InlineKeyboardButton(
                    text="💎 200₽ (50д)",
                    callback_data="pay_200"
                ),
                InlineKeyboardButton(
                    text="👑 400₽ (100д)",
                    callback_data="pay_400"
                )
            ],
            # Своя сумма
            [
                InlineKeyboardButton(
                    text="✏️ Ввести свою сумму",
                    callback_data="pay_custom"
                )
            ],
            # Назад
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def get_payment_methods() -> InlineKeyboardMarkup:
        """
        Способы оплаты
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    text="💳 Банковская карта",
                    callback_data="pay_method_card"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 ЮMoney",
                    callback_data="pay_method_yoomoney"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🪙 Криптовалюта",
                    callback_data="pay_method_crypto"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="top_up"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def get_settings_menu() -> InlineKeyboardMarkup:
        """
        Меню настроек
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    text="🔔 Уведомления",
                    callback_data="settings_notifications"
                ),
                InlineKeyboardButton(
                    text="🔄 Автопродление",
                    callback_data="settings_auto_renewal"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ О боте",
                    callback_data="about_bot"
                ),
                InlineKeyboardButton(
                    text="📋 FAQ",
                    callback_data="faq"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def get_back_button(callback_data: str = "main_menu", text: str = "🏠 Главное меню") -> InlineKeyboardMarkup:
        """
        Универсальная кнопка "Назад"
        
        Args:
            callback_data: Callback для кнопки
            text: Текст кнопки
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def get_referral_menu() -> InlineKeyboardMarkup:
        """
        Меню реферальной программы
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    text="📤 Поделиться ссылкой",
                    switch_inline_query="Присоединяйся к YoVPN! 🚀"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Мои рефералы",
                    callback_data="my_referrals"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def get_support_menu() -> InlineKeyboardMarkup:
        """
        Меню поддержки
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    text="💬 Написать в поддержку",
                    url="https://t.me/YoVPNSupport"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 FAQ",
                    callback_data="faq"
                ),
                InlineKeyboardButton(
                    text="📖 Инструкции",
                    callback_data="instructions"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
