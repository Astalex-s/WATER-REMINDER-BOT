"""
Модули для работы с базой данных
"""
from .manager import DatabaseManager
from .models import User, WaterIntake, Reminder, MotivationLog

# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()


