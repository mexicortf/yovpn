"""
Broadcast Routes
Управление рассылками
"""

from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from typing import Optional
import os
import aiofiles

from database import get_db
from database.models import User

router = APIRouter()

# Настраиваем шаблоны
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Директория для загрузки изображений
UPLOAD_DIR = BASE_DIR / "static" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/", response_class=HTMLResponse)
async def broadcast_form(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Форма для создания рассылки"""
    # Получаем количество активных пользователей
    result = await db.execute(
        select(User).where(User.is_blocked == False)
    )
    active_users = result.scalars().all()
    
    return templates.TemplateResponse(
        "broadcast_form.html",
        {
            "request": request,
            "total_users": len(active_users),
        }
    )


@router.post("/send")
async def send_broadcast(
    message: str = Form(...),
    image: Optional[UploadFile] = File(None),
    button_text: Optional[str] = Form(None),
    button_url: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Отправить рассылку"""
    import asyncio
    from aiogram import Bot
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    # Получаем токен бота
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise HTTPException(status_code=500, detail="BOT_TOKEN not configured")
    
    bot = Bot(token=bot_token)
    
    # Сохраняем изображение если есть
    image_path = None
    if image and image.filename:
        image_path = UPLOAD_DIR / image.filename
        async with aiofiles.open(image_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
    
    # Создаем клавиатуру если есть кнопка
    keyboard = None
    if button_text and button_url:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=button_text, url=button_url)]
        ])
    
    # Получаем всех активных пользователей
    result = await db.execute(
        select(User).where(User.is_blocked == False)
    )
    users = result.scalars().all()
    
    # Отправляем сообщения
    success_count = 0
    failed_count = 0
    
    for user in users:
        try:
            if image_path:
                with open(image_path, 'rb') as photo:
                    await bot.send_photo(
                        chat_id=user.tg_id,
                        photo=photo,
                        caption=message,
                        reply_markup=keyboard
                    )
            else:
                await bot.send_message(
                    chat_id=user.tg_id,
                    text=message,
                    reply_markup=keyboard
                )
            success_count += 1
            # Небольшая задержка для избежания флуда
            await asyncio.sleep(0.05)
        except Exception as e:
            failed_count += 1
            print(f"Failed to send to {user.tg_id}: {e}")
    
    await bot.session.close()
    
    return templates.TemplateResponse(
        "broadcast_result.html",
        {
            "request": request,
            "success_count": success_count,
            "failed_count": failed_count,
            "total": len(users),
        }
    )
