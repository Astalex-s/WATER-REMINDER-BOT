"""
Основной модуль бота WaterReminder
"""
from .bot import bot, dp
from .startup import on_startup, on_shutdown

__all__ = ['bot', 'dp', 'on_startup', 'on_shutdown']


