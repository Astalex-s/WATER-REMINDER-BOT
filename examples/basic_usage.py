"""
Базовый пример использования WaterReminder Bot
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from src.database import db_manager
from src.motivation import motivation_manager
from src.stats import stats_manager
from src.scheduler import scheduler


async def basic_example():
    """Базовый пример использования функций бота"""
    
    print("🚀 Запуск примера WaterReminder Bot")
    print("=" * 50)
    
    try:
        # Инициализация базы данных
        await db_manager.init_db()
        print("✅ База данных инициализирована")
        
        # Создание пользователя
        user_id = 123456789
        await db_manager.create_user(user_id, "example_user", 2000)
        print("✅ Пользователь создан")
        
        # Планирование напоминаний
        await scheduler.schedule_daily_reminders(user_id)
        print("✅ Напоминания запланированы")
        
        # Добавление записи о приеме воды
        await db_manager.add_water_intake(user_id, 250)
        print("✅ Запись о приеме воды добавлена")
        
        # Получение статистики
        stats = await stats_manager.get_daily_stats(user_id)
        print(f"📊 Статистика: {stats['current_ml']}/{stats['goal_ml']} мл ({stats['percentage']:.1f}%)")
        
        # Получение мотивационного сообщения
        motivation = await motivation_manager.get_water_reminder(user_id)
        print(f"💫 Мотивация: {motivation}")
        
        # Получение достижений
        achievements = await stats_manager.get_achievements(user_id)
        print(f"🏆 Достижения: {len(achievements)}")
        
        print("\n✅ Пример завершен успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка в примере: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Остановка планировщика
        await scheduler.stop()
        print("\n🛑 Планировщик остановлен")


if __name__ == "__main__":
    asyncio.run(basic_example())


