"""
Обработчик реферальной системы
5 уровней глубины с учетом пополнений
"""

import logging
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ReferralHandler:
    """Обработчик реферальной программы"""
    
    def __init__(self, services):
        self.services = services
        self.user_service = services.get_user_service()
        
        # Бонусы за рефералов (1 день = 4 руб)
        self.referral_bonus = 4.0  # 1 день VPN
        
        # Процент от пополнений рефералов по уровням
        self.level_percentages = {
            1: 10,  # 10% от первого уровня
            2: 5,   # 5% от второго уровня
            3: 3,   # 3% от третьего уровня
            4: 2,   # 2% от четвертого уровня
            5: 1    # 1% от пятого уровня
        }
    
    async def get_referral_tree(self, user_id: int, max_level: int = 5) -> Dict:
        """
        Получить дерево рефералов пользователя
        
        Args:
            user_id: ID пользователя
            max_level: Максимальный уровень глубины
            
        Returns:
            Дерево рефералов с статистикой
        """
        tree = {
            'levels': {},
            'total_referrals': 0,
            'total_earnings': 0.0
        }
        
        # Получаем рефералов по уровням
        current_level_users = [user_id]
        
        for level in range(1, max_level + 1):
            if not current_level_users:
                break
            
            # Получаем рефералов текущего уровня
            level_referrals = await self.user_service.get_referrals_by_users(current_level_users)
            
            if not level_referrals:
                break
            
            # Считаем статистику уровня
            level_count = len(level_referrals)
            level_earnings = sum(r.get('referral_earnings', 0) for r in level_referrals)
            
            tree['levels'][level] = {
                'count': level_count,
                'earnings': level_earnings,
                'users': level_referrals
            }
            
            tree['total_referrals'] += level_count
            tree['total_earnings'] += level_earnings
            
            # Переходим на следующий уровень
            current_level_users = [r['tg_id'] for r in level_referrals]
        
        return tree
    
    async def process_referral_deposit(self, user_id: int, amount: float):
        """
        Обработка пополнения реферала - начисление бонусов вверх по дереву
        
        Args:
            user_id: ID пользователя, который пополнил баланс
            amount: Сумма пополнения
        """
        # Получаем информацию о пользователе
        user = await self.user_service.get_user(user_id)
        if not user or not user.get('referred_by'):
            return
        
        # Идем вверх по реферальной цепочке
        current_referrer_id = user['referred_by']
        current_level = 1
        
        while current_referrer_id and current_level <= 5:
            # Получаем процент для текущего уровня
            percentage = self.level_percentages.get(current_level, 0)
            if percentage == 0:
                break
            
            # Вычисляем бонус
            bonus = amount * (percentage / 100)
            
            # Начисляем бонус реферреру
            await self.user_service.add_balance(
                user_id=current_referrer_id,
                amount=bonus,
                description=f"💰 Реферальный бонус ({percentage}%) от пополнения уровня {current_level}"
            )
            
            # Обновляем статистику заработка
            await self.user_service.update_referral_earnings(current_referrer_id, bonus)
            
            logger.info(f"💰 Начислен реферальный бонус: {bonus}₽ для ID {current_referrer_id} (уровень {current_level})")
            
            # Переходим на следующий уровень
            referrer = await self.user_service.get_user(current_referrer_id)
            current_referrer_id = referrer.get('referred_by') if referrer else None
            current_level += 1
    
    async def register_referral(self, user_id: int, referrer_id: int) -> bool:
        """
        Регистрация реферала
        
        Args:
            user_id: ID нового пользователя
            referrer_id: ID пригласившего
            
        Returns:
            True если успешно зарегистрирован
        """
        try:
            # Проверяем, что пользователь еще не зарегистрирован
            user = await self.user_service.get_user(user_id)
            if user and user.get('referred_by'):
                return False
            
            # Получаем уровень реферрера
            referrer = await self.user_service.get_user(referrer_id)
            if not referrer:
                return False
            
            referrer_level = referrer.get('referral_level', 0)
            
            # Регистрируем реферала
            await self.user_service.update_user(
                user_id=user_id,
                referred_by=referrer_id,
                referral_level=referrer_level + 1
            )
            
            # Увеличиваем счетчик рефералов
            await self.user_service.increment_referral_count(referrer_id)
            
            # Начисляем бонус за приглашение (1 день VPN = 4 руб)
            await self.user_service.add_balance(
                user_id=referrer_id,
                amount=self.referral_bonus,
                description=f"🎁 Бонус за приглашение друга (1 день VPN)"
            )
            
            logger.info(f"✅ Зарегистрирован реферал: {user_id} -> {referrer_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка регистрации реферала: {e}")
            return False
    
    async def referral_command(self, message: Message):
        """Команда /invite - реферальная программа"""
        user_id = message.from_user.id
        
        # Получаем реферальную ссылку
        bot_username = (await message.bot.me()).username
        referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        
        # Получаем статистику рефералов
        tree = await self.get_referral_tree(user_id)
        
        total_referrals = tree['total_referrals']
        total_earnings = tree['total_earnings']
        
        # Формируем текст по уровням
        levels_text = ""
        for level in range(1, 6):
            if level in tree['levels']:
                level_data = tree['levels'][level]
                count = level_data['count']
                earnings = level_data['earnings']
                percentage = self.level_percentages.get(level, 0)
                levels_text += f"   {level} уровень: <b>{count}</b> чел. | {percentage}% | {earnings:.2f}₽\n"
        
        text = (
            "<b>👥 Реферальная программа</b>\n\n"
            f"💎 <b>Ваши бонусы:</b>\n"
            f"   • <b>1 день VPN</b> (4₽) за каждого друга\n"
            f"   • <b>До 10%</b> от пополнений рефералов\n\n"
            f"📊 <b>Ваша статистика:</b>\n"
            f"   Всего рефералов: <b>{total_referrals}</b>\n"
            f"   Заработано: <b>{total_earnings:.2f}₽</b>\n\n"
            f"🎯 <b>Структура по уровням:</b>\n"
            f"{levels_text if levels_text else '   Пока нет рефералов\n'}\n"
            f"<b>🔗 Ваша реферальная ссылка:</b>\n"
            f"<code>{referral_link}</code>\n\n"
            f"💡 <i>Отправьте эту ссылку друзьям!</i>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📤 Поделиться ссылкой", switch_inline_query=referral_link)],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="referral_stats")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        ])
        
        await message.answer(text, reply_markup=keyboard)
    
    async def referral_callback(self, callback: CallbackQuery):
        """Callback для реферальной программы"""
        user_id = callback.from_user.id
        
        # Получаем реферальную ссылку
        bot_username = (await callback.bot.me()).username
        referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        
        # Получаем статистику
        tree = await self.get_referral_tree(user_id)
        
        total_referrals = tree['total_referrals']
        total_earnings = tree['total_earnings']
        
        # Формируем текст
        levels_text = ""
        for level in range(1, 6):
            if level in tree['levels']:
                level_data = tree['levels'][level]
                count = level_data['count']
                earnings = level_data['earnings']
                percentage = self.level_percentages.get(level, 0)
                levels_text += f"   {level} уровень: <b>{count}</b> чел. | {percentage}% | {earnings:.2f}₽\n"
        
        text = (
            "<b>👥 Реферальная программа</b>\n\n"
            f"💎 <b>Ваши бонусы:</b>\n"
            f"   • <b>1 день VPN</b> (4₽) за каждого друга\n"
            f"   • <b>До 10%</b> от пополнений рефералов\n\n"
            f"📊 <b>Ваша статистика:</b>\n"
            f"   Всего рефералов: <b>{total_referrals}</b>\n"
            f"   Заработано: <b>{total_earnings:.2f}₽</b>\n\n"
            f"🎯 <b>Структура по уровням:</b>\n"
            f"{levels_text if levels_text else '   Пока нет рефералов\n'}\n"
            f"<b>🔗 Ваша реферальная ссылка:</b>\n"
            f"<code>{referral_link}</code>\n\n"
            f"💡 <i>Отправьте эту ссылку друзьям!</i>"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📤 Поделиться ссылкой", switch_inline_query=referral_link)],
            [InlineKeyboardButton(text="📊 Детальная статистика", callback_data="referral_stats_detailed")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
    
    async def referral_stats_detailed_callback(self, callback: CallbackQuery):
        """Детальная статистика рефералов"""
        user_id = callback.from_user.id
        
        tree = await self.get_referral_tree(user_id)
        
        if not tree['levels']:
            text = (
                "<b>📊 Детальная статистика</b>\n\n"
                "У вас пока нет рефералов.\n"
                "Пригласите друзей и начните зарабатывать!"
            )
        else:
            text = "<b>📊 Детальная статистика по уровням</b>\n\n"
            
            for level in range(1, 6):
                if level in tree['levels']:
                    level_data = tree['levels'][level]
                    count = level_data['count']
                    earnings = level_data['earnings']
                    percentage = self.level_percentages.get(level, 0)
                    
                    text += (
                        f"<b>Уровень {level}</b> ({percentage}% от пополнений)\n"
                        f"   Рефералов: {count}\n"
                        f"   Заработано: {earnings:.2f}₽\n\n"
                    )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="referral")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
    
    def register_handlers(self, dp: Dispatcher):
        """Регистрация обработчиков"""
        from aiogram.filters import Command
        
        # Команды
        dp.message.register(self.referral_command, Command("invite"))
        
        # Callbacks
        dp.callback_query.register(self.referral_callback, F.data == "referral")
        dp.callback_query.register(self.referral_stats_detailed_callback, F.data == "referral_stats_detailed")
        
        logger.info("✅ Обработчики реферальной системы зарегистрированы")
