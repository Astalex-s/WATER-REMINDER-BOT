"""
Состояния FSM для мотивационных сообщений
"""
from aiogram.fsm.state import State, StatesGroup


class MotivationStates(StatesGroup):
    """Состояния для мотивационных сообщений"""
    
    # Состояние просмотра достижений
    viewing_achievements = State()
    
    # Состояние просмотра статистики
    viewing_statistics = State()
    
    # Состояние просмотра научных фактов
    viewing_facts = State()


