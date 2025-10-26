"""
Admin Panel Main Application
FastAPI приложение для админ-панели
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from .routes import admin_routes, user_routes, subscription_routes, broadcast_routes, settings_routes

# Получаем путь к директории admin
BASE_DIR = Path(__file__).resolve().parent

# Создаем приложение FastAPI
app = FastAPI(
    title="YoVPN Admin Panel",
    description="Панель управления VPN ботом",
    version="1.0.0",
    docs_url="/admin/docs",
    redoc_url="/admin/redoc",
)

# Монтируем статические файлы
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/admin/static", StaticFiles(directory=str(static_dir)), name="static")

# Настраиваем шаблоны Jinja2
templates_dir = BASE_DIR / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Добавляем фильтры для Jinja2
def format_currency(value):
    """Форматирование валюты"""
    return f"{value:.2f} ₽"

def format_datetime(value):
    """Форматирование даты и времени"""
    if value:
        return value.strftime("%d.%m.%Y %H:%M")
    return "-"

def format_date(value):
    """Форматирование даты"""
    if value:
        return value.strftime("%d.%m.%Y")
    return "-"

templates.env.filters["currency"] = format_currency
templates.env.filters["datetime"] = format_datetime
templates.env.filters["date"] = format_date

# ID администратора (из переменных окружения или hardcoded)
ADMIN_TG_ID = int(os.getenv("ADMIN_TG_ID", "7610842643"))


async def check_admin_access(tg_id: int = None):
    """Проверка прав администратора"""
    if tg_id != ADMIN_TG_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin only."
        )
    return True


@app.get("/", response_class=HTMLResponse)
async def root():
    """Редирект на админ панель"""
    return RedirectResponse(url="/admin")


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Главная страница админ панели"""
    from database.models import User, Subscription, Transaction
    from sqlalchemy import select, func
    
    # Получаем статистику
    total_users = await db.scalar(select(func.count(User.id)))
    active_subscriptions = await db.scalar(
        select(func.count(Subscription.id)).where(Subscription.is_active == True)
    )
    total_balance = await db.scalar(select(func.sum(User.balance))) or 0
    total_transactions = await db.scalar(select(func.count(Transaction.id)))
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_users": total_users or 0,
            "active_subscriptions": active_subscriptions or 0,
            "total_balance": total_balance,
            "total_transactions": total_transactions or 0,
        }
    )


# Подключаем роуты
app.include_router(admin_routes.router, prefix="/admin", tags=["admin"])
app.include_router(user_routes.router, prefix="/admin/users", tags=["users"])
app.include_router(subscription_routes.router, prefix="/admin/subscriptions", tags=["subscriptions"])
app.include_router(broadcast_routes.router, prefix="/admin/broadcast", tags=["broadcast"])
app.include_router(settings_routes.router, prefix="/admin/settings", tags=["settings"])

# Новые роуты
from .routes import statistics_routes, balance_routes, marzban_routes, security_routes

app.include_router(statistics_routes.router, prefix="/admin/statistics", tags=["statistics"])
app.include_router(balance_routes.router, prefix="/admin/balance", tags=["balance"])
app.include_router(marzban_routes.router, prefix="/admin/marzban", tags=["marzban"])
app.include_router(security_routes.router, prefix="/admin/security", tags=["security"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
