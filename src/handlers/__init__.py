"""
Обработчики команд и кнопок для бота WaterReminder
"""
from .commands import router as commands_router, send_reminder_message
from .callbacks import router as callbacks_router

# Объединяем все роутеры
__all__ = ['commands_router', 'callbacks_router', 'send_reminder_message']


