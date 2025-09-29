"""
Функции запуска и остановки бота
"""
import logging
from src.database import db_manager
from src.scheduler import scheduler

logger = logging.getLogger(__name__)


async def on_startup():
    """Функция запуска бота"""
    print("Starting WaterReminder bot...")
    
    # Инициализируем базу данных
    await db_manager.init_db()
    print("Database initialized")
    
    # Запускаем планировщик
    await scheduler.start()
    print("Scheduler started")
    
    print("WaterReminder bot started successfully!")


async def on_shutdown():
    """Функция остановки бота"""
    print("Stopping WaterReminder bot...")
    
    # Останавливаем планировщик
    await scheduler.stop()
    print("Scheduler stopped")
    
    print("WaterReminder bot stopped")


