"""
Основной файл запуска бота WaterReminder
"""
import asyncio
import logging
import sys
import os

from src.bot import bot, dp, on_startup, on_shutdown
from config import settings

# Настройка логирования
def setup_logging():
    """Настройка логирования"""
    # Очищаем существующие обработчики
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Создаем новый обработчик
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Создаем форматтер
    formatter = logging.Formatter(settings.LOG_FORMAT)
    handler.setFormatter(formatter)
    
    # Настраиваем корневой логгер
    logging.root.setLevel(getattr(logging, settings.LOG_LEVEL))
    logging.root.addHandler(handler)

# Настраиваем логирование
setup_logging()

logger = logging.getLogger(__name__)


async def main():
    """Основная функция"""
    try:
        # Небольшая задержка для избежания конфликтов
        await asyncio.sleep(2)
        
        # Регистрируем функции запуска и остановки
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Запускаем бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")