"""
Обработчик подписок
Управление подписками пользователей, активация и деактивация
"""

import logging
from aiogram import Dispatcher
from aiogram.types import CallbackQuery, Message
from aiogram import F

from assets.emojis.interface import EMOJI, get_emoji_combination

logger = logging.getLogger(__name__)

async def handle_my_subscriptions(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "Мои подписки"
    
    Показывает информацию о подписках пользователя
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем сервисы из контекста
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        user_service = services.get_user_service()
        marzban_service = services.get_marzban_service()
        ui_service = services.get_ui_service()
        
        # Получаем данные пользователя
        user = await user_service.get_or_create_user(
            user_id=user_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name or "Пользователь"
        )
        
        # Получаем статистику
        stats = await user_service.get_user_stats(user_id)
        balance = stats.get('balance', 0.0)
        subscription_active = stats.get('subscription_active', False)
        subscription_days = stats.get('subscription_days', 0)
        
        # Форматируем сообщение
        message_text = ui_service.format_user_balance_message(
            balance=balance,
            days=subscription_days,
            subscription_active=subscription_active
        )
        
        # Создаем клавиатуру
        keyboard = ui_service.create_subscription_menu_keyboard(
            has_active_subscription=subscription_active
        )
        
        # Отправляем сообщение
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard
        )
        
        await callback.answer()
        logger.info(f"📱 Показаны подписки пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_my_subscriptions: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

async def handle_activate_subscription(callback: CallbackQuery, **kwargs):
    """
    Обработчик активации подписки
    
    Активирует подписку пользователя если есть достаточный баланс
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем сервисы
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        user_service = services.get_user_service()
        marzban_service = services.get_marzban_service()
        animation_service = services.get_animation_service()
        
        # Проверяем доступность Marzban API
        if not await marzban_service.check_api_availability():
            await callback.answer(
                "❌ Сервис VPN временно недоступен. Попробуйте позже.",
                show_alert=True
            )
            return
        
        # Проверяем баланс
        balance = await user_service.get_user_balance(user_id)
        if balance < 4.0:
            await callback.answer(
                "❌ Недостаточно средств. Минимум 4 ₽ для активации подписки.",
                show_alert=True
            )
            return
        
        # Рассчитываем количество дней на основе баланса (4₽ = 1 день)
        days = int(balance / 4)
        
        logger.info(f"💰 Баланс пользователя {user_id}: {balance}₽, доступно дней: {days}")
        
        # Получаем данные пользователя
        user = await user_service.get_or_create_user(
            user_id=user_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name or "Пользователь"
        )
        
        # Формируем имя пользователя для Marzban (по username телеграма)
        tg_username = callback.from_user.username
        if tg_username:
            marzban_username = tg_username.lstrip('@')
        else:
            marzban_username = f"user_{user_id}"
        
        logger.info(f"🔄 Создание/обновление пользователя {marzban_username} в Marzban")
        
        # Проверяем, существует ли уже пользователь
        existing_user = await marzban_service.get_user(marzban_username)
        
        if existing_user:
            # Обновляем существующего пользователя (продлеваем подписку)
            logger.info(f"👤 Пользователь {marzban_username} уже существует, обновляем...")
            
            import time
            from datetime import datetime, timedelta
            
            # Рассчитываем новую дату истечения
            expire_timestamp = int((datetime.now() + timedelta(days=days)).timestamp())
            
            update_result = await marzban_service.update_user(marzban_username, {
                'expire': expire_timestamp,
                'status': 'active',
                'note': f"Обновлено через YoVPN Bot - {days} дней"
            })
            
            if update_result:
                # Активируем подписку
                await user_service.activate_subscription(user_id, days)
                
                # Отправляем сообщение об успехе
                await animation_service.send_subscription_activated(
                    callback.message, 
                    days
                )
                
                logger.info(f"✅ Подписка продлена для {user_id}: {days} дней")
            else:
                await callback.answer(
                    "❌ Ошибка обновления пользователя в Marzban. Попробуйте позже.",
                    show_alert=True
                )
        else:
            # Создаем нового пользователя с VLESS TCP REALITY
            marzban_user = await marzban_service.create_user(marzban_username, {
                'days': days,  # Передаем количество дней
                'data_limit': 0,  # Безлимит трафика
                'status': 'active',
                'note': f"Telegram ID: {user_id}"
            })
            
            if marzban_user:
                # Активируем подписку
                await user_service.activate_subscription(user_id, days)
                
                # Отправляем сообщение об успехе с эффектом
                await animation_service.send_subscription_activated(
                    callback.message, 
                    days
                )
                
                logger.info(f"✅ Подписка активирована для пользователя {user_id}: {days} дней")
            else:
                await callback.answer(
                    "❌ Ошибка создания пользователя в Marzban. Проверьте настройки inbounds (VLESS TCP REALITY).",
                    show_alert=True
                )
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_activate_subscription: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await callback.answer("❌ Произошла ошибка при активации. Обратитесь в поддержку.", show_alert=True)

async def handle_setup_vpn(callback: CallbackQuery, **kwargs):
    """
    Обработчик настройки VPN
    
    Показывает инструкции по настройке VPN
    """
    try:
        message_text = f"""
📱 <b>Настройка VPN</b>

<b>Выберите ваше устройство:</b>

<b>📱 Мобильные устройства:</b>
• <b>Android:</b> Скачайте приложение V2rayNG
• <b>iOS:</b> Скачайте приложение OneClick

<b>💻 Компьютеры:</b>
• <b>Windows:</b> Скачайте V2rayN
• <b>macOS:</b> Скачайте V2rayU
• <b>Linux:</b> Используйте v2ray-core

<b>🔗 Получение конфигурации:</b>
1. Нажмите "Скопировать ссылку"
2. Вставьте в приложение
3. Подключитесь к серверу

<b>❓ Нужна помощь?</b> Обратитесь в поддержку 👇
        """
        
        from bot.services.ui_service import UIService
        ui_service = UIService()
        keyboard = ui_service.create_back_keyboard("my_subscriptions")
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard
        )
        
        await callback.answer()
        logger.info(f"📱 Показана инструкция по настройке VPN для пользователя {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_setup_vpn: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

async def handle_copy_config(callback: CallbackQuery, **kwargs):
    """
    Обработчик копирования конфигурации
    
    Показывает ссылки для копирования
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем сервисы
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        marzban_service = services.get_marzban_service()
        ui_service = services.get_ui_service()
        
        # Получаем данные пользователя
        user = await services.get_user_service().get_user(user_id)
        
        username = user.get('username', f"user_{user_id}")
        
        # Получаем конфигурацию
        config_data = await marzban_service.get_user_config(username)
        if not config_data:
            await callback.answer("❌ Конфигурация не найдена", show_alert=True)
            return
        
        message_text = f"""
🔗 <b>Конфигурация VPN</b>

<b>VLESS ссылка:</b>
<code>{config_data['vless_url']}</code>

<b>Subscription URL:</b>
<code>{config_data['subscription_url']}</code>

<b>📋 Инструкция:</b>
1. Скопируйте одну из ссылок выше
2. Вставьте в ваше VPN приложение
3. Подключитесь к серверу

<b>💡 Совет:</b> Используйте VLESS ссылку для быстрой настройки
        """
        
        keyboard = ui_service.create_back_keyboard("my_subscriptions")
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard
        )
        
        await callback.answer()
        logger.info(f"🔗 Показана конфигурация для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_copy_config: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

def register_subscription_handler(dp: Dispatcher):
    """
    Регистрация обработчиков подписок
    
    Args:
        dp: Диспетчер бота
    """
    dp.callback_query.register(handle_my_subscriptions, F.data == "my_subscriptions")
    dp.callback_query.register(handle_activate_subscription, F.data == "activate_subscription")
    dp.callback_query.register(handle_setup_vpn, F.data == "setup_vpn")
    dp.callback_query.register(handle_copy_config, F.data == "copy_config")
    
    logger.info("✅ Обработчики подписок зарегистрированы")