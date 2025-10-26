"""
Современная админ-панель для управления YoVPN Bot
Специально разработана для администратора ID: 7610842643
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest

from ..services.user_service import UserService
from ..services.marzban_service import MarzbanService
from ..services.ui_service import UIService
from ..services.animation_service import AnimationService

logger = logging.getLogger(__name__)

# ID администратора
ADMIN_ID = 7610842643

# Состояния для админ панели
class AdminStates(StatesGroup):
    waiting_user_id = State()
    waiting_balance_amount = State()
    waiting_subscription_days = State()
    waiting_broadcast_message = State()
    waiting_test_balance_user = State()

# Роутер для админ команд
admin_router = Router()

class ModernAdminPanel:
    """
    Современная админ-панель с полным функционалом управления
    Специально для администратора ID: 7610842643
    """
    
    def __init__(self, user_service: UserService, marzban_service: MarzbanService, 
                 ui_service: UIService, animation_service: AnimationService):
        self.user_service = user_service
        self.marzban_service = marzban_service
        self.ui_service = ui_service
        self.animation_service = animation_service
        self.admin_id = ADMIN_ID
        
    def is_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь администратором"""
        return user_id == self.admin_id
    
    async def get_main_menu(self) -> InlineKeyboardMarkup:
        """Главное меню админ панели с современным дизайном"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text="📊 Статистика", 
                    callback_data="admin_stats"
                ),
                InlineKeyboardButton(
                    text="👥 Пользователи", 
                    callback_data="admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Управление балансом", 
                    callback_data="admin_balance"
                ),
                InlineKeyboardButton(
                    text="🎁 Тестовый баланс", 
                    callback_data="admin_test_balance"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔧 Управление подписками", 
                    callback_data="admin_subscriptions"
                ),
                InlineKeyboardButton(
                    text="📢 Рассылка", 
                    callback_data="admin_broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Настройки Marzban", 
                    callback_data="admin_marzban"
                ),
                InlineKeyboardButton(
                    text="📈 Аналитика", 
                    callback_data="admin_analytics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔒 Безопасность", 
                    callback_data="admin_security"
                ),
                InlineKeyboardButton(
                    text="❌ Закрыть", 
                    callback_data="admin_close"
                )
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    async def get_stats_menu(self) -> InlineKeyboardMarkup:
        """Меню статистики с современным дизайном"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text="📊 Общая статистика", 
                    callback_data="admin_stats_general"
                ),
                InlineKeyboardButton(
                    text="👥 Пользователи", 
                    callback_data="admin_stats_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Финансы", 
                    callback_data="admin_stats_finance"
                ),
                InlineKeyboardButton(
                    text="🔧 Marzban", 
                    callback_data="admin_stats_marzban"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data="admin_back"
                )
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    async def get_users_menu(self) -> InlineKeyboardMarkup:
        """Меню управления пользователями"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text="🔍 Найти пользователя", 
                    callback_data="admin_find_user"
                ),
                InlineKeyboardButton(
                    text="📋 Список всех", 
                    callback_data="admin_list_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Активные", 
                    callback_data="admin_active_users"
                ),
                InlineKeyboardButton(
                    text="💸 С балансом", 
                    callback_data="admin_users_with_balance"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data="admin_back"
                )
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    async def get_balance_menu(self) -> InlineKeyboardMarkup:
        """Меню управления балансом"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text="➕ Пополнить", 
                    callback_data="admin_add_balance"
                ),
                InlineKeyboardButton(
                    text="➖ Списать", 
                    callback_data="admin_subtract_balance"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔧 Установить", 
                    callback_data="admin_set_balance"
                ),
                InlineKeyboardButton(
                    text="📊 Статистика", 
                    callback_data="admin_balance_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data="admin_back"
                )
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    async def get_subscription_menu(self) -> InlineKeyboardMarkup:
        """Меню управления подписками"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text="✅ Активировать", 
                    callback_data="admin_activate_subscription"
                ),
                InlineKeyboardButton(
                    text="❌ Деактивировать", 
                    callback_data="admin_deactivate_subscription"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⏰ Продлить", 
                    callback_data="admin_extend_subscription"
                ),
                InlineKeyboardButton(
                    text="📊 Статистика", 
                    callback_data="admin_subscription_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data="admin_back"
                )
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    async def get_general_stats(self) -> str:
        """Получить общую статистику с красивым форматированием"""
        try:
            users = await self.user_service.get_all_users()
            total_users = len(users)
            
            active_subscriptions = sum(1 for user in users.values() if user.get('subscription_active', False))
            total_balance = sum(user.get('balance', 0) for user in users.values())
            total_payments = sum(user.get('total_payments', 0) for user in users.values())
            
            # Статистика Marzban
            marzban_stats = await self.marzban_service.get_system_stats()
            marzban_status = "🟢 Онлайн" if self.marzban_service.is_available() else "🔴 Офлайн"
            
            # Расчеты
            activity_percent = (active_subscriptions/total_users*100) if total_users > 0 else 0
            avg_balance = (total_balance/total_users) if total_users > 0 else 0
            
            stats_text = f"""
