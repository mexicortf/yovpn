#!/usr/bin/env python3
"""
Тесты для UserService
"""

import pytest
import tempfile
import os
from src.services.user_service import UserService
from src.models.user import User

class TestUserService:
    """Тесты для UserService"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем временный файл для тестов
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        # Создаем сервис с временным файлом
        self.user_service = UserService()
        self.user_service.data_file = self.temp_file.name
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        # Удаляем временный файл
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_ensure_user_record_new_user(self):
        """Тест создания нового пользователя"""
        user = self.user_service.ensure_user_record(123, "testuser", "Test User")
        
        assert user.user_id == 123
        assert user.username == "testuser"
        assert user.balance_rub == 0
        assert user.bonus_given == False
        assert user.first_start_completed == False
    
    def test_ensure_user_record_existing_user(self):
        """Тест получения существующего пользователя"""
        # Создаем пользователя
        user1 = self.user_service.ensure_user_record(123, "testuser", "Test User")
        user1.balance_rub = 100
        self.user_service.update_user_record(123, {"balance_rub": 100})
        
        # Получаем того же пользователя
        user2 = self.user_service.ensure_user_record(123, "testuser", "Test User")
        
        assert user2.user_id == 123
        assert user2.balance_rub == 100
    
    def test_credit_balance(self):
        """Тест зачисления баланса"""
        user = self.user_service.ensure_user_record(123, "testuser", "Test User")
        
        # Зачисляем 50 рублей
        success = self.user_service.credit_balance(123, 50, "test")
        assert success == True
        
        # Проверяем баланс
        updated_user = self.user_service.get_user_record(123)
        assert updated_user.balance_rub == 50
    
    def test_credit_balance_negative(self):
        """Тест зачисления отрицательного баланса"""
        user = self.user_service.ensure_user_record(123, "testuser", "Test User")
        user.balance_rub = 30
        self.user_service.update_user_record(123, {"balance_rub": 30})
        
        # Списываем 50 рублей (должно стать 0)
        success = self.user_service.credit_balance(123, -50, "test")
        assert success == True
        
        # Проверяем баланс
        updated_user = self.user_service.get_user_record(123)
        assert updated_user.balance_rub == 0
    
    def test_record_referral(self):
        """Тест записи реферальной связи"""
        # Создаем двух пользователей
        referrer = self.user_service.ensure_user_record(123, "referrer", "Referrer")
        referred = self.user_service.ensure_user_record(456, "referred", "Referred")
        
        # Записываем реферальную связь
        success = self.user_service.record_referral(123, 456)
        assert success == True
        
        # Проверяем связь
        updated_referrer = self.user_service.get_user_record(123)
        updated_referred = self.user_service.get_user_record(456)
        
        assert 456 in updated_referrer.referrals
        assert updated_referred.referred_by == 123
        assert updated_referrer.balance_rub == 12  # Бонус за реферала
    
    def test_record_referral_self(self):
        """Тест записи реферальной связи с самим собой"""
        user = self.user_service.ensure_user_record(123, "testuser", "Test User")
        
        # Пытаемся записать реферальную связь с самим собой
        success = self.user_service.record_referral(123, 123)
        assert success == False
    
    def test_find_user_id_by_username(self):
        """Тест поиска пользователя по username"""
        user = self.user_service.ensure_user_record(123, "testuser", "Test User")
        
        # Ищем по username
        found_id = self.user_service.find_user_id_by_username("testuser")
        assert found_id == 123
        
        # Ищем несуществующего пользователя
        found_id = self.user_service.find_user_id_by_username("nonexistent")
        assert found_id is None
    
    def test_get_user_stats(self):
        """Тест получения статистики пользователя"""
        user = self.user_service.ensure_user_record(123, "testuser", "Test User")
        user.balance_rub = 100
        self.user_service.update_user_record(123, {"balance_rub": 100})
        
        stats = self.user_service.get_user_stats(123)
        
        assert stats['user_id'] == 123
        assert stats['username'] == "testuser"
        assert stats['balance_rub'] == 100
        assert stats['days_remaining'] == 25  # 100 / 4
        assert stats['referrals_count'] == 0
        assert stats['referral_income'] == 0