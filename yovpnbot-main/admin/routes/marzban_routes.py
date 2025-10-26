"""
Marzban Management Routes
Управление настройками и синхронизацией с Marzban
"""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
import os

from database import get_db
from database.models import Settings
from api.marzban_api import MarzbanAPI

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


async def get_marzban_client() -> MarzbanAPI:
    """Получить клиент Marzban API"""
    api_url = os.getenv("MARZBAN_API_URL", "http://localhost:8000")
    api_token = os.getenv("MARZBAN_API_TOKEN", "")
    return MarzbanAPI(api_url, api_token)


@router.get("/", response_class=HTMLResponse)
async def marzban_settings(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Настройки Marzban"""
    api_url = os.getenv("MARZBAN_API_URL", "")
    api_token_masked = os.getenv("MARZBAN_API_TOKEN", "")[:10] + "..." if os.getenv("MARZBAN_API_TOKEN") else ""
    
    return templates.TemplateResponse(
        "marzban_settings.html",
        {
            "request": request,
            "api_url": api_url,
            "api_token_masked": api_token_masked,
        }
    )


@router.post("/test")
async def test_connection():
    """Тест соединения с Marzban API"""
    try:
        client = await get_marzban_client()
        is_available = await client.check_api_availability()
        await client.close()
        
        if is_available:
            return JSONResponse({
                "success": True,
                "message": "✅ Соединение с Marzban API установлено успешно"
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "❌ Marzban API недоступен. Проверьте URL и токен."
            }, status_code=500)
    
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"❌ Ошибка: {str(e)}"
        }, status_code=500)


@router.post("/sync")
async def sync_subscriptions(db: AsyncSession = Depends(get_db)):
    """Синхронизация подписок с Marzban"""
    try:
        from database.models import Subscription, User
        
        client = await get_marzban_client()
        
        # Получаем все подписки из Marzban
        marzban_users = await client.get_all_subscriptions()
        
        synced_count = 0
        error_count = 0
        
        for marzban_user in marzban_users:
            try:
                # Ищем подписку в нашей БД
                result = await db.execute(
                    select(Subscription).where(
                        Subscription.marzban_username == marzban_user.username
                    )
                )
                subscription = result.scalar_one_or_none()
                
                if subscription:
                    # Обновляем статус
                    subscription.is_active = marzban_user.status == "active"
                    subscription.used_traffic = marzban_user.used_traffic
                    synced_count += 1
            
            except Exception as e:
                error_count += 1
                continue
        
        await db.commit()
        await client.close()
        
        return JSONResponse({
            "success": True,
            "message": f"✅ Синхронизировано: {synced_count}, ошибок: {error_count}"
        })
    
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"❌ Ошибка синхронизации: {str(e)}"
        }, status_code=500)


@router.get("/users", response_class=HTMLResponse)
async def marzban_users(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Список пользователей в Marzban"""
    try:
        client = await get_marzban_client()
        users = await client.get_all_subscriptions()
        await client.close()
        
        return templates.TemplateResponse(
            "marzban_users.html",
            {
                "request": request,
                "users": users,
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Ошибка получения пользователей: {str(e)}"
            }
        )
