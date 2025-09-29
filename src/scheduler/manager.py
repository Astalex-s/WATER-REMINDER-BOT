"""
Планировщик напоминаний о воде
"""
import asyncio
from datetime import datetime, timedelta, time
from typing import List, Dict, Any

from config import settings
from src.database import db_manager


class ReminderScheduler:
    """Планировщик напоминаний о воде"""
    
    def __init__(self):
        self.running = False
        self.tasks = {}
    
    async def start(self):
        """Запустить планировщик"""
        if self.running:
            return
        
        self.running = True
        asyncio.create_task(self._scheduler_loop())
    
    async def stop(self):
        """Остановить планировщик"""
        self.running = False
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()
    
    async def _scheduler_loop(self):
        """Основной цикл планировщика"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Получаем все ожидающие напоминания
                pending_reminders = await db_manager.get_pending_reminders(current_time)
                
                for reminder in pending_reminders:
                    await self._process_reminder(reminder)
                
                # Ждем 30 секунд перед следующей проверкой
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"Ошибка в планировщике: {e}")
                await asyncio.sleep(60)
    
    async def _process_reminder(self, reminder):
        """Обработать одно напоминание"""
        reminder_id = reminder.id
        user_id = reminder.user_id
        reminder_type = reminder.reminder_type
        attempt_number = reminder.attempt_number
        
        # Проверяем, не превышено ли количество попыток для повторных напоминаний
        if reminder_type == 'follow_up' and attempt_number >= settings.MAX_FOLLOW_UPS:
            await db_manager.mark_reminder_skipped(reminder_id)
            return
        
        # Отправляем напоминание (это будет реализовано в handlers)
        from src.handlers import send_reminder_message
        await send_reminder_message(user_id, reminder_id, reminder_type)
    
    async def schedule_daily_reminders(self, user_id: int):
        """Запланировать ежедневные напоминания для пользователя"""
        # Удаляем старые напоминания пользователя
        await self._clear_user_reminders(user_id)
        
        # Создаем новые напоминания на сегодня
        today = datetime.now().date()
        start_time = datetime.combine(today, time(settings.WORK_START_HOUR, 0))
        
        # Рассчитываем время напоминаний
        reminder_times = []
        current_time = start_time
        
        while current_time.hour < settings.WORK_END_HOUR:
            reminder_times.append(current_time)
            current_time += timedelta(minutes=settings.REMINDER_INTERVAL_MINUTES)
        
        # Создаем напоминания в базе данных
        for i, reminder_time in enumerate(reminder_times):
            # Первое напоминание - утреннее
            reminder_type = 'morning' if i == 0 else 'regular'
            await db_manager.create_reminder(user_id, reminder_time, reminder_type)
    
    async def _clear_user_reminders(self, user_id: int):
        """Удалить все напоминания пользователя"""
        def _clear_reminders():
            import sqlite3
            with sqlite3.connect(db_manager.db_path) as conn:
                conn.execute(
                    "DELETE FROM reminders WHERE user_id = ? AND status = 'pending'",
                    (user_id,)
                )
                conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _clear_reminders)
    
    async def create_follow_up_reminder(self, user_id: int, original_reminder_id: int):
        """Создать повторное напоминание"""
        return await db_manager.create_follow_up_reminder(
            user_id, original_reminder_id, settings.FOLLOW_UP_DELAY_MINUTES
        )
    
    async def mark_reminder_completed(self, reminder_id: int):
        """Отметить напоминание как выполненное"""
        await db_manager.mark_reminder_completed(reminder_id)
    
    async def mark_reminder_skipped(self, reminder_id: int):
        """Отметить напоминание как пропущенное"""
        await db_manager.mark_reminder_skipped(reminder_id)
    
    async def postpone_reminder(self, reminder_id: int, minutes: int = 10):
        """Отложить напоминание на указанное количество минут"""
        def _postpone():
            import sqlite3
            with sqlite3.connect(db_manager.db_path) as conn:
                # Получаем текущее время напоминания
                cursor = conn.execute(
                    "SELECT scheduled_time FROM reminders WHERE id = ?", (reminder_id,)
                )
                row = cursor.fetchone()
                if row:
                    new_time = datetime.fromisoformat(row[0]) + timedelta(minutes=minutes)
                    conn.execute(
                        "UPDATE reminders SET scheduled_time = ? WHERE id = ?",
                        (new_time, reminder_id)
                    )
                    conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _postpone)
    
    def get_reminder_schedule(self) -> List[time]:
        """Получить расписание напоминаний на день"""
        start_time = time(settings.WORK_START_HOUR, 0)
        schedule = []
        current_time = start_time
        
        while current_time.hour < settings.WORK_END_HOUR:
            schedule.append(current_time)
            # Добавляем интервал
            total_minutes = current_time.hour * 60 + current_time.minute + settings.REMINDER_INTERVAL_MINUTES
            hours = total_minutes // 60
            minutes = total_minutes % 60
            current_time = time(hours, minutes)
        
        return schedule
    
    async def schedule_daily_reminders(self, user_id: int):
        """Планировать ежедневные напоминания для пользователя"""
        # Отменяем существующие напоминания
        await self.cancel_user_reminders(user_id)
        
        # Получаем настройки времени пользователя
        start_hour, end_hour = await db_manager.get_user_time_settings(user_id)
        
        # Проверяем, включены ли уведомления
        if not await db_manager.is_notifications_enabled(user_id):
            return
        
        # Создаем расписание напоминаний
        schedule = self._create_reminder_schedule(start_hour, end_hour)
        
        # Создаем напоминания в базе данных
        from datetime import datetime, date
        today = date.today()
        
        for reminder_time in schedule:
            # Конвертируем time в datetime для сегодняшнего дня
            reminder_datetime = datetime.combine(today, reminder_time)
            
            await db_manager.create_reminder(
                user_id=user_id,
                scheduled_time=reminder_datetime,
                reminder_type='water_reminder'
            )
    
    async def cancel_user_reminders(self, user_id: int):
        """Отменить все напоминания пользователя"""
        def _cancel_reminders():
            import sqlite3
            with sqlite3.connect(db_manager.db_path) as conn:
                conn.execute(
                    "DELETE FROM reminders WHERE user_id = ? AND status = 'pending'",
                    (user_id,)
                )
                conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _cancel_reminders)
    
    def _create_reminder_schedule(self, start_hour: int, end_hour: int) -> List[time]:
        """Создать расписание напоминаний для пользователя"""
        schedule = []
        current_time = time(start_hour, 0)
        end_time = time(end_hour, 0)
        
        while current_time < end_time:
            schedule.append(current_time)
            # Добавляем интервал
            total_minutes = current_time.hour * 60 + current_time.minute + settings.REMINDER_INTERVAL_MINUTES
            hours = total_minutes // 60
            minutes = total_minutes % 60
            current_time = time(hours, minutes)
        
        return schedule

