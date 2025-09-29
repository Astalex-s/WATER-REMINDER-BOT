"""
Настройки бота WaterReminder
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Класс настроек бота"""
    
    def __init__(self):
        # Токен бота
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        
        # Настройки базы данных
        self.DATABASE_PATH = "water_reminder.db"
        
        # Настройки напоминаний
        self.DAILY_GOAL_ML = 2000  # Целевой объем воды в день (мл)
        self.WATER_PER_SESSION_ML = 250  # Объем за один прием (мл)
        self.REMINDER_INTERVAL_MINUTES = 105  # Интервал между напоминаниями (минуты)
        self.WORK_START_HOUR = 8  # Начало работы (час)
        self.WORK_END_HOUR = 22  # Конец работы (час)
        self.FOLLOW_UP_DELAY_MINUTES = 5  # Задержка повторного напоминания (минуты)
        self.MAX_FOLLOW_UPS = 3  # Максимальное количество повторных напоминаний
        
        # Настройки мотивации
        self.MOTIVATION_COOLDOWN_HOURS = 24  # Кулдаун для особых мотиваций (часы)
        
        # Настройки логирования
        self.LOG_LEVEL = "INFO"
        self.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.LOG_ENCODING = "utf-8"
        
        # Валидация настроек
        self._validate_settings()
    
    def _validate_settings(self):
        """Валидация настроек"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в переменных окружения")
        
        if self.DAILY_GOAL_ML <= 0:
            raise ValueError("DAILY_GOAL_ML должен быть больше 0")
        
        if self.WATER_PER_SESSION_ML <= 0:
            raise ValueError("WATER_PER_SESSION_ML должен быть больше 0")
        
        if self.REMINDER_INTERVAL_MINUTES <= 0:
            raise ValueError("REMINDER_INTERVAL_MINUTES должен быть больше 0")
        
        if not (0 <= self.WORK_START_HOUR < 24):
            raise ValueError("WORK_START_HOUR должен быть от 0 до 23")
        
        if not (0 <= self.WORK_END_HOUR < 24):
            raise ValueError("WORK_END_HOUR должен быть от 0 до 23")
        
        if self.WORK_START_HOUR >= self.WORK_END_HOUR:
            raise ValueError("WORK_START_HOUR должен быть меньше WORK_END_HOUR")


