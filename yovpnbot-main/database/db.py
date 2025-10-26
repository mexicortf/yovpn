"""
Настройка подключения к базе данных MySQL
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:password@localhost:3306/yovpn"
)

# Создаем async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Отключаем логирование SQL запросов в продакшене
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,  # Пересоздание соединений каждый час
    pool_size=10,  # Размер пула соединений
    max_overflow=20,  # Максимум дополнительных соединений
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Базовый класс для моделей
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных
    Используется в FastAPI и aiogram handlers
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Инициализация базы данных (создание таблиц)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database initialized successfully")


async def close_db():
    """Закрытие соединений с базой данных"""
    await engine.dispose()
    logger.info("✅ Database connections closed")
