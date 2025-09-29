"""
Продвинутый пример использования WaterReminder Bot
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from src.database import db_manager
from src.motivation import motivation_manager
from src.stats import stats_manager
from src.scheduler import scheduler


async def test_motivation_system():
    """Тестирование системы мотивации"""
    
    print("\n🧪 Тестирование системы мотивации:")
    
    user_id = 123456789
    
    # Тест различных типов мотивационных сообщений
    tests = [
        ("Напоминание о воде", motivation_manager.get_water_reminder(user_id)),
        ("Подтверждение приема", motivation_manager.get_intake_confirmation(user_id, 500, 2000)),
        ("Утренняя мотивация", motivation_manager.get_morning_motivation(user_id)),
        ("Повторное напоминание", motivation_manager.get_follow_up_reminder(user_id)),
        ("Особая мотивация", motivation_manager.get_special_motivation(user_id)),
        ("Научный факт", motivation_manager.get_scientific_fact(user_id)),
        ("Случайная мотивация", motivation_manager.get_random_motivation(user_id))
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func
            print(f"✅ {test_name}: {result[:50]}...")
        except Exception as e:
            print(f"❌ {test_name}: {e}")


async def test_stats_system():
    """Тестирование системы статистики"""
    
    print("\n📊 Тестирование системы статистики:")
    
    user_id = 123456789
    
    # Добавляем несколько записей о приемах воды
    volumes = [250, 300, 200, 250, 500]
    for volume in volumes:
        await db_manager.add_water_intake(user_id, volume)
    
    # Получаем статистику
    daily_stats = await stats_manager.get_daily_stats(user_id)
    weekly_stats = await stats_manager.get_weekly_stats(user_id)
    
    print(f"Дневная статистика:")
    print(f"  Текущий объем: {daily_stats['current_ml']} мл")
    print(f"  Процент выполнения: {daily_stats['percentage']:.1f}%")
    print(f"  Прогресс-бар: {daily_stats['progress_bar']}")
    
    print(f"\nНедельная статистика:")
    print(f"  Общий объем: {weekly_stats['total_ml']} мл")
    print(f"  Средний в день: {weekly_stats['avg_daily']:.0f} мл")
    print(f"  Процент выполнения: {weekly_stats['weekly_percentage']:.1f}%")


async def test_scheduler():
    """Тестирование планировщика"""
    
    print("\n⏰ Тестирование планировщика:")
    
    user_id = 123456789
    
    # Получаем расписание напоминаний
    schedule = scheduler.get_reminder_schedule()
    print(f"Расписание напоминаний на день:")
    for i, time_slot in enumerate(schedule, 1):
        print(f"  {i}. {time_slot}")
    
    # Получаем ожидающие напоминания
    pending_reminders = await db_manager.get_pending_reminders(datetime.now())
    print(f"\nОжидающие напоминания: {len(pending_reminders)}")


async def test_database_operations():
    """Тестирование операций с базой данных"""
    
    print("\n🗄️ Тестирование операций с базой данных:")
    
    user_id = 123456789
    
    # Создание пользователя
    user = await db_manager.create_user(user_id, "test_user", 2000)
    print(f"✅ Пользователь создан: {user.user_id}")
    
    # Обновление цели
    await db_manager.update_user_goal(user_id, 2500)
    updated_user = await db_manager.get_user(user_id)
    print(f"✅ Цель обновлена: {updated_user.daily_goal} мл")
    
    # Добавление записей о приемах воды
    for i, volume in enumerate([250, 300, 200, 250, 500]):
        intake_id = await db_manager.add_water_intake(user_id, volume)
        print(f"✅ Запись {i+1} добавлена: ID {intake_id}, объем {volume}мл")
    
    # Получение истории
    history = await db_manager.get_intake_history(user_id, 10)
    print(f"✅ История получена: {len(history)} записей")
    
    # Получение дневного приема
    daily_intake = await db_manager.get_daily_intake(user_id)
    print(f"✅ Дневной прием: {daily_intake} мл")


async def main():
    """Основная функция для тестирования"""
    
    print("🚀 Запуск продвинутого тестирования WaterReminder Bot")
    print("=" * 60)
    
    try:
        # Инициализация
        await db_manager.init_db()
        print("✅ База данных инициализирована")
        
        # Тестирование системы мотивации
        await test_motivation_system()
        
        # Тестирование системы статистики
        await test_stats_system()
        
        # Тестирование планировщика
        await test_scheduler()
        
        # Тестирование операций с БД
        await test_database_operations()
        
        print("\n✅ Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Остановка планировщика
        await scheduler.stop()
        print("\n🛑 Планировщик остановлен")


if __name__ == "__main__":
    asyncio.run(main())