🎯 <b>ОБЩАЯ СТАТИСТИКА</b>

👥 <b>Пользователи:</b>
• Всего: <code>{total_users}</code>
• Активные подписки: <code>{active_subscriptions}</code>
• Процент активности: <code>{activity_percent:.1f}%</code>

💰 <b>Финансы:</b>
• Общий баланс: <code>{total_balance:.2f} ₽</code>
• Общие платежи: <code>{total_payments:.2f} ₽</code>
• Средний баланс: <code>{avg_balance:.2f} ₽</code>

🔧 <b>Marzban:</b>
• Статус: {marzban_status}
• Пользователи: <code>{marzban_stats.get('users', 'N/A')}</code>
• Трафик: <code>{marzban_stats.get('traffic', 'N/A')}</code>

🕐 <b>Время:</b> <code>{self.ui_service.get_current_time()}</code>
"""
            return stats_text
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return f"❌ <b>Ошибка получения статистики:</b>\n<code>{e}</code>"
    
    async def get_user_stats(self, user_id: int) -> str:
        """Получить статистику конкретного пользователя"""
        try:
            user = await self.user_service.get_user(user_id)
            if not user:
                return f"❌ <b>Пользователь с ID</b> <code>{user_id}</code> <b>не найден</b>"
            
            stats = await self.user_service.get_user_stats(user_id)
            
            stats_text = f"""
👤 <b>ПОЛЬЗОВАТЕЛЬ #{user_id}</b>

📝 <b>Информация:</b>
• Имя: <code>{user.get('first_name', 'N/A')}</code>
• Username: <code>@{user.get('username', 'N/A')}</code>
• Реферальный код: <code>{user.get('referral_code', 'N/A')}</code>

💰 <b>Финансы:</b>
• Баланс: <code>{stats.get('balance', 0):.2f} ₽</code>
• Всего платежей: <code>{stats.get('total_payments', 0):.2f} ₽</code>

🔧 <b>Подписка:</b>
• Статус: {'✅ Активна' if stats.get('subscription_active') else '❌ Неактивна'}
• Дней: <code>{stats.get('subscription_days', 0)}</code>

📊 <b>Активность:</b>
• Рефералов: <code>{stats.get('referrals_count', 0)}</code>
• Создан: <code>{stats.get('created_at', 'N/A')}</code>
• Последняя активность: <code>{stats.get('last_activity', 'N/A')}</code>
"""
            return stats_text
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики пользователя: {e}")
            return f"❌ <b>Ошибка получения статистики пользователя:</b>\n<code>{e}</code>"
    
    async def get_users_list(self, limit: int = 10) -> str:
        """Получить список пользователей с красивым форматированием"""
        try:
            users = await self.user_service.get_all_users()
            
            if not users:
                return "📋 <b>Список пользователей пуст</b>"
            
            # Сортируем по дате создания
            sorted_users = sorted(users.values(), 
                                key=lambda x: x.get('created_at', ''), 
                                reverse=True)
            
            users_text = f"📋 <b>ПОЛЬЗОВАТЕЛИ</b> (показано {min(limit, len(sorted_users))} из {len(users)})\n\n"
            
            for i, user in enumerate(sorted_users[:limit], 1):
                user_id = user.get('user_id', 'N/A')
                first_name = user.get('first_name', 'N/A')
                username = user.get('username', 'N/A')
                balance = user.get('balance', 0)
                subscription_active = user.get('subscription_active', False)
                
                status_emoji = "✅" if subscription_active else "❌"
                username_text = f"@{username}" if username != 'N/A' else "Без username"
                
                users_text += f"<b>{i}.</b> <code>{first_name}</code> ({username_text})\n"
                users_text += f"   ID: <code>{user_id}</code> | Баланс: <code>{balance:.2f} ₽</code> | Подписка: {status_emoji}\n\n"
            
            return users_text
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка пользователей: {e}")
            return f"❌ <b>Ошибка получения списка пользователей:</b>\n<code>{e}</code>"

# Инициализация админ панели
admin_panel = None

def init_admin_panel(user_service: UserService, marzban_service: MarzbanService, 
                    ui_service: UIService, animation_service: AnimationService):
    """Инициализировать админ панель"""
    global admin_panel
    admin_panel = ModernAdminPanel(user_service, marzban_service, ui_service, animation_service)

# Обработчики команд
@admin_router.message(Command("admin"))
async def admin_command(message: Message):
    """Команда /admin - открыть админ панель"""
    if not admin_panel or not admin_panel.is_admin(message.from_user.id):
        await message.reply("❌ <b>У вас нет прав администратора</b>")
        return
    
    keyboard = await admin_panel.get_main_menu()
    await message.reply(
        "🔧 <b>АДМИН ПАНЕЛЬ</b>\n\n"
        "Добро пожаловать в панель управления YoVPN Bot!\n"
        "Выберите действие:",
        reply_markup=keyboard
    )

# Обработчики callback'ов
@admin_router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    """Обработчик статистики"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    keyboard = await admin_panel.get_stats_menu()
    await callback.message.edit_text(
        "📊 <b>СТАТИСТИКА</b>\n\nВыберите тип статистики:",
        reply_markup=keyboard
    )

