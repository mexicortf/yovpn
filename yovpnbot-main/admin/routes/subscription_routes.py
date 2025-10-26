"""
Subscription Management Routes
Управление подписками
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path

from database import get_db
from database.models import Subscription, User

router = APIRouter()

# Настраиваем шаблоны
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def subscriptions_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    status: str = None
):
    """Список подписок"""
    query = select(Subscription).join(User).order_by(Subscription.created_at.desc())
    
    if status:
        if status == "active":
            query = query.where(Subscription.is_active == True)
        elif status == "inactive":
            query = query.where(Subscription.is_active == False)
    
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    return templates.TemplateResponse(
        "subscriptions_list.html",
        {
            "request": request,
            "subscriptions": subscriptions,
            "status_filter": status,
        }
    )


@router.get("/{subscription_id}", response_class=HTMLResponse)
async def subscription_detail(
    request: Request,
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Детальная информация о подписке"""
    result = await db.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Получаем пользователя
    user_result = await db.execute(
        select(User).where(User.id == subscription.user_id)
    )
    user = user_result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "subscription_detail.html",
        {
            "request": request,
            "subscription": subscription,
            "user": user,
        }
    )


@router.post("/{subscription_id}/deactivate")
async def deactivate_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Деактивировать подписку"""
    result = await db.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.is_active = False
    await db.commit()
    
    return RedirectResponse(url=f"/admin/subscriptions/{subscription_id}", status_code=303)


@router.post("/{subscription_id}/activate")
async def activate_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Активировать подписку"""
    result = await db.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.is_active = True
    await db.commit()
    
    return RedirectResponse(url=f"/admin/subscriptions/{subscription_id}", status_code=303)
