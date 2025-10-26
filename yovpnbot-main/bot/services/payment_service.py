"""
Сервис платежей
Управление платежами, балансом и ежедневными списаниями
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PaymentService:
    """
    Сервис для работы с платежами
    
    Отвечает за:
    - Обработку платежей и пополнений
    - Ежедневные списания за подписку
    - Управление балансом пользователей
    - Уведомления о платежах
    """
    
    def __init__(self, user_service, marzban_service, daily_cost: float = 4.0):
        """
        Инициализация сервиса
        
        Args:
            user_service: Сервис пользователей
            marzban_service: Сервис Marzban
            daily_cost: Стоимость дня подписки
        """
        self.user_service = user_service
        self.marzban_service = marzban_service
        self.daily_cost = daily_cost
        self._running = False
        
        logger.info(f"✅ PaymentService инициализирован, стоимость дня: {daily_cost} ₽")
    
    async def process_payment(self, user_id: int, amount: float, payment_method: str = "demo") -> Dict[str, Any]:
        """
        Обработать платеж
        
        Args:
            user_id: ID пользователя
            amount: Сумма платежа
            payment_method: Способ оплаты
        
        Returns:
            Dict: Результат обработки платежа
        """
        try:
            # В реальной системе здесь была бы интеграция с платежными системами
            if payment_method == "demo":
                # Демо-режим: просто добавляем средства
                success = await self.user_service.update_user_balance(user_id, amount, "add")
                
                if success:
                    # Обновляем статистику платежей
                    user = await self.user_service.get_user(user_id)
                    if user:
                        user['total_payments'] = user.get('total_payments', 0) + amount
                        self.user_service._save_users()
                    
                    days_added = int(amount / self.daily_cost)
                    
                    logger.info(f"💰 Платеж обработан: {user_id} +{amount} ₽ ({days_added} дней)")
                    
                    return {
                        'success': True,
                        'amount': amount,
                        'days_added': days_added,
                        'new_balance': await self.user_service.get_user_balance(user_id),
                        'message': f"Платеж на {amount:.2f} ₽ успешно обработан! Добавлено {days_added} дней."
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Ошибка обновления баланса'
                    }
            else:
                # Здесь была бы интеграция с реальными платежными системами
                return {
                    'success': False,
                    'error': 'Платежная система недоступна'
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки платежа: {e}")
            return {
                'success': False,
                'error': f'Ошибка обработки платежа: {str(e)}'
            }
    
    async def daily_payment_loop(self):
        """
        Основной цикл ежедневных платежей
        Запускается в фоновом режиме
        """
        self._running = True
        logger.info("🔄 Запуск цикла ежедневных платежей")
        
        while self._running:
            try:
                await self._process_daily_payments()
                # Ждем 24 часа до следующей проверки
                await asyncio.sleep(24 * 60 * 60)
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле ежедневных платежей: {e}")
                # При ошибке ждем 1 час перед повтором
                await asyncio.sleep(60 * 60)
    
    async def _process_daily_payments(self):
        """
        Обработать ежедневные платежи для всех пользователей
        """
        try:
            users = await self.user_service.get_all_users()
            processed_count = 0
            deactivated_count = 0
            
            for user_id, user_data in users.items():
                if not user_data.get('subscription_active', False):
                    continue
                
                balance = user_data.get('balance', 0.0)
                
                if balance >= self.daily_cost:
                    # Списываем средства за день
                    success = await self.user_service.update_user_balance(
                        user_id, 
                        self.daily_cost, 
                        "subtract"
                    )
                    
                    if success:
                        # Обновляем подписку в Marzban
                        await self._update_marzban_subscription(user_id, user_data)
                        processed_count += 1
                        
                        logger.info(f"💰 Списано {self.daily_cost} ₽ с пользователя {user_id}")
                    else:
                        logger.error(f"❌ Ошибка списания с пользователя {user_id}")
                else:
                    # Недостаточно средств - деактивируем подписку
                    await self.user_service.deactivate_subscription(user_id)
                    await self._deactivate_marzban_subscription(user_id, user_data)
                    deactivated_count += 1
                    
                    logger.info(f"❌ Подписка деактивирована для пользователя {user_id} (недостаточно средств)")
            
            logger.info(f"📊 Ежедневные платежи обработаны: {processed_count} списаний, {deactivated_count} деактиваций")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки ежедневных платежей: {e}")
    
    async def _update_marzban_subscription(self, user_id: int, user_data: Dict[str, Any]):
        """
        Обновить подписку в Marzban
        
        Args:
            user_id: ID пользователя
            user_data: Данные пользователя
        """
        try:
            username = user_data.get('username', f"user_{user_id}")
            
            # Продлеваем подписку на 1 день
            new_expire = datetime.now() + timedelta(days=1)
            expire_timestamp = int(new_expire.timestamp())
            
            # Обновляем пользователя в Marzban
            await self.marzban_service.update_user(
                username=username,
                updates={
                    'expire': expire_timestamp,
                    'status': 'active'
                }
            )
            
            logger.debug(f"✅ Подписка в Marzban обновлена для {username}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления подписки в Marzban: {e}")
    
    async def _deactivate_marzban_subscription(self, user_id: int, user_data: Dict[str, Any]):
        """
        Деактивировать подписку в Marzban
        
        Args:
            user_id: ID пользователя
            user_data: Данные пользователя
        """
        try:
            username = user_data.get('username', f"user_{user_id}")
            
            # Деактивируем пользователя в Marzban
            await self.marzban_service.update_user(
                username=username,
                updates={
                    'status': 'expired'
                }
            )
            
            logger.debug(f"❌ Подписка в Marzban деактивирована для {username}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка деактивации подписки в Marzban: {e}")
    
    async def get_payment_history(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получить историю платежей пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            List: История платежей
        """
        # В реальной системе здесь была бы база данных с историей платежей
        user = await self.user_service.get_user(user_id)
        if not user:
            return []
        
        # Пока возвращаем базовую информацию
        return [{
            'date': user.get('created_at', ''),
            'amount': user.get('total_payments', 0.0),
            'type': 'Пополнение',
            'status': 'Успешно'
        }]
    
    async def get_available_payment_methods(self) -> List[Dict[str, Any]]:
        """
        Получить доступные способы оплаты
        
        Returns:
            List: Способы оплаты
        """
        return [
            {
                'id': 'demo',
                'name': 'Демо-режим',
                'description': 'Тестовый режим для разработки',
                'enabled': True
            },
            {
                'id': 'card',
                'name': 'Банковская карта',
                'description': 'Visa, MasterCard, МИР',
                'enabled': False  # В разработке
            },
            {
                'id': 'yoomoney',
                'name': 'ЮMoney',
                'description': 'Быстрые платежи',
                'enabled': False  # В разработке
            },
            {
                'id': 'crypto',
                'name': 'Криптовалюта',
                'description': 'Bitcoin, Ethereum',
                'enabled': False  # В разработке
            }
        ]
    
    async def stop(self):
        """Остановить сервис"""
        self._running = False
        logger.info("🛑 PaymentService остановлен")
    
    def is_running(self) -> bool:
        """Проверить, запущен ли сервис"""
        return self._running