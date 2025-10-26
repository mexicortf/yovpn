"""
Обработчик текстового режима бота
Реализует полный функционал без WebApp
"""

import asyncio
import logging
from aiogram import Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Optional

logger = logging.getLogger(__name__)


class ActivationStates(StatesGroup):
    """Состояния активации подписки"""
    waiting_for_platform = State()
    waiting_for_app_install = State()
    waiting_for_config = State()


class TextModeHandler:
    """Обработчик текстового режима"""
    
    def __init__(self, services):
        self.services = services
        self.user_service = services.get_user_service()
        self.marzban_service = services.get_marzban_service()
        self.animation_service = services.get_animation_service()
        
        # Поддержка
        self.support_username = "@yovpnsupbot"
        self.required_channel = "@yodevelop"
    
    async def check_channel_subscription(self, user_id: int, bot) -> bool:
        """Проверка подписки на канал"""
        try:
            member = await bot.get_chat_member(chat_id=self.required_channel, user_id=user_id)
            return member.status in ['member', 'administrator', 'creator']
        except Exception as e:
            logger.error(f"Ошибка проверки подписки: {e}")
            return False
    
    async def send_subscription_required(self, message: Message):
        """Отправка сообщения о необходимости подписки"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{self.required_channel[1:]}")],
            [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
        ])
        
        text = (
            "⚠️ <b>Доступ ограничен</b>\n\n"
            f"Для использования бота необходимо подписаться на наш канал {self.required_channel}\n\n"
            "📢 После подписки нажмите кнопку <b>\"Я подписался\"</b>"
        )
        
        await message.answer(text, reply_markup=keyboard)
    
    async def start_command(self, message: Message, state: FSMContext):
        """
        Команда /start с анимированным приветствием
        
        Логика:
        1. Проверка подписки на канал
        2. Анимация загрузки для новых пользователей
        3. Выдача приветственного бонуса (3 дня = 12 руб)
        4. Создание пользователя в MySQL
        5. Отображение главного меню
        """
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name or "Пользователь"
        
        # Проверяем подписку на канал
        is_subscribed = await self.check_channel_subscription(user_id, message.bot)
        
        if not is_subscribed:
            await self.send_subscription_required(message)
            return
        
        # Получаем или создаем пользователя
        user = await self.user_service.get_user(user_id)
        is_new_user = user is None
        
        if is_new_user:
            # Анимация загрузки для новых пользователей
            loading_msg = await message.answer("🔄 <b>Инициализация...</b>")
            
            for text in [
                "⚙️ <b>Создание аккаунта...</b>",
                "💎 <b>Начисление бонуса...</b>",
                "🛰️ <b>Настройка подключения...</b>",
                "✨ <b>Готово!</b>"
            ]:
                await asyncio.sleep(0.7)
                await loading_msg.edit_text(text)
            
            await asyncio.sleep(0.5)
            await loading_msg.delete()
            
            # Создаем пользователя с бонусом
            user = await self.user_service.create_or_update_user(
                user_id=user_id,
                username=username,
                first_name=first_name
            )
            
            # Начисляем приветственный бонус (3 дня = 12 руб)
            await self.user_service.add_balance(
                user_id=user_id,
                amount=12.0,
                description="🎁 Приветственный бонус"
            )
            
            # Приветственное сообщение
            welcome_text = (
                f"🎉 <b>Добро пожаловать, {first_name}!</b>\n\n"
                "💎 Вы получили <b>приветственный бонус</b>:\n"
                "   • <b>12 рублей</b> на балансе\n"
                "   • <b>3 дня</b> бесплатного VPN\n\n"
                "🚀 <b>Начните прямо сейчас!</b>\n"
                "Активируйте подписку в 3 простых шага:\n"
                "   1️⃣ Выберите платформу\n"
                "   2️⃣ Установите приложение\n"
                "   3️⃣ Получите конфигурацию\n\n"
                "💡 Пригласите друзей и получайте <b>1 день VPN</b> за каждого!"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Активировать VPN", callback_data="activate_start")],
                [InlineKeyboardButton(text="👥 Пригласить друга", callback_data="referral")]
            ])
            
            await message.answer(welcome_text, reply_markup=keyboard)
            
            logger.info(f"✅ Новый пользователь зарегистрирован: {first_name} (ID: {user_id})")
        
        else:
            # Обновляем данные пользователя
            await self.user_service.update_user(
                user_id=user_id,
                username=username,
                first_name=first_name
            )
            
            # Получаем статистику
            balance = user.get('balance', 0.0)
            subscription_days = balance // 4  # 4 руб = 1 день
            
            welcome_text = (
                f"👋 <b>С возвращением, {first_name}!</b>\n\n"
                f"💰 Баланс: <b>{balance:.2f} ₽</b>\n"
                f"📅 Доступно дней: <b>{subscription_days}</b>\n\n"
                "Выберите действие:"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Моя подписка", callback_data="my_subscription")],
                [InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="add_balance")],
                [InlineKeyboardButton(text="👥 Рефералы", callback_data="referral")],
                [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{self.support_username[1:]}")],
            ])
            
            await message.answer(welcome_text, reply_markup=keyboard)
    
    async def activate_start_callback(self, callback: CallbackQuery, state: FSMContext):
        """Начало активации VPN - выбор платформы"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 iOS (iPhone/iPad)", callback_data="platform_ios")],
            [InlineKeyboardButton(text="🤖 Android", callback_data="platform_android")],
            [InlineKeyboardButton(text="💻 Windows", callback_data="platform_windows")],
            [InlineKeyboardButton(text="🍎 macOS", callback_data="platform_macos")],
            [InlineKeyboardButton(text="🐧 Linux", callback_data="platform_linux")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
        
        text = (
            "<b>📱 Шаг 1/3: Выбор платформы</b>\n\n"
            "Выберите вашу операционную систему:"
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(ActivationStates.waiting_for_platform)
    
    async def platform_selected_callback(self, callback: CallbackQuery, state: FSMContext):
        """Обработка выбора платформы"""
        platform = callback.data.replace("platform_", "")
        await state.update_data(platform=platform)
        
        # Обновляем выбранную платформу в БД
        await self.user_service.update_user(
            user_id=callback.from_user.id,
            selected_platform=platform,
            activation_step=1
        )
        
        # Рекомендации по приложениям
        apps = {
            "ios": {
                "name": "Shadowrocket",
                "url": "https://apps.apple.com/app/shadowrocket/id932747118",
                "alt": ["V2Box", "Quantumult X"]
            },
            "android": {
                "name": "v2rayNG",
                "url": "https://play.google.com/store/apps/details?id=com.v2ray.ang",
                "alt": ["SagerNet", "Clash for Android"]
            },
            "windows": {
                "name": "v2rayN",
                "url": "https://github.com/2dust/v2rayN/releases",
                "alt": ["Clash for Windows", "Qv2ray"]
            },
            "macos": {
                "name": "V2RayXS",
                "url": "https://github.com/Cenmrev/V2RayXS/releases",
                "alt": ["ClashX", "V2RayU"]
            },
            "linux": {
                "name": "v2ray-core",
                "url": "https://github.com/v2fly/v2ray-core/releases",
                "alt": ["Qv2ray", "v2rayA"]
            }
        }
        
        app_info = apps.get(platform, apps["android"])
        
        text = (
            f"<b>✅ Шаг 2/3: Установка приложения</b>\n\n"
            f"Для <b>{platform.upper()}</b> рекомендуем:\n\n"
            f"📲 <b>{app_info['name']}</b>\n"
            f"🔗 {app_info['url']}\n\n"
            f"<i>Альтернативы: {', '.join(app_info['alt'])}</i>\n\n"
            f"После установки нажмите <b>\"Продолжить\"</b>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Продолжить", callback_data="app_installed")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(ActivationStates.waiting_for_app_install)
    
    async def app_installed_callback(self, callback: CallbackQuery, state: FSMContext):
        """Приложение установлено - создание конфигурации"""
        user_id = callback.from_user.id
        username = callback.from_user.username or f"user_{user_id}"
        
        data = await state.get_data()
        platform = data.get('platform', 'android')
        
        # Обновляем шаг активации
        await self.user_service.update_user(
            user_id=user_id,
            activation_step=2
        )
        
        # Создаем подписку через Marzban API
        loading_msg = await callback.message.edit_text("⚙️ <b>Создание VPN конфигурации...</b>")
        
        try:
            # Создаем подписку на 3 дня (приветственный бонус)
            subscription = await self.marzban_service.create_subscription(
                username=username,
                telegram_id=user_id,
                days=3,
                data_limit=0  # Безлимитный трафик
            )
            
            if subscription:
                # Сохраняем подписку в БД
                await self.user_service.create_subscription(
                    user_id=user_id,
                    marzban_username=username,
                    subscription_url=subscription.subscription_url,
                    days=3
                )
                
                # Обновляем шаг активации
                await self.user_service.update_user(
                    user_id=user_id,
                    activation_step=3,
                    first_start_completed=True
                )
                
                text = (
                    "<b>🎉 Поздравляем! VPN активирован</b>\n\n"
                    f"✅ Ваша подписка создана\n"
                    f"📅 Срок: <b>3 дня</b> (бесплатно)\n"
                    f"🌐 Трафик: <b>Безлимит</b>\n\n"
                    f"<b>📋 Инструкция:</b>\n"
                    f"1. Скопируйте ссылку ниже\n"
                    f"2. Откройте приложение VPN\n"
                    f"3. Вставьте ссылку\n"
                    f"4. Подключитесь!\n\n"
                    f"<code>{subscription.subscription_url}</code>\n\n"
                    f"💡 <i>Нажмите на ссылку для копирования</i>"
                )
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Моя подписка", callback_data="my_subscription")],
                    [InlineKeyboardButton(text="👥 Пригласить друзей", callback_data="referral")],
                    [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{self.support_username[1:]}")],
                ])
                
                await loading_msg.edit_text(text, reply_markup=keyboard)
                await state.clear()
                
                logger.info(f"✅ VPN активирован для {username} (ID: {user_id})")
            
            else:
                raise Exception("Не удалось создать подписку")
        
        except Exception as e:
            logger.error(f"❌ Ошибка активации VPN: {e}")
            
            text = (
                "❌ <b>Ошибка активации</b>\n\n"
                "Не удалось создать VPN конфигурацию.\n"
                f"Обратитесь в поддержку: {self.support_username}"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="activate_start")],
                [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{self.support_username[1:]}")],
            ])
            
            await loading_msg.edit_text(text, reply_markup=keyboard)
            await state.clear()
    
    async def my_subscription_callback(self, callback: CallbackQuery):
        """Просмотр информации о подписке"""
        user_id = callback.from_user.id
        
        # Получаем информацию о подписке
        subscription = await self.user_service.get_active_subscription(user_id)
        balance = await self.user_service.get_balance(user_id)
        
        if subscription:
            days_left = (subscription['end_date'] - datetime.now()).days if subscription.get('end_date') else 0
            
            text = (
                "<b>📊 Ваша подписка</b>\n\n"
                f"✅ Статус: <b>Активна</b>\n"
                f"📅 Осталось дней: <b>{days_left}</b>\n"
                f"🌐 Трафик: <b>Безлимит</b>\n"
                f"💰 Баланс: <b>{balance:.2f} ₽</b>\n\n"
                f"<b>Ваша конфигурация:</b>\n"
                f"<code>{subscription['subscription_url']}</code>"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Продлить", callback_data="add_balance")],
                [InlineKeyboardButton(text="👥 Пригласить друга", callback_data="referral")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
            ])
        else:
            text = (
                "<b>📊 Подписка не активна</b>\n\n"
                f"💰 Баланс: <b>{balance:.2f} ₽</b>\n\n"
                "Активируйте VPN или пополните баланс"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Активировать", callback_data="activate_start")],
                [InlineKeyboardButton(text="💳 Пополнить", callback_data="add_balance")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
            ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
    
    async def unknown_command_handler(self, message: Message):
        """Обработка неизвестных команд"""
        text = (
            "❓ <b>Неизвестная команда</b>\n\n"
            "Доступные команды:\n"
            "• /start - Главное меню\n"
            "• /sub - Моя подписка\n"
            "• /invite - Реферальная программа\n\n"
            f"Или обратитесь в поддержку: {self.support_username}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")],
            [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{self.support_username[1:]}")],
        ])
        
        await message.answer(text, reply_markup=keyboard)
    
    def register_handlers(self, dp: Dispatcher):
        """Регистрация всех обработчиков"""
        # Команды
        dp.message.register(self.start_command, CommandStart())
        dp.message.register(self.unknown_command_handler, F.text & ~F.text.startswith('/start'))
        
        # Callbacks
        dp.callback_query.register(self.activate_start_callback, F.data == "activate_start")
        dp.callback_query.register(self.platform_selected_callback, F.data.startswith("platform_"))
        dp.callback_query.register(self.app_installed_callback, F.data == "app_installed")
        dp.callback_query.register(self.my_subscription_callback, F.data == "my_subscription")
        
        logger.info("✅ Обработчики текстового режима зарегистрированы")
