"""
Admin Routes
Основные роуты админ панели
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from database import get_db

router = APIRouter()

# Настраиваем шаблоны
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def admin_home(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Главная страница админки"""
    from database.models import User, Subscription, Transaction
    from sqlalchemy import select, func
    
    # Получаем статистику
    total_users = await db.scalar(select(func.count(User.id)))
    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_blocked == False)
    )
    active_subscriptions = await db.scalar(
        select(func.count(Subscription.id)).where(Subscription.is_active == True)
    )
    total_balance = await db.scalar(select(func.sum(User.balance))) or 0
    total_transactions = await db.scalar(select(func.count(Transaction.id)))
    
    # Получаем последних пользователей
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(10)
    )
    recent_users = result.scalars().all()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_users": total_users or 0,
            "active_users": active_users or 0,
            "active_subscriptions": active_subscriptions or 0,
            "total_balance": total_balance,
            "total_transactions": total_transactions or 0,
            "recent_users": recent_users,
        }
    )


@router.get("/stats/json", response_class=JSONResponse)
async def admin_stats_json(db: AsyncSession = Depends(get_db)):
    """Получить статистику в JSON"""
    from database.models import User, Subscription, Transaction
    from sqlalchemy import select, func
    
    total_users = await db.scalar(select(func.count(User.id)))
    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_blocked == False)
    )
    active_subscriptions = await db.scalar(
        select(func.count(Subscription.id)).where(Subscription.is_active == True)
    )
    total_balance = await db.scalar(select(func.sum(User.balance))) or 0
    total_transactions = await db.scalar(select(func.count(Transaction.id)))
    
    return {
        "total_users": total_users or 0,
        "active_users": active_users or 0,
        "active_subscriptions": active_subscriptions or 0,
        "total_balance": float(total_balance),
        "total_transactions": total_transactions or 0,
    }
