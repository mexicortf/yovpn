"""
User Management Routes
Управление пользователями
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from typing import Optional

from database import get_db
from database.models import User, Subscription, Transaction, TransactionType

router = APIRouter()

# Настраиваем шаблоны
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def users_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = None
):
    """Список пользователей"""
    query = select(User).order_by(User.created_at.desc())
    
    if search:
        query = query.where(
            (User.username.contains(search)) |
            (User.tg_id == int(search) if search.isdigit() else False)
        )
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return templates.TemplateResponse(
        "users_list.html",
        {
            "request": request,
            "users": users,
            "search": search,
        }
    )


@router.get("/{user_id}", response_class=HTMLResponse)
async def user_detail(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Детальная информация о пользователе"""
    # Получаем пользователя
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем подписки
    subs_result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.created_at.desc())
    )
    subscriptions = subs_result.scalars().all()
    
    # Получаем транзакции
    trans_result = await db.execute(
        select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.created_at.desc()).limit(50)
    )
    transactions = trans_result.scalars().all()
    
    return templates.TemplateResponse(
        "user_detail.html",
        {
            "request": request,
            "user": user,
            "subscriptions": subscriptions,
            "transactions": transactions,
        }
    )


@router.post("/{user_id}/block")
async def block_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Заблокировать пользователя"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_blocked = True
    await db.commit()
    
    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)


@router.post("/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Разблокировать пользователя"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_blocked = False
    await db.commit()
    
    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)


@router.post("/{user_id}/balance")
async def update_balance(
    user_id: int,
    amount: float = Form(...),
    description: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    """Изменить баланс пользователя"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    balance_before = user.balance
    user.balance += amount
    balance_after = user.balance
    
    # Создаем транзакцию
    transaction = Transaction(
        user_id=user.id,
        amount=amount,
        type=TransactionType.DEPOSIT if amount > 0 else TransactionType.WITHDRAW,
        description=description or f"Изменение баланса администратором",
        balance_before=balance_before,
        balance_after=balance_after,
    )
    
    db.add(transaction)
    await db.commit()
    
    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)


@router.post("/{user_id}/delete")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить пользователя"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    
    return RedirectResponse(url="/admin/users", status_code=303)
