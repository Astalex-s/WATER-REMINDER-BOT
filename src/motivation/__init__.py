"""
Модули системы мотивации
"""
from .manager import MotivationManager
from .messages import MotivationMessages

# Глобальные экземпляры
motivation_manager = MotivationManager()
motivation_messages = MotivationMessages()


