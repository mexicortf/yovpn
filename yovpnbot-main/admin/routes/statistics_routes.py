"""
Statistics Routes
Детальная статистика по разным разделам
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pathlib import Path
from datetime import datetime, timedelta

from database import get_db
from database.models import User, Subscription, Transaction, TransactionType

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def statistics_overview(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Общая статистика"""
    
    # Пользователи
    total_users = await db.scalar(select(func.count(User.id)))
    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_blocked == False)
    )
    new_users_today = await db.scalar(
        select(func.count(User.id)).where(
            User.created_at >= datetime.now() - timedelta(days=1)
        )
    )
    
    # Подписки
    active_subscriptions = await db.scalar(
        select(func.count(Subscription.id)).where(Subscription.is_active == True)
    )
    total_subscriptions = await db.scalar(select(func.count(Subscription.id)))
    
    # Финансы
    total_balance = await db.scalar(select(func.sum(User.balance))) or 0
    
    # Транзакции за сегодня
    today_transactions = await db.scalar(
        select(func.count(Transaction.id)).where(
            Transaction.created_at >= datetime.now() - timedelta(days=1)
        )
    )
    
    # Доход за сегодня
    today_income = await db.scalar(
        select(func.sum(Transaction.amount)).where(
            Transaction.created_at >= datetime.now() - timedelta(days=1),
            Transaction.type == TransactionType.DEPOSIT
        )
    ) or 0
    
    # Рефералы
    total_referrals = await db.scalar(
        select(func.sum(User.referral_count))
    ) or 0
    
    referral_earnings = await db.scalar(
        select(func.sum(User.referral_earnings))
    ) or 0
    
    return templates.TemplateResponse(
        "statistics_overview.html",
        {
            "request": request,
            "total_users": total_users or 0,
            "active_users": active_users or 0,
            "new_users_today": new_users_today or 0,
            "active_subscriptions": active_subscriptions or 0,
            "total_subscriptions": total_subscriptions or 0,
            "total_balance": total_balance,
            "today_transactions": today_transactions or 0,
            "today_income": today_income,
            "total_referrals": total_referrals,
            "referral_earnings": referral_earnings,
        }
    )


@router.get("/users", response_class=HTMLResponse)
async def statistics_users(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Статистика по пользователям"""
    
    # Общие показатели
    total_users = await db.scalar(select(func.count(User.id)))
    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_blocked == False)
    )
    blocked_users = await db.scalar(
        select(func.count(User.id)).where(User.is_blocked == True)
    )
    
    # По периодам
    periods = {
        'today': datetime.now() - timedelta(days=1),
        'week': datetime.now() - timedelta(days=7),
        'month': datetime.now() - timedelta(days=30),
    }
    
    new_users = {}
    for period_name, period_start in periods.items():
        count = await db.scalar(
            select(func.count(User.id)).where(User.created_at >= period_start)
        )
        new_users[period_name] = count or 0
    
    # Топ рефереров
    result = await db.execute(
        select(User).where(User.referral_count > 0).order_by(User.referral_count.desc()).limit(10)
    )
    top_referrers = result.scalars().all()
    
    return templates.TemplateResponse(
        "statistics_users.html",
        {
            "request": request,
            "total_users": total_users or 0,
            "active_users": active_users or 0,
            "blocked_users": blocked_users or 0,
            "new_users": new_users,
            "top_referrers": top_referrers,
        }
    )


@router.get("/finance", response_class=HTMLResponse)
async def statistics_finance(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Статистика по финансам"""
    
    # Общий баланс
    total_balance = await db.scalar(select(func.sum(User.balance))) or 0
    
    # Транзакции по типам
    transaction_stats = {}
    for trans_type in TransactionType:
        count = await db.scalar(
            select(func.count(Transaction.id)).where(Transaction.type == trans_type)
        )
        amount = await db.scalar(
            select(func.sum(Transaction.amount)).where(Transaction.type == trans_type)
        ) or 0
        transaction_stats[trans_type.value] = {'count': count or 0, 'amount': amount}
    
    # Доход по периодам
    periods = {
        'today': datetime.now() - timedelta(days=1),
        'week': datetime.now() - timedelta(days=7),
        'month': datetime.now() - timedelta(days=30),
    }
    
    income_by_period = {}
    for period_name, period_start in periods.items():
        amount = await db.scalar(
            select(func.sum(Transaction.amount)).where(
                Transaction.created_at >= period_start,
                Transaction.type == TransactionType.DEPOSIT
            )
        )
        income_by_period[period_name] = amount or 0
    
    # Реферальные доходы
    referral_earnings = await db.scalar(
        select(func.sum(User.referral_earnings))
    ) or 0
    
    return templates.TemplateResponse(
        "statistics_finance.html",
        {
            "request": request,
            "total_balance": total_balance,
            "transaction_stats": transaction_stats,
            "income_by_period": income_by_period,
            "referral_earnings": referral_earnings,
        }
    )


@router.get("/marzban", response_class=HTMLResponse)
async def statistics_marzban(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Статистика по Marzban"""
    
    # Подписки
    active_subscriptions = await db.scalar(
        select(func.count(Subscription.id)).where(Subscription.is_active == True)
    )
    inactive_subscriptions = await db.scalar(
        select(func.count(Subscription.id)).where(Subscription.is_active == False)
    )
    
    # Трафик (если есть данные)
    total_traffic_used = await db.scalar(
        select(func.sum(Subscription.used_traffic))
    ) or 0
    
    # Подписки по статусам
    from database.models import SubscriptionStatus
    subscription_by_status = {}
    for status in SubscriptionStatus:
        count = await db.scalar(
            select(func.count(Subscription.id)).where(Subscription.status == status)
        )
        subscription_by_status[status.value] = count or 0
    
    # Последние созданные подписки
    result = await db.execute(
        select(Subscription).order_by(Subscription.created_at.desc()).limit(10)
    )
    recent_subscriptions = result.scalars().all()
    
    return templates.TemplateResponse(
        "statistics_marzban.html",
        {
            "request": request,
            "active_subscriptions": active_subscriptions or 0,
            "inactive_subscriptions": inactive_subscriptions or 0,
            "total_traffic_used": total_traffic_used,
            "subscription_by_status": subscription_by_status,
            "recent_subscriptions": recent_subscriptions,
        }
    )
