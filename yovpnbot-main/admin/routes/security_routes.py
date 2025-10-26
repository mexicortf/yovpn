"""
Security Routes  
Логи, мониторинг, резервное копирование
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pathlib import Path
from datetime import datetime, timedelta
import os
import subprocess
import logging

from database import get_db
from database.models import User, Transaction

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def security_overview(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Обзор безопасности"""
    
    # Последние 50 транзакций
    result = await db.execute(
        select(Transaction).order_by(desc(Transaction.created_at)).limit(50)
    )
    recent_transactions = result.scalars().all()
    
    # Заблокированные пользователи
    result = await db.execute(
        select(User).where(User.is_blocked == True)
    )
    blocked_users = result.scalars().all()
    
    return templates.TemplateResponse(
        "security_overview.html",
        {
            "request": request,
            "recent_transactions": recent_transactions,
            "blocked_users": blocked_users,
        }
    )


@router.get("/logs", response_class=HTMLResponse)
async def view_logs(
    request: Request,
    lines: int = 100
):
    """Просмотр логов"""
    log_file = os.getenv("LOG_FILE", "logs/yovpn.log")
    
    if not os.path.exists(log_file):
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Файл логов не найден"
            }
        )
    
    # Читаем последние N строк
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
    except Exception as e:
        recent_lines = [f"Ошибка чтения логов: {str(e)}"]
    
    return templates.TemplateResponse(
        "security_logs.html",
        {
            "request": request,
            "logs": recent_lines,
            "lines": lines,
        }
    )


@router.get("/monitoring", response_class=HTMLResponse)
async def monitoring(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Мониторинг системы"""
    
    # Статистика за последний час
    hour_ago = datetime.now() - timedelta(hours=1)
    
    # Новые пользователи
    result = await db.execute(
        select(User).where(User.created_at >= hour_ago)
    )
    new_users_hour = result.scalars().all()
    
    # Транзакции
    result = await db.execute(
        select(Transaction).where(Transaction.created_at >= hour_ago)
    )
    transactions_hour = result.scalars().all()
    
    # Системная информация
    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    system_info = {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_used': memory.used / (1024**3),  # GB
        'memory_total': memory.total / (1024**3),  # GB
        'disk_percent': disk.percent,
        'disk_used': disk.used / (1024**3),  # GB
        'disk_total': disk.total / (1024**3),  # GB
    }
    
    return templates.TemplateResponse(
        "security_monitoring.html",
        {
            "request": request,
            "new_users_hour": new_users_hour,
            "transactions_hour": transactions_hour,
            "system_info": system_info,
        }
    )


@router.post("/backup")
async def create_backup(db: AsyncSession = Depends(get_db)):
    """Создание резервной копии базы данных"""
    try:
        # Директория для бэкапов
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Имя файла бэкапа
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"yovpn_backup_{timestamp}.sql"
        
        # Получаем данные подключения
        database_url = os.getenv("DATABASE_URL", "")
        
        # Парсим URL (упрощенно)
        # mysql+aiomysql://user:password@host:port/database
        if "mysql" in database_url:
            parts = database_url.split("//")[1].split("/")
            creds = parts[0].split("@")
            user_pass = creds[0].split(":")
            host_port = creds[1].split(":")
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "3306"
            database = parts[1]
            
            # Создаем дамп через mysqldump
            command = [
                "mysqldump",
                f"-h{host}",
                f"-P{port}",
                f"-u{user}",
                f"-p{password}",
                database
            ]
            
            with open(backup_file, 'w') as f:
                subprocess.run(command, stdout=f, check=True)
            
            logger.info(f"✅ Создан бэкап: {backup_file}")
            
            return JSONResponse({
                "success": True,
                "message": f"✅ Резервная копия создана: {backup_file.name}",
                "file": str(backup_file)
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "❌ Поддерживается только MySQL"
            }, status_code=400)
    
    except Exception as e:
        logger.error(f"❌ Ошибка создания бэкапа: {e}")
        return JSONResponse({
            "success": False,
            "message": f"❌ Ошибка: {str(e)}"
        }, status_code=500)


@router.get("/backups", response_class=HTMLResponse)
async def list_backups(request: Request):
    """Список резервных копий"""
    backup_dir = Path("backups")
    
    if not backup_dir.exists():
        backups = []
    else:
        backups = sorted(
            backup_dir.glob("*.sql"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
    
    backup_info = []
    for backup in backups:
        stat = backup.stat()
        backup_info.append({
            'name': backup.name,
            'size': stat.st_size / (1024**2),  # MB
            'created': datetime.fromtimestamp(stat.st_mtime),
            'path': str(backup)
        })
    
    return templates.TemplateResponse(
        "security_backups.html",
        {
            "request": request,
            "backups": backup_info,
        }
    )


@router.get("/download-backup/{filename}")
async def download_backup(filename: str):
    """Скачать резервную копию"""
    backup_file = Path("backups") / filename
    
    if not backup_file.exists():
        return JSONResponse({
            "error": "Файл не найден"
        }, status_code=404)
    
    return FileResponse(
        path=backup_file,
        filename=filename,
        media_type="application/sql"
    )
