"""
Основные сервисы бота
Центральный класс для управления всеми сервисами
"""

import asyncio
import logging
from typing import Optional

from .user_service import UserService
from .marzban_service import MarzbanService
from .payment_service import PaymentService
from .notification_service import NotificationService
from .animation_service import AnimationService
from .ui_service import UIService
from .security_service import SecurityService

logger = logging.getLogger(__name__)

class BotServices:
    """
    Центральный класс для управления всеми сервисами бота
    
    Отвечает за:
    - Инициализацию всех сервисов
    - Управление фоновыми задачами
    - Координацию между сервисами
    - Очистку ресурсов при остановке
    """
    
    def __init__(self, bot):
        """
        Инициализация сервисов
        
        Args:
            bot: Экземпляр бота
        """
        self.bot = bot
        self._background_tasks = []
        
        # Инициализируем сервисы
        self.user_service = UserService()
        self.marzban_service = MarzbanService()
        self.payment_service = PaymentService(self.user_service, self.marzban_service)
        self.notification_service = NotificationService(bot)
        self.animation_service = AnimationService(bot)
        self.ui_service = UIService()
        self.security_service = SecurityService()
        
        logger.info("✅ Все сервисы инициализированы (включая SecurityService)")
    
    async def start_background_tasks(self):
        """Запуск фоновых задач"""
        try:
            # Запускаем ежедневную проверку платежей
            payment_task = asyncio.create_task(
                self.payment_service.daily_payment_loop()
            )
            self._background_tasks.append(payment_task)
            
            # Запускаем проверку уведомлений
            notification_task = asyncio.create_task(
                self.notification_service.notification_loop()
            )
            self._background_tasks.append(notification_task)
            
            logger.info("✅ Фоновые задачи запущены")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска фоновых задач: {e}")
            raise
    
    async def stop_background_tasks(self):
        """Остановка фоновых задач"""
        try:
            # Отменяем все фоновые задачи
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()
            
            # Ждем завершения всех задач
            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            logger.info("✅ Фоновые задачи остановлены")
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки фоновых задач: {e}")
    
    def get_user_service(self) -> UserService:
        """Получить сервис пользователей"""
        return self.user_service
    
    def get_marzban_service(self) -> MarzbanService:
        """Получить сервис Marzban"""
        return self.marzban_service
    
    def get_payment_service(self) -> PaymentService:
        """Получить сервис платежей"""
        return self.payment_service
    
    def get_notification_service(self) -> NotificationService:
        """Получить сервис уведомлений"""
        return self.notification_service
    
    def get_animation_service(self) -> AnimationService:
        """Получить сервис анимаций"""
        return self.animation_service
    
    def get_ui_service(self) -> UIService:
        """Получить сервис UI"""
        return self.ui_service
    
    def get_security_service(self) -> SecurityService:
        """Получить сервис безопасности"""
        return self.security_service