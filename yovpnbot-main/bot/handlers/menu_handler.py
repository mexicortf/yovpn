"""
Обработчик главного меню
Современный унифицированный интерфейс
"""

import logging
from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram import F

logger = logging.getLogger(__name__)


async def handle_main_menu(callback: CallbackQuery, **kwargs):
    """
    Обработчик возврата в главное меню
    
    Унифицированный стиль с /start
    Современный дизайн 2025-2026
    """
    user_id = callback.from_user.id
    first_name = callback.from_user.first_name or "Пользователь"
    
    try:
        # Получаем сервисы из middleware
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        user_service = services.get_user_service()
        
        # Импортируем модули для текстов и клавиатур
        from bot.utils.texts import get_main_menu_text
        from bot.keyboards.menu_kb import MenuKeyboards
        
        # Получаем данные пользователя
        user = await user_service.get_or_create_user(
            user_id=user_id,
            username=callback.from_user.username,
            first_name=first_name
        )
        
        # Получаем статистику
        stats = await user_service.get_user_stats(user_id)
        balance = stats.get('balance', 0.0)
        subscription_days = stats.get('subscription_days', 0)
        subscription_active = stats.get('subscription_active', False)
        
        # Формируем текст главного меню
        message_text = get_main_menu_text(
            first_name=first_name,
            balance=balance,
            subscription_days=subscription_days,
            subscription_active=subscription_active
        )
        
        # Создаем клавиатуру главного меню
        keyboard = MenuKeyboards.get_main_menu()
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await callback.answer()
        logger.info(f"🏠 Показано главное меню для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_main_menu: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


async def handle_stats(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "Статистика"
    Современный дизайн с красивым форматированием
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем сервисы из middleware
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        user_service = services.get_user_service()
        
        # Импортируем модули
        from bot.utils.texts import get_stats_text
        from bot.keyboards.menu_kb import MenuKeyboards
        
        # Получаем статистику
        stats = await user_service.get_user_stats(user_id)
        
        # Формируем текст статистики
        message_text = get_stats_text(stats)
        
        # Создаем клавиатуру "Назад"
        keyboard = MenuKeyboards.get_back_button("main_menu", "🏠 Главное меню")
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await callback.answer()
        logger.info(f"📊 Показана статистика пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_stats: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


async def handle_referrals(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "Рефералы"
    Современный дизайн реферальной программы
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем сервисы из middleware
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        user_service = services.get_user_service()
        
        # Импортируем модули
        from bot.utils.texts import get_referrals_text
        from bot.keyboards.menu_kb import MenuKeyboards
        
        # Получаем данные пользователя
        user = await user_service.get_or_create_user(
            user_id=user_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name or "Пользователь"
        )
        
        # Получаем статистику рефералов
        stats = await user_service.get_user_stats(user_id)
        referrals_count = stats.get('referrals_count', 0)
        referral_code = user.get('referral_code', f"ref_{user_id}")
        
        # Создаем реферальную ссылку
        bot_me = await callback.bot.get_me()
        bot_username = bot_me.username
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        # Формируем текст
        message_text = get_referrals_text(
            referrals_count=referrals_count,
            referral_code=referral_code,
            referral_link=referral_link
        )
        
        # Создаем клавиатуру
        keyboard = MenuKeyboards.get_referral_menu()
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await callback.answer()
        logger.info(f"🎁 Показана реферальная программа для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_referrals: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


async def handle_settings(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "Настройки"
    """
    try:
        from bot.utils.texts import get_settings_text
        from bot.keyboards.menu_kb import MenuKeyboards
        
        message_text = get_settings_text()
        keyboard = MenuKeyboards.get_settings_menu()
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await callback.answer()
        logger.info(f"⚙️ Показаны настройки для пользователя {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_settings: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


async def handle_support(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "Поддержка"
    """
    try:
        from bot.utils.texts import get_support_text
        from bot.keyboards.menu_kb import MenuKeyboards
        
        message_text = get_support_text()
        keyboard = MenuKeyboards.get_support_menu()
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await callback.answer()
        logger.info(f"🆘 Показана поддержка для пользователя {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_support: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


async def handle_subscriptions(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "Мои подписки"
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем сервисы из middleware
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        user_service = services.get_user_service()
        
        # Импортируем модули
        from bot.utils.texts import get_subscriptions_text
        from bot.keyboards.menu_kb import MenuKeyboards
        
        # Получаем статистику
        stats = await user_service.get_user_stats(user_id)
        subscription_active = stats.get('subscription_active', False)
        subscription_days = stats.get('subscription_days', 0)
        
        # Формируем текст
        message_text = get_subscriptions_text(
            has_active=subscription_active,
            days_left=subscription_days
        )
        
        # Создаем клавиатуру
        keyboard = MenuKeyboards.get_subscription_menu(has_active=subscription_active)
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await callback.answer()
        logger.info(f"📱 Показаны подписки для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_subscriptions: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


async def handle_topup(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "Пополнить баланс"
    """
    try:
        from bot.utils.texts import get_topup_text
        from bot.keyboards.menu_kb import MenuKeyboards
        
        message_text = get_topup_text()
        keyboard = MenuKeyboards.get_payment_amounts()
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await callback.answer()
        logger.info(f"💎 Показано пополнение для пользователя {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_topup: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


def register_menu_handlers(dp: Dispatcher):
    """
    Регистрация всех обработчиков меню
    
    Args:
        dp: Диспетчер бота
    """
    # Главное меню
    dp.callback_query.register(handle_main_menu, F.data == "main_menu")
    
    # Основные разделы
    dp.callback_query.register(handle_subscriptions, F.data == "my_subscriptions")
    dp.callback_query.register(handle_topup, F.data == "top_up")
    dp.callback_query.register(handle_referrals, F.data == "referrals")
    dp.callback_query.register(handle_stats, F.data == "stats")
    dp.callback_query.register(handle_settings, F.data == "settings")
    dp.callback_query.register(handle_support, F.data == "support")
    
    logger.info("✅ Обработчики меню зарегистрированы")
