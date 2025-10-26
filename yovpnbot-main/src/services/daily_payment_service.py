#!/usr/bin/env python3
"""
Сервис для ежедневной проверки баланса и списания средств
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from ..config import config
from .marzban_service import MarzbanService
from .user_service import UserService

logger = logging.getLogger(__name__)

class DailyPaymentService:
    """Сервис для ежедневной проверки баланса и списания средств"""
    
    def __init__(self, marzban_service: MarzbanService, user_service: UserService):
        self.marzban_service = marzban_service
        self.user_service = user_service
        self.daily_cost = 4  # Стоимость дня в рублях
        self.is_running = False
        self.thread = None
        
    def start_daily_checker(self):
        """Запустить ежедневную проверку баланса"""
        if self.is_running:
            logger.warning("Ежедневная проверка уже запущена")
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._daily_check_loop, daemon=True)
        self.thread.start()
        logger.info("Ежедневная проверка баланса запущена")
    
    def stop_daily_checker(self):
        """Остановить ежедневную проверку баланса"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Ежедневная проверка баланса остановлена")
    
    def _daily_check_loop(self):
        """Основной цикл ежедневной проверки"""
        while self.is_running:
            try:
                # Выполняем проверку каждый день в 00:00
                now = datetime.now()
                next_check = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                
                if now.hour == 0 and now.minute < 5:  # Проверяем в течение первых 5 минут после полуночи
                    self._process_daily_payments()
                
                # Спим до следующей проверки (каждые 5 минут)
                time.sleep(300)  # 5 минут
                
            except Exception as e:
                logger.error(f"Ошибка в цикле ежедневной проверки: {e}")
                time.sleep(60)  # При ошибке ждем минуту
    
    def _process_daily_payments(self):
        """Обработать ежедневные платежи для всех пользователей"""
        logger.info("Начинаем ежедневную обработку платежей")
        
        try:
            # Получаем всех пользователей из Marzban
            all_users = self.marzban_service.get_all_users()
            if not all_users:
                logger.warning("Не удалось получить список пользователей из Marzban")
                return
            
            processed_count = 0
            suspended_count = 0
            error_count = 0
            
            for user_data in all_users:
                try:
                    username = user_data.get('username')
                    if not username:
                        continue
                    
                    # Получаем telegram_id пользователя (предполагаем, что он хранится в user_data)
                    telegram_id = user_data.get('telegram_id')
                    if not telegram_id:
                        # Пытаемся найти пользователя по username в нашей базе
                        telegram_id = self._find_telegram_id_by_username(username)
                        if not telegram_id:
                            continue
                    
                    # Обрабатываем платеж для пользователя
                    result = self._process_user_payment(telegram_id, username, user_data)
                    
                    if result == 'processed':
                        processed_count += 1
                    elif result == 'suspended':
                        suspended_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"Ошибка обработки пользователя {username}: {e}")
                    error_count += 1
            
            logger.info(f"Ежедневная обработка завершена: обработано={processed_count}, "
                       f"приостановлено={suspended_count}, ошибок={error_count}")
            
        except Exception as e:
            logger.error(f"Ошибка ежедневной обработки платежей: {e}")
    
    def _find_telegram_id_by_username(self, username: str) -> Optional[int]:
        """Найти telegram_id по username"""
        try:
            # Читаем файл данных пользователей
            with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            users = data.get('users', {})
            for user_id, user_info in users.items():
                if user_info.get('username') == username:
                    return int(user_id)
            
            return None
        except Exception as e:
            logger.error(f"Ошибка поиска telegram_id для {username}: {e}")
            return None
    
    def _process_user_payment(self, telegram_id: int, username: str, user_data: Dict) -> str:
        """Обработать платеж для конкретного пользователя"""
        try:
            # Получаем статистику пользователя
            user_stats = self.user_service.get_user_stats(telegram_id)
            balance = user_stats.get('balance', 0)
            
            # Проверяем, достаточно ли средств
            if balance >= self.daily_cost:
                # Списываем средства
                new_balance = balance - self.daily_cost
                self.user_service.update_user_balance(telegram_id, new_balance)
                
                # Продлеваем подписку на 1 день
                self._extend_subscription(username, 1)
                
                # Отправляем уведомление о списании
                self._send_payment_notification(telegram_id, self.daily_cost, new_balance, 'charged')
                
                logger.info(f"Списано {self.daily_cost} руб. с пользователя {username}, баланс: {new_balance}")
                return 'processed'
                
            else:
                # Недостаточно средств - приостанавливаем подписку
                self._suspend_subscription(username)
                
                # Отправляем уведомление о приостановке
                self._send_payment_notification(telegram_id, 0, balance, 'suspended')
                
                logger.info(f"Недостаточно средств у пользователя {username}, подписка приостановлена")
                return 'suspended'
                
        except Exception as e:
            logger.error(f"Ошибка обработки платежа для {username}: {e}")
            return 'error'
    
    def _extend_subscription(self, username: str, days: int):
        """Продлить подписку пользователя на указанное количество дней"""
        try:
            # Получаем текущие данные пользователя
            user_data = self.marzban_service.get_user_by_username(username)
            if not user_data:
                logger.error(f"Пользователь {username} не найден в Marzban")
                return False
            
            # Вычисляем новую дату окончания
            current_expire = user_data.get('expire')
            if current_expire:
                if isinstance(current_expire, str):
                    expire_date = datetime.fromisoformat(current_expire.replace('Z', '+00:00'))
                else:
                    expire_date = datetime.fromtimestamp(current_expire)
            else:
                expire_date = datetime.now()
            
            new_expire = expire_date + timedelta(days=days)
            new_expire_timestamp = int(new_expire.timestamp())
            
            # Обновляем пользователя
            updates = {
                'expire': new_expire_timestamp,
                'status': 'active'
            }
            
            result = self.marzban_service.update_user(username, updates)
            if result:
                logger.info(f"Подписка пользователя {username} продлена на {days} дней до {new_expire}")
                return True
            else:
                logger.error(f"Не удалось продлить подписку пользователя {username}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка продления подписки для {username}: {e}")
            return False
    
    def _suspend_subscription(self, username: str):
        """Приостановить подписку пользователя"""
        try:
            updates = {
                'status': 'expired'
            }
            
            result = self.marzban_service.update_user(username, updates)
            if result:
                logger.info(f"Подписка пользователя {username} приостановлена")
                return True
            else:
                logger.error(f"Не удалось приостановить подписку пользователя {username}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка приостановки подписки для {username}: {e}")
            return False
    
    def _send_payment_notification(self, telegram_id: int, amount: float, balance: float, action: str):
        """Отправить уведомление о платеже пользователю"""
        try:
            # Здесь должна быть логика отправки уведомлений через Telegram
            # Пока просто логируем
            if action == 'charged':
                logger.info(f"Уведомление для {telegram_id}: списано {amount} руб., баланс: {balance} руб.")
            elif action == 'suspended':
                logger.info(f"Уведомление для {telegram_id}: подписка приостановлена, баланс: {balance} руб.")
                
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления для {telegram_id}: {e}")
    
    def check_low_balance_users(self):
        """Проверить пользователей с низким балансом и отправить уведомления"""
        logger.info("Проверяем пользователей с низким балансом")
        
        try:
            # Получаем всех пользователей из Marzban
            all_users = self.marzban_service.get_all_users()
            if not all_users:
                return
            
            low_balance_count = 0
            
            for user_data in all_users:
                try:
                    username = user_data.get('username')
                    if not username:
                        continue
                    
                    # Находим telegram_id
                    telegram_id = self._find_telegram_id_by_username(username)
                    if not telegram_id:
                        continue
                    
                    # Получаем статистику пользователя
                    user_stats = self.user_service.get_user_stats(telegram_id)
                    balance = user_stats.get('balance', 0)
                    
                    # Проверяем, нужно ли отправить уведомление
                    if self._should_send_low_balance_notification(telegram_id, balance):
                        self._send_low_balance_notification(telegram_id, balance)
                        low_balance_count += 1
                        
                except Exception as e:
                    logger.error(f"Ошибка проверки баланса для {username}: {e}")
            
            logger.info(f"Отправлено {low_balance_count} уведомлений о низком балансе")
            
        except Exception as e:
            logger.error(f"Ошибка проверки пользователей с низким балансом: {e}")
    
    def _should_send_low_balance_notification(self, telegram_id: int, balance: float) -> bool:
        """Проверить, нужно ли отправить уведомление о низком балансе"""
        try:
            # Проверяем, отправляли ли уже уведомление сегодня
            today = datetime.now().date().isoformat()
            
            # Читаем файл данных пользователей
            with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            users = data.get('users', {})
            user_info = users.get(str(telegram_id), {})
            last_notification = user_info.get('last_low_balance_notification')
            
            # Если уведомление уже отправлялось сегодня, не отправляем повторно
            if last_notification == today:
                return False
            
            # Отправляем уведомление, если баланс меньше 4 рублей (1 день)
            return balance < self.daily_cost
            
        except Exception as e:
            logger.error(f"Ошибка проверки необходимости уведомления для {telegram_id}: {e}")
            return False
    
    def _send_low_balance_notification(self, telegram_id: int, balance: float):
        """Отправить уведомление о низком балансе"""
        try:
            # Обновляем дату последнего уведомления
            today = datetime.now().date().isoformat()
            
            with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'users' not in data:
                data['users'] = {}
            
            if str(telegram_id) not in data['users']:
                data['users'][str(telegram_id)] = {}
            
            data['users'][str(telegram_id)]['last_low_balance_notification'] = today
            
            with open(config.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Логируем уведомление (здесь должна быть отправка через Telegram)
            logger.info(f"Уведомление о низком балансе для {telegram_id}: баланс {balance} руб.")
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о низком балансе для {telegram_id}: {e}")