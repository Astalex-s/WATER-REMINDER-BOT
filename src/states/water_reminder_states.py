"""
Состояния FSM для напоминаний о воде
"""
from aiogram.fsm.state import State, StatesGroup


class WaterReminderStates(StatesGroup):
    """Состояния для напоминаний о воде"""
    
    # Состояние выбора объема воды
    choosing_water_volume = State()
    
    # Состояние просмотра истории
    viewing_history = State()


