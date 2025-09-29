"""
Менеджер мотивационных сообщений
"""
import random
from datetime import datetime, date
from typing import List, Dict, Any

from src.database import db_manager
from .messages import MotivationMessages


class MotivationManager:
    """Менеджер мотивационных сообщений"""
    
    def __init__(self):
        self.messages = MotivationMessages()
    
    async def get_water_reminder(self, user_id: int) -> str:
        """Получить случайное напоминание о воде"""
        # Получаем недавние сообщения, чтобы избежать повторений
        recent = await db_manager.get_recent_motivations(user_id, 1)
        available_messages = [msg for msg in self.messages.messages['water_reminders'] if msg not in recent]
        
        if not available_messages:
            available_messages = self.messages.messages['water_reminders']
        
        message = random.choice(available_messages)
        await db_manager.log_motivation(user_id, 'water_reminder', message)
        return message
    
    async def get_intake_confirmation(self, user_id: int, current_ml: int, goal_ml: int) -> str:
        """Получить сообщение подтверждения приема воды"""
        percentage = (current_ml / goal_ml) * 100
        message_template = self.messages.get_intake_confirmation(percentage)
        message = message_template.format(current=current_ml)
        await db_manager.log_motivation(user_id, 'intake_confirmation', message)
        return message
    
    async def get_milestone_message(self, user_id: int, percentage: int) -> str:
        """Получить сообщение о достижении вехи"""
        message = self.messages.get_milestone_message(percentage)
        if message:
            await db_manager.log_motivation(user_id, 'milestone', message)
        return message
    
    async def get_goal_achieved_message(self, user_id: int) -> str:
        """Получить сообщение о достижении цели"""
        message = self.messages.get_goal_achieved_message()
        await db_manager.log_motivation(user_id, 'goal_achieved', message)
        return message
    
    async def get_follow_up_reminder(self, user_id: int) -> str:
        """Получить повторное напоминание"""
        message = self.messages.get_follow_up_reminder()
        await db_manager.log_motivation(user_id, 'follow_up', message)
        return message
    
    async def get_morning_motivation(self, user_id: int) -> str:
        """Получить утреннее мотивационное сообщение"""
        message = self.messages.get_morning_motivation()
        await db_manager.log_motivation(user_id, 'morning', message)
        return message
    
    async def get_evening_stats(self, user_id: int, current_ml: int, goal_ml: int) -> str:
        """Получить вечернюю статистику"""
        message = self.messages.get_evening_stats(current_ml, goal_ml)
        await db_manager.log_motivation(user_id, 'evening_stats', message)
        return message
    
    async def get_special_motivation(self, user_id: int) -> str:
        """Получить особую мотивацию (не чаще 1 раза в день)"""
        user = await db_manager.get_user(user_id)
        if not user:
            return ""
        
        last_motivation = user.last_motivation_date
        today = date.today()
        
        # Проверяем, отправляли ли уже сегодня особую мотивацию
        if last_motivation and last_motivation == today:
            return ""
        
        message = self.messages.get_special_motivation()
        await db_manager.log_motivation(user_id, 'special', message)
        await db_manager.update_last_motivation_date(user_id)
        return message
    
    async def get_scientific_fact(self, user_id: int) -> str:
        """Получить научный факт"""
        message = self.messages.get_scientific_fact()
        await db_manager.log_motivation(user_id, 'scientific_fact', message)
        return message
    
    async def get_random_motivation(self, user_id: int) -> str:
        """Получить случайное мотивационное сообщение"""
        # Собираем все доступные сообщения
        all_messages = []
        all_messages.extend(self.messages.messages['water_reminders'])
        all_messages.extend(self.messages.messages['intake_confirmations'].values())
        all_messages.extend(self.messages.messages['milestones'].values())
        all_messages.extend(self.messages.messages['follow_ups'])
        all_messages.extend(self.messages.messages['special'])
        all_messages.extend(self.messages.messages['facts'])
        
        # Исключаем недавние сообщения
        recent = await db_manager.get_recent_motivations(user_id, 2)
        available_messages = [msg for msg in all_messages if msg not in recent]
        
        if not available_messages:
            available_messages = all_messages
        
        message = random.choice(available_messages)
        await db_manager.log_motivation(user_id, 'random', message)
        return message
    
    def get_progress_bar(self, current_ml: int, goal_ml: int) -> str:
        """Создать прогресс-бар"""
        return self.messages.get_progress_bar(current_ml, goal_ml)


