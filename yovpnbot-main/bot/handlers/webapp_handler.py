"""
WebApp Handler for YoVPN Bot
Handles the integration between Telegram Bot and WebApp
"""

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from bot.handlers.webapp_handler import add_webapp_to_main_menu

commands = await add_webapp_to_main_menu()
await bot.set_my_commands(commands)

router = Router()

# WebApp URL (замените на ваш актуальный URL после деплоя)
WEBAPP_URL = "https://webapp-production-5fe6.up.railway.app"  # или для разработки: http://localhost:3000


@router.message(Command("webapp"))
async def cmd_webapp(message: types.Message):
    """
    Команда для открытия WebApp
    /webapp - открывает WebApp для активации подписки
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть WebApp",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Помощь",
                    callback_data="help_webapp"
                )
            ]
        ]
    )
    
    await message.answer(
        "📱 <b>Активация подписки через WebApp</b>\n\n"
        "Нажмите кнопку ниже, чтобы:\n"
        "1️⃣ Выбрать платформу (Android, iOS, macOS, Windows, Android TV)\n"
        "2️⃣ Скачать приложение v2raytun\n"
        "3️⃣ Активировать подписку в 1 клик\n\n"
        "✨ Всё быстро и удобно!",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "help_webapp")
async def callback_help_webapp(callback: types.CallbackQuery):
    """Помощь по WebApp"""
    await callback.answer()
    
    await callback.message.answer(
        "📖 <b>Как пользоваться WebApp:</b>\n\n"
        "1️⃣ <b>Выбор платформы</b>\n"
        "   Выберите устройство, на которое хотите установить v2raytun\n\n"
        "2️⃣ <b>Скачивание</b>\n"
        "   Нажмите кнопку скачивания для вашей платформы\n\n"
        "3️⃣ <b>Активация</b>\n"
        "   Нажмите кнопку активации - URI будет скопирован автоматически\n"
        "   и приложение откроется с вашей подпиской\n\n"
        "❓ Если есть проблемы - напишите /support",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "open_webapp")
async def callback_open_webapp(callback: types.CallbackQuery):
    """Кнопка для открытия WebApp из других меню"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть WebApp",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )
    
    await callback.message.edit_text(
        "📱 Нажмите кнопку ниже, чтобы открыть WebApp для активации подписки:",
        reply_markup=keyboard
    )
    await callback.answer()


# Можно добавить в главное меню бота
async def add_webapp_to_main_menu():
    """
    Функция для добавления WebApp в главное меню бота
    Вызовите её в start_handler.py или main.py
    """
    from aiogram.types import BotCommand
    
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="webapp", description="🚀 Активировать подписку (WebApp)"),
        BotCommand(command="subscription", description="📊 Моя подписка"),
        BotCommand(command="support", description="💬 Поддержка"),
    ]
    
    return commands
