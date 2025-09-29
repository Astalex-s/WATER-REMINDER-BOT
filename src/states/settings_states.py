"""
Состояния FSM для настроек
"""
from aiogram.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    """Состояния для настроек"""
    
    # Состояние изменения дневной цели
    changing_daily_goal = State()
    
    # Состояние изменения времени напоминаний
    changing_time = State()
    
    # Состояние включения/выключения уведомлений
    toggling_notifications = State()