@admin_router.callback_query(F.data == "admin_stats_general")
async def admin_stats_general_callback(callback: CallbackQuery):
    """Общая статистика"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    stats_text = await admin_panel.get_general_stats()
    keyboard = await admin_panel.get_stats_menu()
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=keyboard
    )

@admin_router.callback_query(F.data == "admin_users")
async def admin_users_callback(callback: CallbackQuery):
    """Обработчик пользователей"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    keyboard = await admin_panel.get_users_menu()
    await callback.message.edit_text(
        "👥 <b>УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ</b>\n\nВыберите действие:",
        reply_markup=keyboard
    )

@admin_router.callback_query(F.data == "admin_list_users")
async def admin_list_users_callback(callback: CallbackQuery):
    """Список пользователей"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    users_text = await admin_panel.get_users_list()
    keyboard = await admin_panel.get_users_menu()
    
    await callback.message.edit_text(
        users_text,
        reply_markup=keyboard
    )

@admin_router.callback_query(F.data == "admin_balance")
async def admin_balance_callback(callback: CallbackQuery):
    """Обработчик баланса"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    keyboard = await admin_panel.get_balance_menu()
    await callback.message.edit_text(
        "💰 <b>УПРАВЛЕНИЕ БАЛАНСОМ</b>\n\nВыберите действие:",
        reply_markup=keyboard
    )

@admin_router.callback_query(F.data == "admin_subscriptions")
async def admin_subscriptions_callback(callback: CallbackQuery):
    """Обработчик подписок"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    keyboard = await admin_panel.get_subscription_menu()
    await callback.message.edit_text(
        "🔧 <b>УПРАВЛЕНИЕ ПОДПИСКАМИ</b>\n\nВыберите действие:",
        reply_markup=keyboard
    )

@admin_router.callback_query(F.data == "admin_back")
async def admin_back_callback(callback: CallbackQuery):
    """Назад в главное меню"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    keyboard = await admin_panel.get_main_menu()
    await callback.message.edit_text(
        "🔧 <b>АДМИН ПАНЕЛЬ</b>\n\nВыберите действие:",
        reply_markup=keyboard
    )

@admin_router.callback_query(F.data == "admin_close")
async def admin_close_callback(callback: CallbackQuery):
    """Закрыть админ панель"""
    await callback.message.delete()
    await callback.answer("✅ Админ панель закрыта")

