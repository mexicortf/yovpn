"""
Обработчик платежей
Управление пополнением баланса и обработка платежей
"""

import logging
from aiogram import Dispatcher
from aiogram.types import CallbackQuery, Message
from aiogram import F

from assets.emojis.interface import EMOJI, format_balance

logger = logging.getLogger(__name__)

async def handle_top_up(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "Пополнить"
    
    Показывает опции пополнения баланса
    """
    user_id = callback.from_user.id
    
    try:
        # Получаем сервисы из middleware
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        user_service = services.get_user_service()
        ui_service = services.get_ui_service()
        
        # Получаем текущий баланс
        balance = await user_service.get_user_balance(user_id)
        
        message_text = f"""
💳 <b>Пополнение баланса</b>

💰 <b>Текущий баланс:</b> {format_balance(balance)}
📅 <b>Дней доступа:</b> {int(balance / 4)} дней

<b>Выберите сумму для пополнения:</b>

💡 <b>Рекомендуем:</b> 120 ₽ за 30 дней
🔄 <b>Продление:</b> Автоматическое
⚡ <b>Активация:</b> Мгновенная
        """
        
        # Создаем клавиатуру с суммами
        keyboard = ui_service.create_payment_keyboard([40, 80, 120, 200, 400])
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard
        )
        
        await callback.answer()
        logger.info(f"💳 Показаны опции пополнения для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_top_up: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

async def handle_payment_amount(callback: CallbackQuery, **kwargs):
    """
    Обработчик выбора суммы платежа
    
    Обрабатывает callback с суммой платежа (pay_40, pay_80, etc.)
    """
    user_id = callback.from_user.id
    callback_data = callback.data
    
    try:
        # Извлекаем сумму из callback_data (pay_40 -> 40)
        amount = float(callback_data.replace("pay_", ""))
        
        # Получаем сервисы
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        ui_service = services.get_ui_service()
        payment_service = services.get_payment_service()
        
        # Форматируем сообщение с опциями платежа
        message_text = ui_service.format_payment_options(amount)
        
        # Создаем клавиатуру способов оплаты
        keyboard = ui_service.create_payment_methods_keyboard()
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard
        )
        
        await callback.answer()
        logger.info(f"💰 Выбрана сумма {amount} ₽ для пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_payment_amount: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

async def handle_payment_method(callback: CallbackQuery, **kwargs):
    """
    Обработчик выбора способа оплаты
    
    Обрабатывает выбор способа оплаты (pay_method_card, etc.)
    """
    user_id = callback.from_user.id
    callback_data = callback.data
    
    try:
        # Извлекаем способ оплаты из callback_data
        method = callback_data.replace("pay_method_", "")
        
        # Получаем сервисы
        services = kwargs.get("services")
        if not services:
            await callback.answer("❌ Сервисы недоступны", show_alert=True)
            return
        
        payment_service = services.get_payment_service()
        animation_service = services.get_animation_service()
        
        # В реальной системе здесь была бы интеграция с платежными системами
        # Пока используем демо-режим
        if method == "demo":
            # Получаем сумму из предыдущего сообщения (упрощенно)
            amount = 120.0  # В реальной системе это должно передаваться через состояние
            
            # Обрабатываем платеж
            result = await payment_service.process_payment(
                user_id=user_id,
                amount=amount,
                payment_method="demo"
            )
            
            if result['success']:
                # Отправляем сообщение об успехе с эффектом
                await animation_service.send_payment_success(
                    callback.message,
                    result['amount'],
                    result['days_added']
                )
                
                logger.info(f"✅ Платеж обработан для пользователя {user_id}: {result['amount']} ₽")
            else:
                await callback.answer(
                    f"❌ Ошибка обработки платежа: {result['error']}",
                    show_alert=True
                )
        else:
            # Для других способов оплаты показываем сообщение о разработке
            message_text = f"""
🚧 <b>Способ оплаты в разработке</b>

<b>Выбранный способ:</b> {method.title()}
📅 <b>Статус:</b> В разработке

<b>Доступные способы:</b>
• 💳 Демо-режим (тестирование)
• 🔄 Автопополнение (скоро)

<b>Что делать:</b>
• Используйте демо-режим для тестирования
• Следите за обновлениями
• Обратитесь в поддержку
            """
            
            from bot.services.ui_service import UIService
            ui_service = UIService()
            keyboard = ui_service.create_back_keyboard("top_up")
            
            await callback.message.edit_text(
                message_text,
                reply_markup=keyboard
            )
            
            await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_payment_method: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

async def handle_my_balance(callback: CallbackQuery, **kwargs):
    """
    Обработчик кнопки "Мой баланс"
    
    Показывает детальную информацию о балансе
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
        
        balance = user.get('balance', 0.0)
        total_payments = user.get('total_payments', 0.0)
        days = int(balance / 4)
        
        message_text = f"""
💰 <b>Детальная информация о балансе</b>

💵 <b>Текущий баланс:</b> {format_balance(balance)}
📅 <b>Дней доступа:</b> {days} дней
💳 <b>Всего пополнено:</b> {total_payments:.2f} ₽
🔄 <b>Последнее обновление:</b> Сейчас

<b>Расчет стоимости:</b>
• 1 день = 4 ₽
• 7 дней = 28 ₽
• 30 дней = 120 ₽
• 365 дней = 1460 ₽

<b>Автоматическое продление:</b>
• Списание каждый день в 00:00
• Уведомления за 24 часа до окончания
• Приостановка при недостатке средств
        """
        
        keyboard = ui_service.create_back_keyboard("main_menu")
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard
        )
        
        await callback.answer()
        logger.info(f"💰 Показан баланс пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_my_balance: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

def register_payment_handler(dp: Dispatcher):
    """
    Регистрация обработчиков платежей
    
    Args:
        dp: Диспетчер бота
    """
    dp.callback_query.register(handle_top_up, F.data == "top_up")
    dp.callback_query.register(handle_my_balance, F.data == "my_balance")
    
    # Регистрируем обработчики для сумм платежей
    for amount in [40, 80, 120, 200, 400]:
        dp.callback_query.register(handle_payment_amount, F.data == f"pay_{amount}")
    
    # Регистрируем обработчики способов оплаты
    for method in ["card", "yoomoney", "crypto", "demo"]:
        dp.callback_query.register(handle_payment_method, F.data == f"pay_method_{method}")
    
    logger.info("✅ Обработчики платежей зарегистрированы")