"""
Обработчики команд бота
"""
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.database import db_manager
from src.motivation import motivation_manager
from src.stats import stats_manager
from src.scheduler import scheduler
from config import settings

# Создаем роутер
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Создаем пользователя в базе данных
    await db_manager.create_user(user_id, username)
    
    # Планируем ежедневные напоминания
    await scheduler.schedule_daily_reminders(user_id)
    
    # Приветственное сообщение
    welcome_text = """
💧 *Добро пожаловать в WaterReminder!* 🌊

Я ваш персональный гид к здоровой привычке пить воду! 

🎯 *Моя цель:* помочь вам выпивать 2 литра воды в день
⏰ *Расписание:* напоминания с 8:00 до 22:00
📊 *Статистика:* отслеживание прогресса и мотивация
💫 *Мотивация:* вдохновляющие сообщения и научные факты

*Что я буду делать:*
• Напоминать пить воду каждые 1 час 45 минут
• Отслеживать ваш прогресс к цели 2000мл
• Мотивировать интересными фактами о воде
• Показывать статистику и достижения

🚀 *Начнем наш путь к здоровью!*

Используйте команды:
/stats - ваша статистика за сегодня
/settings - настройки цели
/motivate - случайная мотивация

💝 *Помните:* каждый глоток воды - это забота о себе!
"""
    
    # Создаем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Начать путь", callback_data="start_journey"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ],
        [
            InlineKeyboardButton(text="💫 Мотивация", callback_data="motivate")
        ]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
    await state.clear()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обработчик команды /stats"""
    user_id = message.from_user.id
    
    # Получаем статистику за сегодня
    stats = await stats_manager.get_daily_stats(user_id)
    
    if not stats:
        await message.answer("❌ Ошибка получения статистики. Попробуйте позже.")
        return
    
    # Формируем сообщение со статистикой
    stats_text = f"""
📊 *Ваша статистика за сегодня*

{stats['progress_bar']}

*Текущий результат:* {stats['current_ml']}/{stats['goal_ml']} мл
*Процент выполнения:* {stats['percentage']:.1f}%
*Статус:* {stats['status_text']}

*Приемов воды:* {stats['intake_count']}
*Средний объем за прием:* {stats['avg_per_intake']:.0f} мл
*Следующее напоминание:* {stats['next_reminder']}

{motivation_manager.get_progress_bar(stats['current_ml'], stats['goal_ml'])}
"""
    
    # Добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Недельная статистика", callback_data="weekly_stats"),
            InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements")
        ],
        [
            InlineKeyboardButton(text="📋 История приемов", callback_data="intake_history")
        ]
    ])
    
    await message.answer(stats_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Обработчик команды /settings"""
    user_id = message.from_user.id
    
    # Получаем данные пользователя
    user = await db_manager.get_user(user_id)
    if not user:
        await message.answer("❌ Ошибка получения настроек. Попробуйте позже.")
        return
    
    settings_text = f"""
⚙️ *Настройки WaterReminder*

*Текущая дневная цель:* {user.daily_goal} мл
*Время напоминаний:* 8:00 - 22:00
*Интервал:* каждые 1 час 45 минут
*Объем за прием:* 250 мл

Выберите, что хотите изменить:
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎯 Изменить цель", callback_data="change_goal")
        ],
        [
            InlineKeyboardButton(text="⏰ Изменить время", callback_data="change_time")
        ],
        [
            InlineKeyboardButton(text="🔔 Уведомления", callback_data="toggle_notifications")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
        ]
    ])
    
    await message.answer(settings_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("motivate"))
async def cmd_motivate(message: Message):
    """Обработчик команды /motivate"""
    user_id = message.from_user.id
    
    # Получаем случайное мотивационное сообщение
    motivation_text = await motivation_manager.get_random_motivation(user_id)
    
    if not motivation_text:
        motivation_text = "💧 *Помните:* каждый глоток воды - это забота о себе! ✨"
    
    # Добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💫 Еще мотивации", callback_data="motivate"),
            InlineKeyboardButton(text="🔬 Научные факты", callback_data="scientific_facts")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
        ]
    ])
    
    await message.answer(motivation_text, reply_markup=keyboard, parse_mode="Markdown")


# Функция для отправки напоминаний (используется планировщиком)
async def send_reminder_message(user_id: int, reminder_id: int, reminder_type: str):
    """Отправить напоминание пользователю"""
    from src.bot import bot
    
    try:
        # Получаем мотивационное сообщение
        if reminder_type == 'morning':
            message_text = await motivation_manager.get_morning_motivation(user_id)
        elif reminder_type == 'follow_up':
            message_text = await motivation_manager.get_follow_up_reminder(user_id)
        else:
            message_text = await motivation_manager.get_water_reminder(user_id)
        
        # Создаем кнопки
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Выпил(250мл)", callback_data=f"water_intake_250_{reminder_id}"),
                InlineKeyboardButton(text="🔄 Выпил больше", callback_data=f"water_intake_custom_{reminder_id}")
            ],
            [
                InlineKeyboardButton(text="⏰ Напомнить позже", callback_data=f"postpone_{reminder_id}"),
                InlineKeyboardButton(text="💫 Мотивация!", callback_data="motivate")
            ]
        ])
        
        # Отправляем сообщение
        await bot.send_message(user_id, message_text, reply_markup=keyboard, parse_mode="Markdown")
        
        # Отмечаем напоминание как отправленное
        await db_manager.mark_reminder_completed(reminder_id)
        
    except Exception as e:
        print(f"Ошибка отправки напоминания: {e}")
        # Отмечаем напоминание как пропущенное при ошибке
        await db_manager.mark_reminder_skipped(reminder_id)