# Обработчики для управления балансом
@admin_router.callback_query(F.data == "admin_add_balance")
async def admin_add_balance_callback(callback: CallbackQuery, state: FSMContext):
    """Добавить баланс"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_user_id)
    await callback.message.edit_text(
        "💰 <b>ПОПОЛНЕНИЕ БАЛАНСА</b>\n\n"
        "Введите ID пользователя:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")]
        ])
    )

@admin_router.message(StateFilter(AdminStates.waiting_user_id))
async def process_user_id(message: Message, state: FSMContext):
    """Обработка ID пользователя"""
    try:
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
        await state.set_state(AdminStates.waiting_balance_amount)
        
        await message.reply(
            f"✅ <b>ID пользователя:</b> <code>{user_id}</code>\n\n"
            "Введите сумму для пополнения:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")]
            ])
        )
    except ValueError:
        await message.reply("❌ <b>Неверный формат ID.</b> Введите число:")

@admin_router.message(StateFilter(AdminStates.waiting_balance_amount))
async def process_balance_amount(message: Message, state: FSMContext):
    """Обработка суммы баланса"""
    try:
        amount = float(message.text)
        data = await state.get_data()
        user_id = data['user_id']
        
        # Обновляем баланс
        success = await admin_panel.user_service.update_user_balance(user_id, amount, "add")
        
        if success:
            user_stats = await admin_panel.get_user_stats(user_id)
            await message.reply(
                f"✅ <b>Баланс пользователя</b> <code>{user_id}</code> <b>пополнен на</b> <code>{amount:.2f} ₽</code>\n\n{user_stats}",
                reply_markup=await admin_panel.get_balance_menu()
            )
        else:
            await message.reply(
                f"❌ <b>Ошибка пополнения баланса для пользователя</b> <code>{user_id}</code>",
                reply_markup=await admin_panel.get_balance_menu()
            )
        
        await state.clear()
        
    except ValueError:
        await message.reply("❌ <b>Неверный формат суммы.</b> Введите число:")

# Обработчики для управления подписками
@admin_router.callback_query(F.data == "admin_activate_subscription")
async def admin_activate_subscription_callback(callback: CallbackQuery, state: FSMContext):
    """Активировать подписку"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_user_id)
    await callback.message.edit_text(
        "✅ <b>АКТИВАЦИЯ ПОДПИСКИ</b>\n\n"
        "Введите ID пользователя:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")]
        ])
    )

@admin_router.callback_query(F.data == "admin_find_user")
async def admin_find_user_callback(callback: CallbackQuery, state: FSMContext):
    """Найти пользователя"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_user_id)
    await callback.message.edit_text(
        "🔍 <b>ПОИСК ПОЛЬЗОВАТЕЛЯ</b>\n\n"
        "Введите ID пользователя:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")]
        ])
    )

@admin_router.message(StateFilter(AdminStates.waiting_user_id))
async def process_find_user(message: Message, state: FSMContext):
    """Обработка поиска пользователя"""
    try:
        user_id = int(message.text)
        user_stats = await admin_panel.get_user_stats(user_id)
        
        await message.reply(
            user_stats,
            reply_markup=await admin_panel.get_users_menu()
        )
        await state.clear()
        
    except ValueError:
        await message.reply("❌ <b>Неверный формат ID.</b> Введите число:")

# Обработчики для тестового баланса
@admin_router.callback_query(F.data == "admin_test_balance")
async def admin_test_balance_callback(callback: CallbackQuery, state: FSMContext):
    """Тестовый баланс 15₽"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_test_balance_user)
    await callback.message.edit_text(
        "🎁 <b>ТЕСТОВЫЙ БАЛАНС</b>\n\n"
        "Начислить <code>15 ₽</code> тестового баланса пользователю.\n\n"
        "Введите ID пользователя:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")]
        ])
    )

