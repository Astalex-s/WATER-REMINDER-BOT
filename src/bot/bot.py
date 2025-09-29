"""
Основной файл бота WaterReminder
"""
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from src.handlers import commands_router, callbacks_router

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Создаем бота и диспетчер
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем роутеры
dp.include_router(commands_router)
dp.include_router(callbacks_router)


