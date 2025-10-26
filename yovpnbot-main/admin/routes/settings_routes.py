"""
Settings Routes
Управление настройками бота
"""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path

from database import get_db
from database.models import Settings

router = APIRouter()

# Настраиваем шаблоны
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


async def get_setting(db: AsyncSession, key: str, default: str = "") -> str:
    """Получить значение настройки"""
    result = await db.execute(
        select(Settings).where(Settings.key == key)
    )
    setting = result.scalar_one_or_none()
    return setting.value if setting else default


async def set_setting(db: AsyncSession, key: str, value: str, description: str = None):
    """Установить значение настройки"""
    result = await db.execute(
        select(Settings).where(Settings.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = value
        if description:
            setting.description = description
    else:
        setting = Settings(key=key, value=value, description=description)
        db.add(setting)
    
    await db.commit()


@router.get("/", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Страница настроек"""
    # Получаем все настройки
    result = await db.execute(select(Settings))
    all_settings = result.scalars().all()
    
    # Создаем словарь настроек
    settings_dict = {s.key: s.value for s in all_settings}
    
    # Дефолтные настройки если их нет
    default_settings = {
        "maintenance_mode": "false",
        "webapp_enabled": "true",
        "welcome_bonus": "12",
        "daily_price": "4",
        "referral_bonus": "8",
        "min_deposit": "40",
        "support_username": "@YoVPNSupport",
        "channel_username": "@YoVPN",
    }
    
    # Объединяем с дефолтными
    for key, value in default_settings.items():
        if key not in settings_dict:
            settings_dict[key] = value
    
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "settings": settings_dict,
        }
    )


@router.post("/update")
async def update_settings(
    request: Request,
    maintenance_mode: str = Form("false"),
    webapp_enabled: str = Form("false"),
    welcome_bonus: str = Form("12"),
    daily_price: str = Form("4"),
    referral_bonus: str = Form("8"),
    min_deposit: str = Form("40"),
    support_username: str = Form("@YoVPNSupport"),
    channel_username: str = Form("@YoVPN"),
    db: AsyncSession = Depends(get_db)
):
    """Обновить настройки"""
    
    # Обновляем все настройки
    await set_setting(db, "maintenance_mode", maintenance_mode, "Режим техобслуживания")
    await set_setting(db, "webapp_enabled", webapp_enabled, "Включен ли WebApp режим")
    await set_setting(db, "welcome_bonus", welcome_bonus, "Приветственный бонус в рублях")
    await set_setting(db, "daily_price", daily_price, "Цена за день в рублях")
    await set_setting(db, "referral_bonus", referral_bonus, "Бонус за реферала в рублях")
    await set_setting(db, "min_deposit", min_deposit, "Минимальное пополнение в рублях")
    await set_setting(db, "support_username", support_username, "Username поддержки")
    await set_setting(db, "channel_username", channel_username, "Username канала")
    
    return RedirectResponse(url="/admin/settings?updated=true", status_code=303)


@router.post("/mode/maintenance")
async def toggle_maintenance(
    db: AsyncSession = Depends(get_db)
):
    """Переключить режим техобслуживания"""
    current = await get_setting(db, "maintenance_mode", "false")
    new_value = "false" if current == "true" else "true"
    await set_setting(db, "maintenance_mode", new_value, "Режим техобслуживания")
    
    return RedirectResponse(url="/admin/settings", status_code=303)


@router.post("/mode/webapp")
async def toggle_webapp(
    db: AsyncSession = Depends(get_db)
):
    """Переключить режим WebApp"""
    current = await get_setting(db, "webapp_enabled", "true")
    new_value = "false" if current == "true" else "true"
    await set_setting(db, "webapp_enabled", new_value, "WebApp режим")
    
    return RedirectResponse(url="/admin/settings", status_code=303)
