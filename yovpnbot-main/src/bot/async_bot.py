"""
Асинхронный Telegram бот с использованием aiogram
Включает все улучшения UX, безопасности и производительности
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Импорты наших сервисов
from src.services.ux_service import UXService, ResponseType
from src.services.validation_service import ValidationService, ValidationError
from src.services.security_service import SecurityService
from src.services.user_service import UserService
from src.services.marzban_service import MarzbanService
from src.services.animation_service import StickerService
from src.services.ui_service import UIService
from src.services.copy_service import CopyService
from src.services.interaction_service import InteractionService
from src.services.daily_payment_service import DailyPaymentService
from src.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class BotStates(StatesGroup):
    """Состояния FSM"""
    waiting_for_payment_amount = State()
    waiting_for_payment_method = State()
    waiting_for_custom_amount = State()

class AsyncYoVPNBot:
    """Асинхронный YoVPN бот"""
    
    def __init__(self, token: str, marzban_api_url: str, marzban_admin_token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Инициализация сервисов
        self.ux_service = UXService(self.bot)
        self.validation_service = ValidationService()
        self.security_service = SecurityService()
        self.user_service = UserService()
        self.marzban_service = MarzbanService(marzban_api_url, marzban_admin_token)
        self.sticker_service = StickerService(self.bot)
        self.ui_service = UIService()
        self.copy_service = CopyService(self.bot)
        self.interaction_service = InteractionService(self.bot)
        self.notification_service = NotificationService(self.bot)
        self.daily_payment_service = DailyPaymentService(
            self.user_service, 
            self.marzban_service, 
            self.notification_service
        )
        
        # Настройка обработчиков
        self._setup_handlers()
        
        # Запуск фоновых задач
        self.background_tasks = set()

    def _setup_handlers(self):
        """Настройка обработчиков команд и callback'ов"""
        
        # Команды
        self.dp.message.register(self.start_command, CommandStart())
        self.dp.message.register(self.help_command, Command("help"))
        self.dp.message.register(self.balance_command, Command("balance"))
        self.dp.message.register(self.subscription_command, Command("subscription"))
        self.dp.message.register(self.referral_command, Command("referral"))
        
        # Callback queries
        self.dp.callback_query.register(self.handle_callback)
        
        # Сообщения
        self.dp.message.register(self.handle_message)

    async def start_command(self, message: Message, state: FSMContext):
        """Обработка команды /start"""
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        
        # Немедленный отклик
        await self.ux_service.send_immediate_ack(
            message.chat.id, 
            message=f"Привет, {first_name}! Настраиваю ваш аккаунт..."
        )
        
        try:
            # Валидация данных пользователя
            user_data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'language_code': message.from_user.language_code or 'ru'
            }
            
            validated_user = self.validation_service.validate_user_registration(user_data)
            
            # Проверка безопасности
            if not self.security_service.check_suspicious_activity(
                user_id, "start_command", str(user_data)
            ):
                await self.ux_service.send_error_response(
                    message.chat.id, 
                    "E999",
                    message="Обнаружена подозрительная активность"
                )
                return
            
            # Создание пользователя
            user = self.user_service.ensure_user_record(
                validated_user.user_id,
                validated_user.username,
                validated_user.first_name
            )
            
            # Приветственный бонус
            if not user.bonus_given:
                self.user_service.add_balance(user_id, 20)
                self.user_service.update_user_record(user_id, {"bonus_given": True})
                
                # Анимация приветствия
                await self.sticker_service.send_celebration(
                    message.chat.id, 
                    "🎉 Добро пожаловать! Вам начислен приветственный бонус 20 ₽"
                )
                
                self.notification_service.send_welcome_bonus_notification(user_id, 20, 20)
            
            # Показ главного меню
            await self.show_main_menu(message)
            
            # Логирование
            self.ux_service.log_operation(
                "start_command", user_id, f"User: {username}", success=True
            )
            
        except ValidationError as e:
            await self.ux_service.send_error_response(
                message.chat.id, 
                "E001",
                message=f"Ошибка валидации: {e.message}"
            )
        except Exception as e:
            logger.error(f"Ошибка в start_command: {e}")
            await self.ux_service.send_error_response(message.chat.id, "E999")

    async def help_command(self, message: Message):
        """Обработка команды /help"""
        await self.ux_service.send_immediate_ack(
            message.chat.id, 
            message="Загружаю справку..."
        )
        
        help_text = """
🔧 <b>Справка по боту YoVPN</b>

<b>Основные команды:</b>
/start - Начать работу с ботом
/balance - Посмотреть баланс
/subscription - Управление подпиской
/referral - Реферальная программа
/help - Эта справка

<b>Как пользоваться:</b>
1. Пополните баланс (4 ₽/день)
2. Выберите сервер
3. Получите конфигурацию
4. Настройте VPN

<b>Поддержка:</b>
Если возникли вопросы, обратитесь к администратору.

<b>Безопасность:</b>
• Все данные защищены
• Платежи через безопасные шлюзы
• Логирование для отладки
"""
        
        await self.bot.send_message(
            chat_id=message.chat.id,
            text=help_text,
            parse_mode='HTML'
        )

    async def balance_command(self, message: Message):
        """Обработка команды /balance"""
        await self.ux_service.send_immediate_ack(
            message.chat.id,
            message="Загружаю информацию о балансе..."
        )
        
        try:
            await self.show_balance_menu(message)
        except Exception as e:
            logger.error(f"Ошибка в balance_command: {e}")
            await self.ux_service.send_error_response(message.chat.id, "E999")

    async def subscription_command(self, message: Message):
        """Обработка команды /subscription"""
        await self.ux_service.send_immediate_ack(
            message.chat.id,
            message="Загружаю информацию о подписке..."
        )
        
        try:
            await self.show_my_subscriptions(message)
        except Exception as e:
            logger.error(f"Ошибка в subscription_command: {e}")
            await self.ux_service.send_error_response(message.chat.id, "E999")

    async def referral_command(self, message: Message):
        """Обработка команды /referral"""
        await self.ux_service.send_immediate_ack(
            message.chat.id,
            message="Загружаю реферальную программу..."
        )
        
        try:
            await self.show_invite_menu(message)
        except Exception as e:
            logger.error(f"Ошибка в referral_command: {e}")
            await self.ux_service.send_error_response(message.chat.id, "E999")

    async def handle_callback(self, callback_query: CallbackQuery, state: FSMContext):
        """Обработка callback запросов"""
        user_id = callback_query.from_user.id
        data = callback_query.data
        
        # Валидация callback data
        if not self.security_service.validate_callback_data(data):
            await self.ux_service.send_error_response(
                callback_query.message.chat.id,
                "E999",
                message="Некорректные данные запроса"
            )
            return
        
        # Немедленный отклик
        await self.ux_service.send_immediate_ack(
            callback_query.message.chat.id,
            callback_query.id,
            "Обрабатываю запрос..."
        )
        
        try:
            # Обработка различных типов callback'ов
            if data == "back_to_main":
                await self.show_main_menu(callback_query.message)
            elif data == "balance":
                await self.show_balance_menu(callback_query.message)
            elif data == "subscription":
                await self.show_my_subscriptions(callback_query.message)
            elif data == "referral":
                await self.show_invite_menu(callback_query.message)
            elif data.startswith("quick_top_up_"):
                amount = int(data.replace("quick_top_up_", ""))
                await self.handle_quick_top_up(callback_query.message, amount)
            elif data.startswith("pay_"):
                parts = data.split("_")
                payment_method = parts[1]
                amount = int(parts[2])
                await self.handle_payment_method(callback_query.message, payment_method, amount)
            elif data.startswith("simulate_payment_"):
                amount = int(data.replace("simulate_payment_", ""))
                await self.handle_simulate_payment(callback_query.message, amount)
            elif data.startswith("copy_"):
                copy_type = data.replace("copy_", "")
                await self.handle_copy_request(callback_query.message, copy_type)
            elif data.startswith("qr_"):
                qr_type = data.replace("qr_", "")
                await self.handle_qr_request(callback_query.message, qr_type)
            else:
                await self.ux_service.send_error_response(
                    callback_query.message.chat.id,
                    "E999",
                    message="Неизвестная команда"
                )
                
        except Exception as e:
            logger.error(f"Ошибка в handle_callback: {e}")
            await self.ux_service.send_error_response(
                callback_query.message.chat.id,
                "E999"
            )

    async def handle_message(self, message: Message, state: FSMContext):
        """Обработка обычных сообщений"""
        # Здесь можно добавить обработку текстовых сообщений
        # Например, для ввода суммы платежа
        pass

    async def show_main_menu(self, message: Message):
        """Показать главное меню"""
        user_id = message.from_user.id
        user_stats = self.user_service.get_user_stats(user_id)
        
        # Получаем информацию о подписке
        user_info = self.marzban_service.get_user_info(message.from_user.username)
        has_subscription = user_info and user_info.get('status') == 'active'
        
        # Создаем клавиатуру
        keyboard = self.ui_service.create_main_menu_keyboard(user_stats, has_subscription)
        
        # Форматируем сообщение
        text = f"""
🏠 <b>Главное меню</b>

💰 <b>Баланс:</b> {user_stats.get('balance', 0)} ₽
📅 <b>Доступно дней:</b> {user_stats.get('days_remaining', 0)}
🔗 <b>Подписка:</b> {'Активна' if has_subscription else 'Неактивна'}

Выберите действие:
"""
        
        await self.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='HTML',
            reply_markup=keyboard
        )

    async def show_balance_menu(self, message: Message):
        """Показать меню баланса"""
        user_id = message.from_user.id
        balance = self.user_service.get_balance(user_id)
        days = self.user_service.days_from_balance(user_id)
        
        # Создаем клавиатуру
        keyboard = self.ui_service.create_balance_keyboard(balance)
        
        # Форматируем сообщение
        text = self.ui_service.format_balance_message(balance, days)
        
        await self.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='HTML',
            reply_markup=keyboard
        )

    async def show_my_subscriptions(self, message: Message):
        """Показать подписки"""
        user_id = message.from_user.id
        username = message.from_user.username
        
        # Получаем информацию о подписке
        user_info = self.marzban_service.get_user_info(username)
        
        if not user_info:
            # Создаем пользователя если не существует
            if self.user_service.get_balance(user_id) >= 4:
                user_info = self.marzban_service.create_test_user(username, 1)
        
        subscription_info = {
            'status': user_info.get('status', 'inactive') if user_info else 'inactive',
            'expire': user_info.get('expire', 0) if user_info else 0,
            'data_limit': user_info.get('data_limit', 0) if user_info else 0,
            'used_traffic': user_info.get('used_traffic', 0) if user_info else 0
        }
        
        # Форматируем сообщение
        text = self.ui_service.format_subscription_message(subscription_info)
        
        # Создаем клавиатуру
        keyboard = self.ui_service.create_subscription_keyboard(subscription_info)
        
        await self.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='HTML',
            reply_markup=keyboard
        )

    async def show_invite_menu(self, message: Message):
        """Показать реферальное меню"""
        user_id = message.from_user.id
        referral_link = f"https://t.me/your_bot?start=ref_{user_id}"
        
        # Создаем клавиатуру
        keyboard = self.ui_service.create_referral_keyboard(referral_link)
        
        text = f"""
👥 <b>Реферальная программа</b>

🔗 <b>Ваша реферальная ссылка:</b>
<code>{referral_link}</code>

💰 <b>Бонусы:</b>
• За каждого реферала: 10 ₽
• Реферал получает: 5 ₽

📊 <b>Статистика:</b>
• Приглашено: 0 человек
• Заработано: 0 ₽
"""
        
        await self.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='HTML',
            reply_markup=keyboard
        )

    async def handle_quick_top_up(self, message: Message, amount: int):
        """Обработать быстрое пополнение"""
        user_id = message.from_user.id
        
        # Валидация суммы
        try:
            payment_data = {
                'amount': amount,
                'payment_method': 'card',  # По умолчанию
                'user_id': user_id
            }
            validated_payment = self.validation_service.validate_payment_request(payment_data)
        except ValidationError as e:
            await self.ux_service.send_error_response(
                message.chat.id,
                "E004",
                message=f"Некорректная сумма: {e.message}"
            )
            return
        
        # Показываем информацию о выбранной сумме
        days = int(amount / 4)
        
        text = f"""
💳 <b>Выбрана сумма: {amount} ₽</b>

📅 <b>Доступно дней:</b> {days}
💰 <b>Стоимость:</b> 4 ₽/день

⚠️ <b>Внимание!</b> Это демо-режим. 
В реальной версии здесь будет интеграция с платежной системой.

<b>Доступные способы оплаты:</b>
• 💳 Банковская карта
• 📱 СБП (Система быстрых платежей)
• 🏦 Банковский перевод
• 💰 Электронные кошельки
"""
        
        # Создаем клавиатуру
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("💳 Оплатить картой", callback_data=f"pay_card_{amount}"),
            InlineKeyboardButton("📱 СБП", callback_data=f"pay_sbp_{amount}"),
            InlineKeyboardButton("🏦 Банковский перевод", callback_data=f"pay_bank_{amount}"),
            InlineKeyboardButton("💰 Электронные кошельки", callback_data=f"pay_wallet_{amount}")
        )
        keyboard.add(
            InlineKeyboardButton("⬅️ Назад к выбору суммы", callback_data="balance")
        )
        
        await self.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='HTML',
            reply_markup=keyboard
        )

    async def handle_payment_method(self, message: Message, payment_method: str, amount: int):
        """Обработать выбор способа оплаты"""
        # Реализация аналогична синхронной версии
        pass

    async def handle_simulate_payment(self, message: Message, amount: int):
        """Симулировать оплату (только для демо)"""
        user_id = message.from_user.id
        days = int(amount / 4)
        
        # Показываем анимацию платежа
        await self.sticker_service.animate_payment_process(message.chat.id, amount)
        
        # В ДЕМО-РЕЖИМЕ добавляем средства
        self.user_service.add_balance(user_id, amount)
        
        # Отправляем уведомление об успехе
        await self.sticker_service.send_celebration(
            message.chat.id, 
            f"🎉 ДЕМО: Баланс пополнен на {amount} ₽! Доступно {days} дней"
        )
        
        # Показываем обновленную информацию о балансе
        await self.show_balance_menu(message)

    async def handle_copy_request(self, message: Message, copy_type: str):
        """Обработать запрос на копирование"""
        await self.copy_service.handle_copy_request(message, copy_type)

    async def handle_qr_request(self, message: Message, qr_type: str):
        """Обработать запрос на QR-код"""
        await self.copy_service.handle_qr_request(message, qr_type)

    async def start_background_tasks(self):
        """Запуск фоновых задач"""
        # Запуск ежедневного сервиса платежей
        task = asyncio.create_task(self.daily_payment_service.start())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)

    async def stop_background_tasks(self):
        """Остановка фоновых задач"""
        # Останавливаем все фоновые задачи
        for task in self.background_tasks:
            task.cancel()
        
        # Ждем завершения
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)

    async def start(self):
        """Запуск бота"""
        try:
            # Запуск фоновых задач
            await self.start_background_tasks()
            
            # Запуск бота
            logger.info("Запуск асинхронного бота...")
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
        finally:
            # Остановка фоновых задач
            await self.stop_background_tasks()

    async def stop(self):
        """Остановка бота"""
        logger.info("Остановка бота...")
        await self.stop_background_tasks()
        await self.bot.session.close()

# Функция для запуска бота
async def main():
    """Главная функция"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    token = os.getenv('USERBOT_TOKEN')
    marzban_api_url = os.getenv('MARZBAN_API_URL')
    marzban_admin_token = os.getenv('MARZBAN_ADMIN_TOKEN')
    
    if not all([token, marzban_api_url, marzban_admin_token]):
        logger.error("Не все переменные окружения установлены")
        return
    
    bot = AsyncYoVPNBot(token, marzban_api_url, marzban_admin_token)
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())