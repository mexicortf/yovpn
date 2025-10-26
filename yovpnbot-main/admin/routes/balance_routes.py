"""
Balance Management Routes
Управление балансом пользователей
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pathlib import Path
from typing import Optional

from database import get_db
from database.models import User, Transaction, TransactionType

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def balance_management(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Управление балансом"""
    return templates.TemplateResponse(
        "balance_management.html",
        {
            "request": request,
        }
    )


@router.get("/add", response_class=HTMLResponse)
async def add_balance_form(
    request: Request,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Форма пополнения баланса"""
    user = None
    if user_id:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "balance_add_form.html",
        {
            "request": request,
            "user": user,
        }
    )


@router.post("/add")
async def add_balance(
    user_id: int = Form(...),
    amount: float = Form(...),
    description: str = Form("Пополнение администратором"),
    db: AsyncSession = Depends(get_db)
):
    """Пополнить баланс пользователя"""
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
        type=TransactionType.DEPOSIT,
        description=description,
        balance_before=balance_before,
        balance_after=balance_after,
    )
    
    db.add(transaction)
    await db.commit()
    
    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)


@router.get("/withdraw", response_class=HTMLResponse)
async def withdraw_balance_form(
    request: Request,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Форма списания баланса"""
    user = None
    if user_id:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "balance_withdraw_form.html",
        {
            "request": request,
            "user": user,
        }
    )


@router.post("/withdraw")
async def withdraw_balance(
    user_id: int = Form(...),
    amount: float = Form(...),
    description: str = Form("Списание администратором"),
    db: AsyncSession = Depends(get_db)
):
    """Списать баланс пользователя"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    balance_before = user.balance
    user.balance -= amount
    balance_after = user.balance
    
    # Создаем транзакцию
    transaction = Transaction(
        user_id=user.id,
        amount=-amount,
        type=TransactionType.WITHDRAW,
        description=description,
        balance_before=balance_before,
        balance_after=balance_after,
    )
    
    db.add(transaction)
    await db.commit()
    
    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)


@router.get("/set", response_class=HTMLResponse)
async def set_balance_form(
    request: Request,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Форма установки баланса"""
    user = None
    if user_id:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "balance_set_form.html",
        {
            "request": request,
            "user": user,
        }
    )


@router.post("/set")
async def set_balance(
    user_id: int = Form(...),
    new_balance: float = Form(...),
    description: str = Form("Установка баланса администратором"),
    db: AsyncSession = Depends(get_db)
):
    """Установить баланс пользователя"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    balance_before = user.balance
    user.balance = new_balance
    balance_after = user.balance
    
    difference = new_balance - balance_before
    trans_type = TransactionType.DEPOSIT if difference > 0 else TransactionType.WITHDRAW
    
    # Создаем транзакцию
    transaction = Transaction(
        user_id=user.id,
        amount=difference,
        type=trans_type,
        description=description,
        balance_before=balance_before,
        balance_after=balance_after,
    )
    
    db.add(transaction)
    await db.commit()
    
    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)


@router.get("/search", response_class=HTMLResponse)
async def search_users_for_balance(
    request: Request,
    query: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Поиск пользователей для операций с балансом"""
    users = []
    if query:
        result = await db.execute(
            select(User).where(
                or_(
                    User.username.contains(query),
                    User.tg_id == int(query) if query.isdigit() else False,
                    User.first_name.contains(query)
                )
            ).limit(50)
        )
        users = result.scalars().all()
    
    return templates.TemplateResponse(
        "balance_search.html",
        {
            "request": request,
            "users": users,
            "query": query,
        }
    )