@admin_router.message(StateFilter(AdminStates.waiting_test_balance_user))
async def process_test_balance_user(message: Message, state: FSMContext):
    """Обработка начисления тестового баланса"""
    try:
        user_id = int(message.text)
        
        # Начисляем 15₽ тестового баланса
        success = await admin_panel.user_service.update_user_balance(user_id, 15.0, "add")
        
        if success:
            # Отправляем сообщение с анимацией пользователю
            try:
                # Получаем информацию о пользователе
                user = await admin_panel.user_service.get_user(user_id)
                if user:
                    # Отправляем уведомление с анимацией
                    await admin_panel.animation_service.send_message_with_effect(
                        chat_id=user_id,
                        text="🎁 <b>Тестовый баланс начислен!</b>\n\n"
                             "Вам начислено <code>15 ₽</code> тестового баланса.\n"
                             "Спасибо за использование YoVPN Bot!",
                        effect_name="confetti"
                    )
            except Exception as e:
                logger.warning(f"⚠️ Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            user_stats = await admin_panel.get_user_stats(user_id)
            await message.reply(
                f"🎁 <b>Тестовый баланс начислен!</b>\n\n"
                f"Пользователю <code>{user_id}</code> начислено <code>15 ₽</code>\n\n{user_stats}",
                reply_markup=await admin_panel.get_balance_menu()
            )
        else:
            await message.reply(
                f"❌ <b>Ошибка начисления тестового баланса для пользователя</b> <code>{user_id}</code>",
                reply_markup=await admin_panel.get_balance_menu()
            )
        
        await state.clear()
        
    except ValueError:
        await message.reply("❌ <b>Неверный формат ID.</b> Введите число:")

# Обработчики для рассылки
@admin_router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_callback(callback: CallbackQuery, state: FSMContext):
    """Рассылка сообщений"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_broadcast_message)
    await callback.message.edit_text(
        "📢 <b>РАССЫЛКА СООБЩЕНИЙ</b>\n\n"
        "Введите текст сообщения для рассылки:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back")]
        ])
    )

@admin_router.message(StateFilter(AdminStates.waiting_broadcast_message))
async def process_broadcast_message(message: Message, state: FSMContext):
    """Обработка рассылки сообщений"""
    try:
        broadcast_text = message.text
        users = await admin_panel.user_service.get_all_users()
        
        sent_count = 0
        failed_count = 0
        
        for user_id in users.keys():
            try:
                await message.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 <b>Сообщение от администратора:</b>\n\n{broadcast_text}"
                )
                sent_count += 1
                await asyncio.sleep(0.1)  # Задержка между отправками
            except Exception as e:
                failed_count += 1
                logger.warning(f"⚠️ Не удалось отправить сообщение пользователю {user_id}: {e}")
        
        await message.reply(
            f"📢 <b>Рассылка завершена!</b>\n\n"
            f"✅ Отправлено: <code>{sent_count}</code>\n"
            f"❌ Ошибок: <code>{failed_count}</code>",
            reply_markup=await admin_panel.get_main_menu()
        )
        
        await state.clear()
        
    except Exception as e:
        await message.reply(f"❌ <b>Ошибка рассылки:</b>\n<code>{e}</code>")
        await state.clear()

# Обработчики для Marzban
@admin_router.callback_query(F.data == "admin_marzban")
async def admin_marzban_callback(callback: CallbackQuery):
    """Настройки Marzban"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    marzban_status = "🟢 Онлайн" if admin_panel.marzban_service.is_available() else "🔴 Офлайн"
    marzban_stats = await admin_panel.marzban_service.get_system_stats()
    
    marzban_text = f"""
⚙️ <b>НАСТРОЙКИ MARZBAN</b>

🔧 <b>Статус:</b> {marzban_status}
📊 <b>Пользователи:</b> <code>{marzban_stats.get('users', 'N/A')}</code>
📈 <b>Трафик:</b> <code>{marzban_stats.get('traffic', 'N/A')}</code>
🌐 <b>API URL:</b> <code>{admin_panel.marzban_service.api_url}</code>

<b>Доступные действия:</b>
• Проверить подключение
• Синхронизировать пользователей
• Обновить статистику
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Проверить подключение", callback_data="admin_marzban_check")],
        [InlineKeyboardButton(text="👥 Синхронизировать", callback_data="admin_marzban_sync")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(marzban_text, reply_markup=keyboard)

@admin_router.callback_query(F.data == "admin_marzban_check")
async def admin_marzban_check_callback(callback: CallbackQuery):
    """Проверка подключения к Marzban"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    try:
        is_available = admin_panel.marzban_service.is_available()
        status = "🟢 Подключение успешно" if is_available else "🔴 Ошибка подключения"
        
        await callback.answer(status, show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)

# Обработчики для аналитики
@admin_router.callback_query(F.data == "admin_analytics")
async def admin_analytics_callback(callback: CallbackQuery):
    """Аналитика"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    analytics_text = """
📈 <b>АНАЛИТИКА</b>

<b>Доступные отчеты:</b>
• Финансовая аналитика
• Анализ пользователей
• Статистика подписок
• Тренды и прогнозы

<b>Функции:</b>
• Экспорт данных
• Графики и диаграммы
• Автоматические отчеты
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Финансы", callback_data="admin_analytics_finance")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_analytics_users")],
        [InlineKeyboardButton(text="📊 Подписки", callback_data="admin_analytics_subscriptions")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(analytics_text, reply_markup=keyboard)

# Обработчики для безопасности
@admin_router.callback_query(F.data == "admin_security")
async def admin_security_callback(callback: CallbackQuery):
    """Безопасность"""
    if not admin_panel or not admin_panel.is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    security_text = """
🔒 <b>БЕЗОПАСНОСТЬ</b>

<b>Текущие настройки:</b>
• Админ ID: <code>7610842643</code>
• Логирование: Включено
• Мониторинг: Активен

<b>Функции безопасности:</b>
• Просмотр логов
• Мониторинг активности
• Настройка доступа
• Резервное копирование
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Логи", callback_data="admin_security_logs")],
        [InlineKeyboardButton(text="👁️ Мониторинг", callback_data="admin_security_monitor")],
        [InlineKeyboardButton(text="💾 Резервная копия", callback_data="admin_security_backup")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(security_text, reply_markup=keyboard)