"""
Обработчик настроек
Управление настройками пользователя и системными параметрами
"""

import logging
from aiogram import Dispatcher
from aiogram.types import CallbackQuery, Message
from aiogram import F

from assets.emojis.interface import EMOJI

logger = logging.getLogger(__name__)

async def handle_settings(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "Настройки"
    
    Показывает меню настроек пользователя
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем сервисы
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        user_service = services.get_user_service()
        ui_service = services.get_ui_service()
        
        # Получаем данные пользователя
        user = await user_service.get_or_create_user(
            user_id=user_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name or "Пользователь"
        )
        
        settings = user.get('settings', {})
        notifications = settings.get('notifications', True)
        auto_renewal = settings.get('auto_renewal', True)
        
        message_text = f"""
⚙️ <b>Настройки</b>

🔔 <b>Уведомления:</b> {'Включены' if notifications else 'Отключены'}
🔄 <b>Автопродление:</b> {'Включено' if auto_renewal else 'Отключено'}
🌐 <b>Язык:</b> Русский
📱 <b>Версия бота:</b> 2.0.0

<b>Доступные настройки:</b>
• 🔔 Управление уведомлениями
• 🔄 Настройка автопродления
• ℹ️ Информация о боте
• 🆘 Поддержка

<b>💡 Совет:</b> Рекомендуем оставить уведомления включенными для получения важных сообщений
        """
        
        keyboard = ui_service.create_settings_keyboard()
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard
        )
        
        await callback.answer()
        logger.info(f"⚙️ Показаны настройки пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_settings: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

async def handle_settings_notifications(callback: CallbackQuery, **kwargs):
    """
    Обработчик настройки уведомлений
    
    Переключает уведомления пользователя
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем сервисы
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        user_service = services.get_user_service()
        
        # Получаем данные пользователя
        user = await user_service.get_or_create_user(
            user_id=user_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name or "Пользователь"
        )
        
        # Переключаем уведомления
        settings = user.get('settings', {})
        current_notifications = settings.get('notifications', True)
        new_notifications = not current_notifications
        
        settings['notifications'] = new_notifications
        user['settings'] = settings
        
        # Сохраняем изменения
        user_service._save_users()
        
        status_text = "включены" if new_notifications else "отключены"
        emoji = EMOJI['notification'] if new_notifications else EMOJI['cross']
        
        await callback.answer(
            f"{emoji} Уведомления {status_text}",
            show_alert=True
        )
        
        logger.info(f"🔔 Уведомления {status_text} для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_settings_notifications: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

async def handle_settings_auto_renewal(callback: CallbackQuery, **kwargs):
    """
    Обработчик настройки автопродления
    
    Переключает автопродление подписки
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем сервисы
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        user_service = services.get_user_service()
        
        # Получаем данные пользователя
        user = await user_service.get_or_create_user(
            user_id=user_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name or "Пользователь"
        )
        
        # Переключаем автопродление
        settings = user.get('settings', {})
        current_auto_renewal = settings.get('auto_renewal', True)
        new_auto_renewal = not current_auto_renewal
        
        settings['auto_renewal'] = new_auto_renewal
        user['settings'] = settings
        
        # Сохраняем изменения
        user_service._save_users()
        
        status_text = "включено" if new_auto_renewal else "отключено"
        emoji = EMOJI['refresh'] if new_auto_renewal else EMOJI['cross']
        
        await callback.answer(
            f"{emoji} Автопродление {status_text}",
            show_alert=True
        )
        
        logger.info(f"🔄 Автопродление {status_text} для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_settings_auto_renewal: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

async def handle_about_bot(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "О боте"
    
    Показывает информацию о боте
    """
    try:
        message_text = f"""
ℹ️ <b>О боте YoVPN</b>

<b>Версия:</b> 2.0.0
<b>Разработчик:</b> YoVPN Team
<b>Язык:</b> Python 3.8+
<b>Фреймворк:</b> aiogram 3.x

<b>Особенности:</b>
• 🔒 Безопасный VPN-доступ
• 💰 Ежедневная оплата (4 ₽/день)
• ⚡ Высокая скорость соединения
• 🛡️ Полная анонимность
• 📱 Простая настройка
• 🔄 Автоматическое продление

<b>Технологии:</b>
• Marzban API для управления VPN
• Асинхронная архитектура
• Современный UX/UI дизайн
• Анимированные эффекты сообщений

<b>Поддержка:</b>
• 📞 Техническая поддержка 24/7
• 📧 Email: support@yovpn.com
• 💬 Telegram: @YoVPNSupport

<b>Лицензия:</b> MIT
<b>Исходный код:</b> GitHub
        """
        
        from bot.services.ui_service import UIService
        ui_service = UIService()
        keyboard = ui_service.create_back_keyboard("settings")
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard
        )
        
        await callback.answer()
        logger.info(f"ℹ️ Показана информация о боте для пользователя {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_about_bot: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

def register_settings_handler(dp: Dispatcher):
    """
    Регистрация обработчиков настроек
    
    Args:
        dp: Диспетчер бота
    """
    dp.callback_query.register(handle_settings, F.data == "settings")
    dp.callback_query.register(handle_settings_notifications, F.data == "settings_notifications")
    dp.callback_query.register(handle_settings_auto_renewal, F.data == "settings_auto_renewal")
    dp.callback_query.register(handle_about_bot, F.data == "about_bot")
    
    logger.info("✅ Обработчики настроек зарегистрированы")