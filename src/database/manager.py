"""
Менеджер для работы с базой данных
"""
import sqlite3
import asyncio
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import threading

from config import settings
from config.database_config import CREATE_TABLES, CREATE_INDEXES
from .models import User, WaterIntake, Reminder, MotivationLog


class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self._lock = threading.Lock()
    
    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        def _init():
            with sqlite3.connect(self.db_path) as conn:
                # Создаем таблицы
                for table_name, create_sql in CREATE_TABLES.items():
                    conn.execute(create_sql)
                
                # Создаем индексы
                for index_sql in CREATE_INDEXES:
                    conn.execute(index_sql)
                
                conn.commit()
        
        # Выполняем в отдельном потоке
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _init)
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        def _get_user():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    # Проверяем наличие колонок и используем значения по умолчанию
                    notifications_enabled = 1
                    start_hour = 8
                    end_hour = 22
                    
                    try:
                        notifications_enabled = row['notifications_enabled']
                    except (KeyError, IndexError):
                        pass
                    
                    try:
                        start_hour = row['start_hour']
                    except (KeyError, IndexError):
                        pass
                    
                    try:
                        end_hour = row['end_hour']
                    except (KeyError, IndexError):
                        pass
                    
                    return User(
                        user_id=row['user_id'],
                        username=row['username'],
                        daily_goal=row['daily_goal'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        last_motivation_date=date.fromisoformat(row['last_motivation_date']) if row['last_motivation_date'] else None,
                        notifications_enabled=bool(notifications_enabled),
                        start_hour=start_hour,
                        end_hour=end_hour
                    )
                return None
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_user)
    
    async def create_user(self, user_id: int, username: str = None, daily_goal: int = 2000) -> User:
        """Создать нового пользователя"""
        def _create_user():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO users (user_id, username, daily_goal) VALUES (?, ?, ?)",
                    (user_id, username, daily_goal)
                )
                conn.commit()
                return User(user_id=user_id, username=username, daily_goal=daily_goal)
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _create_user)
    
    async def update_user_goal(self, user_id: int, daily_goal: int):
        """Обновить целевую норму воды для пользователя"""
        def _update_goal():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE users SET daily_goal = ? WHERE user_id = ?",
                    (daily_goal, user_id)
                )
                conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _update_goal)
    
    async def add_water_intake(self, user_id: int, volume: int, reminder_id: int = None) -> int:
        """Добавить запись о приеме воды"""
        def _add_intake():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO water_intake (user_id, volume, reminder_id) VALUES (?, ?, ?)",
                    (user_id, volume, reminder_id)
                )
                conn.commit()
                return cursor.lastrowid
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _add_intake)
    
    async def get_daily_intake(self, user_id: int, target_date: date = None) -> int:
        """Получить общий объем воды за день"""
        if target_date is None:
            target_date = date.today()
        
        def _get_daily_intake():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COALESCE(SUM(volume), 0) as total FROM water_intake WHERE user_id = ? AND DATE(timestamp) = ?",
                    (user_id, target_date.isoformat())
                )
                row = cursor.fetchone()
                return row[0] if row else 0
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_daily_intake)
    
    async def get_intake_history(self, user_id: int, limit: int = 10) -> List[WaterIntake]:
        """Получить историю приемов воды"""
        def _get_history():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM water_intake WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (user_id, limit)
                )
                rows = cursor.fetchall()
                return [
                    WaterIntake(
                        id=row['id'],
                        user_id=row['user_id'],
                        volume=row['volume'],
                        timestamp=datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None,
                        reminder_id=row['reminder_id']
                    )
                    for row in rows
                ]
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_history)
    
    async def create_reminder(self, user_id: int, scheduled_time: datetime, 
                            reminder_type: str = "regular") -> int:
        """Создать напоминание"""
        def _create_reminder():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO reminders (user_id, scheduled_time, reminder_type) VALUES (?, ?, ?)",
                    (user_id, scheduled_time, reminder_type)
                )
                conn.commit()
                return cursor.lastrowid
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _create_reminder)
    
    async def get_pending_reminders(self, user_id: int = None, current_time: datetime = None) -> List[Reminder]:
        """Получить все ожидающие напоминания"""
        def _get_pending():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if user_id and current_time:
                    # Получить напоминания для конкретного пользователя до определенного времени
                    cursor = conn.execute(
                        "SELECT * FROM reminders WHERE user_id = ? AND scheduled_time <= ? AND status = 'pending'",
                        (user_id, current_time)
                    )
                elif user_id:
                    # Получить все напоминания для конкретного пользователя
                    cursor = conn.execute(
                        "SELECT * FROM reminders WHERE user_id = ? AND status = 'pending'",
                        (user_id,)
                    )
                elif current_time:
                    # Получить все напоминания до определенного времени
                    cursor = conn.execute(
                        "SELECT * FROM reminders WHERE scheduled_time <= ? AND status = 'pending'",
                        (current_time,)
                    )
                else:
                    # Получить все ожидающие напоминания
                    cursor = conn.execute(
                        "SELECT * FROM reminders WHERE status = 'pending'"
                    )
                
                rows = cursor.fetchall()
                return [
                    Reminder(
                        id=row['id'],
                        user_id=row['user_id'],
                        scheduled_time=datetime.fromisoformat(row['scheduled_time']) if row['scheduled_time'] else None,
                        reminder_type=row['reminder_type'],
                        status=row['status'],
                        attempt_number=row['attempt_number'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                    )
                    for row in rows
                ]
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_pending)
    
    async def mark_reminder_completed(self, reminder_id: int):
        """Отметить напоминание как выполненное"""
        def _mark_completed():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE reminders SET status = 'completed' WHERE id = ?",
                    (reminder_id,)
                )
                conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _mark_completed)
    
    async def mark_reminder_skipped(self, reminder_id: int):
        """Отметить напоминание как пропущенное"""
        def _mark_skipped():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE reminders SET status = 'skipped' WHERE id = ?",
                    (reminder_id,)
                )
                conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _mark_skipped)
    
    async def create_follow_up_reminder(self, user_id: int, original_reminder_id: int, 
                                      delay_minutes: int = 5) -> int:
        """Создать повторное напоминание"""
        def _create_follow_up():
            with sqlite3.connect(self.db_path) as conn:
                # Получаем информацию об оригинальном напоминании
                cursor = conn.execute(
                    "SELECT * FROM reminders WHERE id = ?", (original_reminder_id,)
                )
                original = cursor.fetchone()
                
                if original:
                    # Создаем новое напоминание с задержкой
                    new_time = datetime.fromisoformat(original[2]) + timedelta(minutes=delay_minutes)
                    cursor = conn.execute(
                        "INSERT INTO reminders (user_id, scheduled_time, reminder_type, attempt_number) VALUES (?, ?, 'follow_up', ?)",
                        (user_id, new_time, original[6] + 1)
                    )
                    conn.commit()
                    return cursor.lastrowid
                return None
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _create_follow_up)
    
    async def log_motivation(self, user_id: int, message_type: str, message_text: str):
        """Записать отправленное мотивационное сообщение"""
        def _log_motivation():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO motivation_log (user_id, message_type, message_text) VALUES (?, ?, ?)",
                    (user_id, message_type, message_text)
                )
                conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _log_motivation)
    
    async def get_recent_motivations(self, user_id: int, hours: int = 24) -> List[str]:
        """Получить недавние мотивационные сообщения"""
        def _get_recent():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT message_text FROM motivation_log WHERE user_id = ? AND sent_at > datetime('now', '-{} hours')".format(hours),
                    (user_id,)
                )
                rows = cursor.fetchall()
                return [row[0] for row in rows]
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_recent)
    
    async def update_last_motivation_date(self, user_id: int):
        """Обновить дату последней особой мотивации"""
        def _update_date():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE users SET last_motivation_date = CURRENT_DATE WHERE user_id = ?",
                    (user_id,)
                )
                conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _update_date)
    
    async def get_weekly_stats(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить статистику за неделю"""
        def _get_weekly_stats():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT DATE(timestamp) as date, SUM(volume) as total 
                    FROM water_intake 
                    WHERE user_id = ? AND timestamp >= date('now', '-7 days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                    """,
                    (user_id,)
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_weekly_stats)
    
    async def update_user_notifications(self, user_id: int, enabled: bool):
        """Обновить настройки уведомлений пользователя"""
        def _update_notifications():
            with sqlite3.connect(self.db_path) as conn:
                # Добавляем колонку если её нет
                try:
                    conn.execute(
                        "ALTER TABLE users ADD COLUMN notifications_enabled INTEGER DEFAULT 1"
                    )
                except sqlite3.OperationalError:
                    pass  # Колонка уже существует
                
                # Обновляем настройки
                conn.execute(
                    "UPDATE users SET notifications_enabled = ? WHERE user_id = ?",
                    (1 if enabled else 0, user_id)
                )
                conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _update_notifications)
    
    async def update_user_time_settings(self, user_id: int, start_hour: int, end_hour: int):
        """Обновить настройки времени пользователя"""
        def _update_time_settings():
            with sqlite3.connect(self.db_path) as conn:
                # Добавляем колонки если их нет
                try:
                    conn.execute(
                        "ALTER TABLE users ADD COLUMN start_hour INTEGER DEFAULT 8"
                    )
                    conn.execute(
                        "ALTER TABLE users ADD COLUMN end_hour INTEGER DEFAULT 22"
                    )
                except sqlite3.OperationalError:
                    pass  # Колонки уже существуют
                
                # Обновляем настройки
                conn.execute(
                    "UPDATE users SET start_hour = ?, end_hour = ? WHERE user_id = ?",
                    (start_hour, end_hour, user_id)
                )
                conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _update_time_settings)
    
    async def get_user_time_settings(self, user_id: int) -> tuple:
        """Получить настройки времени пользователя"""
        def _get_time_settings():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT start_hour, end_hour FROM users WHERE user_id = ?", (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return row['start_hour'] or 8, row['end_hour'] or 22
                return 8, 22  # Значения по умолчанию
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_time_settings)
    
    async def is_notifications_enabled(self, user_id: int) -> bool:
        """Проверить, включены ли уведомления для пользователя"""
        def _check_notifications():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT notifications_enabled FROM users WHERE user_id = ?", (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return bool(row['notifications_enabled'])
                return True  # По умолчанию включены
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _check_notifications)
    
    async def get_user_intake_history(self, user_id: int, limit: int = 10) -> list:
        """Получить историю приемов воды пользователя"""
        def _get_history():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT volume, timestamp FROM water_intake "
                    "WHERE user_id = ? AND DATE(timestamp) = DATE('now') "
                    "ORDER BY timestamp DESC LIMIT ?",
                    (user_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_history)
    
    async def delete_user(self, user_id: int):
        """Удалить пользователя и все связанные данные"""
        def _delete_user():
            with sqlite3.connect(self.db_path) as conn:
                # Удаляем все связанные данные
                conn.execute("DELETE FROM water_intake WHERE user_id = ?", (user_id,))
                conn.execute("DELETE FROM reminders WHERE user_id = ?", (user_id,))
                conn.execute("DELETE FROM motivation_log WHERE user_id = ?", (user_id,))
                conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                conn.commit()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _delete_user)