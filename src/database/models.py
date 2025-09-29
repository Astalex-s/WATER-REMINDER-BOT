"""
Модели данных для базы данных
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class User:
    """Модель пользователя"""
    user_id: int
    username: Optional[str] = None
    daily_goal: int = 2000
    created_at: Optional[datetime] = None
    last_motivation_date: Optional[date] = None
    notifications_enabled: bool = True
    start_hour: int = 8
    end_hour: int = 22


@dataclass
class WaterIntake:
    """Модель записи о приеме воды"""
    id: Optional[int] = None
    user_id: int = 0
    volume: int = 0
    timestamp: Optional[datetime] = None
    reminder_id: Optional[int] = None


@dataclass
class Reminder:
    """Модель напоминания"""
    id: Optional[int] = None
    user_id: int = 0
    scheduled_time: Optional[datetime] = None
    reminder_type: str = 'regular'
    status: str = 'pending'
    attempt_number: int = 0
    created_at: Optional[datetime] = None


@dataclass
class MotivationLog:
    """Модель лога мотивационного сообщения"""
    id: Optional[int] = None
    user_id: int = 0
    message_type: str = ''
    sent_at: Optional[datetime] = None
    message_text: str = ''


