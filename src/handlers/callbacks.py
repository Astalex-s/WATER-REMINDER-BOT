"""
Обработчики callback-кнопок
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from src.database import db_manager
from src.motivation import motivation_manager
from src.stats import stats_manager
from src.scheduler import scheduler
from src.states import WaterReminderStates, SettingsStates
from config import settings

# Создаем роутер
router = Router()


@router.callback_query(F.data == "start_journey")
async def callback_start_journey(callback: CallbackQuery):
    """Обработчик кнопки 'Начать путь'"""
    await callback.answer()
    
    # Получаем статистику
    stats = await stats_manager.get_daily_stats(callback.from_user.id)
    
    if stats:
        journey_text = f"""
🚀 *Добро пожаловать в ваш путь к здоровью!*

{stats['progress_bar']}

*Текущий результат:* {stats['current_ml']}/{stats['goal_ml']} мл
*Статус:* {stats['status_text']}

*Следующее напоминание:* {stats['next_reminder']}

💧 *Готовы начать?* Я буду напоминать вам пить воду каждые 1 час 45 минут!
"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Выпил(250мл)", callback_data="water_intake_250"),
                InlineKeyboardButton(text="🔄 Выпил больше", callback_data="water_intake_custom")
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(journey_text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await callback.message.edit_text("❌ Ошибка получения данных. Попробуйте позже.")


@router.callback_query(F.data == "water_intake_250")
async def callback_water_intake_250(callback: CallbackQuery):
    """Обработчик кнопки 'Выпил(250мл)'"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Добавляем запись о приеме воды
    await db_manager.add_water_intake(user_id, settings.WATER_PER_SESSION_ML)
    
    # Получаем обновленную статистику
    stats = await stats_manager.get_daily_stats(user_id)
    
    # Получаем сообщение подтверждения
    confirmation_text = await motivation_manager.get_intake_confirmation(
        user_id, stats['current_ml'], stats['goal_ml']
    )
    
    # Проверяем достижение вех
    milestone_messages = []
    for milestone in [50, 75, 95]:
        if stats['percentage'] >= milestone:
            milestone_msg = await motivation_manager.get_milestone_message(user_id, milestone)
            if milestone_msg:
                milestone_messages.append(milestone_msg)
    
    # Проверяем достижение цели
    if stats['percentage'] >= 100:
        goal_msg = await motivation_manager.get_goal_achieved_message(user_id)
        milestone_messages.append(goal_msg)
    
    # Объединяем сообщения
    full_message = confirmation_text
    if milestone_messages:
        full_message += "\n\n" + "\n\n".join(milestone_messages)
    
    # Добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
            InlineKeyboardButton(text="💫 Мотивация", callback_data="motivate")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
        ]
    ])
    
    await callback.message.edit_text(full_message, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "water_intake_custom")
async def callback_water_intake_custom(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Выпил больше'"""
    await callback.answer()
    
    # Показываем меню выбора объема
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="150мл", callback_data="water_volume_150"),
            InlineKeyboardButton(text="200мл", callback_data="water_volume_200")
        ],
        [
            InlineKeyboardButton(text="250мл", callback_data="water_volume_250"),
            InlineKeyboardButton(text="300мл", callback_data="water_volume_300")
        ],
        [
            InlineKeyboardButton(text="500мл", callback_data="water_volume_500")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
        ]
    ])
    
    await callback.message.edit_text(
        "💧 *Выберите объем выпитой воды:*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("water_volume_"))
async def callback_water_volume(callback: CallbackQuery):
    """Обработчик выбора объема воды"""
    await callback.answer()
    
    # Извлекаем объем из callback_data
    volume = int(callback.data.split("_")[-1])
    
    user_id = callback.from_user.id
    
    # Добавляем запись о приеме воды
    await db_manager.add_water_intake(user_id, volume)
    
    # Получаем обновленную статистику
    stats = await stats_manager.get_daily_stats(user_id)
    
    # Получаем сообщение подтверждения
    confirmation_text = await motivation_manager.get_intake_confirmation(
        user_id, stats['current_ml'], stats['goal_ml']
    )
    
    # Проверяем достижение вех
    milestone_messages = []
    for milestone in [50, 75, 95]:
        if stats['percentage'] >= milestone:
            milestone_msg = await motivation_manager.get_milestone_message(user_id, milestone)
            if milestone_msg:
                milestone_messages.append(milestone_msg)
    
    # Проверяем достижение цели
    if stats['percentage'] >= 100:
        goal_msg = await motivation_manager.get_goal_achieved_message(user_id)
        milestone_messages.append(goal_msg)
    
    # Объединяем сообщения
    full_message = confirmation_text
    if milestone_messages:
        full_message += "\n\n" + "\n\n".join(milestone_messages)
    
    # Добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
            InlineKeyboardButton(text="💫 Мотивация", callback_data="motivate")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
        ]
    ])
    
    await callback.message.edit_text(full_message, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "stats")
async def callback_stats(callback: CallbackQuery):
    """Обработчик кнопки статистики"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Получаем статистику за сегодня
    stats = await stats_manager.get_daily_stats(user_id)
    
    if not stats:
        await callback.message.edit_text("❌ Ошибка получения статистики. Попробуйте позже.")
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
"""
    
    # Добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Недельная статистика", callback_data="weekly_stats"),
            InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements")
        ],
        [
            InlineKeyboardButton(text="📋 История приемов", callback_data="intake_history")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
        ]
    ])
    
    await callback.message.edit_text(stats_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "weekly_stats")
async def callback_weekly_stats(callback: CallbackQuery):
    """Обработчик кнопки недельной статистики"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Получаем недельную статистику
    weekly_stats = await stats_manager.get_weekly_stats(user_id)
    
    if not weekly_stats:
        await callback.message.edit_text("❌ Ошибка получения статистики. Попробуйте позже.")
        return
    
    # Формируем сообщение
    weekly_text = f"""
📈 *Недельная статистика*

*Общий объем:* {weekly_stats['total_ml']} мл
*Средний в день:* {weekly_stats['avg_daily']:.0f} мл
*Процент выполнения:* {weekly_stats['weekly_percentage']:.1f}%
*Дней с данными:* {weekly_stats['days_with_data']}/7

{weekly_stats['chart']}
"""
    
    # Добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Дневная статистика", callback_data="stats"),
            InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
        ]
    ])
    
    await callback.message.edit_text(weekly_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "achievements")
async def callback_achievements(callback: CallbackQuery):
    """Обработчик кнопки достижений"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Получаем достижения
    achievements = await stats_manager.get_achievements(user_id)
    
    if not achievements:
        achievements_text = """
🏆 *Достижения*

У вас пока нет достижений, но это только начало!

*Доступные достижения:*
• 🏆 Неделя дисциплины - 7 дней подряд
• 👑 Месяц мастерства - 30 дней подряд
• 💎 Идеальный день - 100% цели за день

Продолжайте пить воду регулярно!
"""
    else:
        achievements_text = "🏆 *Ваши достижения:*\n\n"
        for achievement in achievements:
            achievements_text += f"{achievement['icon']} *{achievement['name']}*\n{achievement['description']}\n\n"
    
    # Добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
            InlineKeyboardButton(text="💫 Мотивация", callback_data="motivate")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
        ]
    ])
    
    await callback.message.edit_text(achievements_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "motivate")
async def callback_motivate(callback: CallbackQuery):
    """Обработчик кнопки мотивации"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
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
    
    await callback.message.edit_text(motivation_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "scientific_facts")
async def callback_scientific_facts(callback: CallbackQuery):
    """Обработчик кнопки научных фактов"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Получаем научный факт
    fact_text = await motivation_manager.get_scientific_fact(user_id)
    
    # Добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔬 Еще факты", callback_data="scientific_facts"),
            InlineKeyboardButton(text="💫 Мотивация", callback_data="motivate")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
        ]
    ])
    
    await callback.message.edit_text(fact_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "settings")
async def callback_settings(callback: CallbackQuery):
    """Обработчик кнопки настроек"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Получаем данные пользователя
    user = await db_manager.get_user(user_id)
    if not user:
        await callback.message.edit_text("❌ Ошибка получения настроек. Попробуйте позже.")
        return
    
    # Определяем статус уведомлений из модели пользователя
    notification_status = "🔔 Включены" if user.notifications_enabled else "🔕 Выключены"
    
    settings_text = f"""
⚙️ *Настройки WaterReminder*

*Текущая дневная цель:* {user.daily_goal} мл
*Время напоминаний:* {user.start_hour:02d}:00 - {user.end_hour:02d}:00
*Интервал:* каждые 1 час 45 минут
*Объем за прием:* 250 мл
*Уведомления:* {notification_status}

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
    
    await callback.message.edit_text(settings_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "change_goal")
async def callback_change_goal(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки изменения цели"""
    await callback.answer()
    
    # Устанавливаем состояние
    await state.set_state(SettingsStates.changing_daily_goal)
    
    # Получаем текущую цель пользователя
    user = await db_manager.get_user(callback.from_user.id)
    current_goal = user.daily_goal if user else 2000
    
    # Показываем варианты целей
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1500мл", callback_data="goal_1500"),
            InlineKeyboardButton(text="2000мл", callback_data="goal_2000")
        ],
        [
            InlineKeyboardButton(text="2500мл", callback_data="goal_2500"),
            InlineKeyboardButton(text="3000мл", callback_data="goal_3000")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="settings")
        ]
    ])
    
    await callback.message.edit_text(
        f"🎯 *Выберите новую дневную цель:*\n\n*Текущая цель:* {current_goal}мл",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("goal_"))
async def callback_set_goal(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора цели"""
    await callback.answer()
    
    # Извлекаем цель из callback_data
    goal = int(callback.data.split("_")[1])
    
    user_id = callback.from_user.id
    
    # Обновляем цель в базе данных
    await db_manager.update_user_goal(user_id, goal)
    
    # Отменяем старые напоминания и планируем новые
    await scheduler.cancel_user_reminders(user_id)
    await scheduler.schedule_daily_reminders(user_id)
    
    # Создаем кнопки для возврата
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="settings"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")
        ]
    ])
    
    # Отправляем подтверждение
    await callback.message.edit_text(
        f"✅ *Цель обновлена!*\n\nНовая дневная цель: {goal}мл\n\nНапоминания будут пересчитаны с учетом новой цели.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await state.clear()


@router.callback_query(F.data == "toggle_notifications")
async def callback_toggle_notifications(callback: CallbackQuery):
    """Обработчик кнопки переключения уведомлений"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Получаем текущие настройки пользователя
    user = await db_manager.get_user(user_id)
    if not user:
        await callback.message.edit_text("❌ Ошибка получения настроек. Попробуйте позже.")
        return
    
    # Переключаем уведомления
    current_status = user.notifications_enabled
    new_status = not current_status
    
    # Обновляем настройки в базе данных
    await db_manager.update_user_notifications(user_id, new_status)
    
    # Обновляем данные пользователя в памяти
    user.notifications_enabled = new_status
    
    # Если уведомления включены, планируем напоминания
    if new_status:
        # Сначала отменяем старые напоминания, затем создаем новые
        await scheduler.cancel_user_reminders(user_id)
        await scheduler.schedule_daily_reminders(user_id)
        status_text = "включены"
        status_icon = "🔔"
    else:
        # Если выключены, отменяем все напоминания
        await scheduler.cancel_user_reminders(user_id)
        status_text = "выключены"
        status_icon = "🔕"
    
    # Показываем результат
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="settings"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")
        ]
    ])
    
    await callback.message.edit_text(
        f"{status_icon} *Уведомления {status_text}!*\n\n"
        f"Напоминания о воде теперь {status_text}.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "change_time")
async def callback_change_time(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки изменения времени"""
    await callback.answer()
    
    # Устанавливаем состояние
    await state.set_state(SettingsStates.changing_time)
    
    # Получаем текущие настройки времени из модели пользователя
    user = await db_manager.get_user(callback.from_user.id)
    if not user:
        await callback.message.edit_text("❌ Ошибка получения настроек. Попробуйте позже.")
        return
    
    start_hour, end_hour = user.start_hour, user.end_hour
    
    # Показываем варианты времени
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="7:00 - 21:00", callback_data="time_7_21"),
            InlineKeyboardButton(text="8:00 - 22:00", callback_data="time_8_22")
        ],
        [
            InlineKeyboardButton(text="9:00 - 23:00", callback_data="time_9_23"),
            InlineKeyboardButton(text="6:00 - 20:00", callback_data="time_6_20")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="settings")
        ]
    ])
    
    await callback.message.edit_text(
        f"⏰ *Выберите время работы напоминаний:*\n\n"
        f"*Текущее время:* {start_hour:02d}:00 - {end_hour:02d}:00",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("time_"))
async def callback_set_time(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора времени"""
    await callback.answer()
    
    # Извлекаем время из callback_data
    time_parts = callback.data.split("_")[1:]  # ['8', '22']
    start_hour = int(time_parts[0])
    end_hour = int(time_parts[1])
    
    user_id = callback.from_user.id
    
    # Обновляем время в базе данных
    await db_manager.update_user_time_settings(user_id, start_hour, end_hour)
    
    # Отменяем старые напоминания и планируем новые с новым временем
    await scheduler.cancel_user_reminders(user_id)
    await scheduler.schedule_daily_reminders(user_id)
    
    # Создаем кнопки для возврата
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="settings"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")
        ]
    ])
    
    # Отправляем подтверждение
    await callback.message.edit_text(
        f"✅ *Время обновлено!*\n\n"
        f"Новое время напоминаний: {start_hour:02d}:00 - {end_hour:02d}:00\n\n"
        f"Напоминания будут пересчитаны с учетом нового времени.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await state.clear()


@router.callback_query(F.data == "intake_history")
async def callback_intake_history(callback: CallbackQuery):
    """Обработчик кнопки истории приемов"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Получаем историю приемов за сегодня
    history = await db_manager.get_user_intake_history(user_id, limit=10)
    
    if not history:
        await callback.message.edit_text(
            "📋 *История приемов*\n\n"
            "За сегодня приемов воды не было.\n"
            "Начните свой путь к здоровью прямо сейчас! 💧",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💧 Выпить воду", callback_data="water_intake_250")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="stats")]
            ]),
            parse_mode="Markdown"
        )
        return
    
    # Формируем сообщение с историей
    history_text = "📋 *История приемов за сегодня*\n\n"
    
    total_ml = 0
    for i, intake in enumerate(history, 1):
        # Преобразуем timestamp в datetime объект, если это строка
        timestamp = intake['timestamp']
        if isinstance(timestamp, str):
            from datetime import datetime
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = timestamp.strftime("%H:%M")
        history_text += f"{i}. {time_str} - {intake['volume']} мл\n"
        total_ml += intake['volume']
    
    history_text += f"\n*Общий объем:* {total_ml} мл"
    
    # Добавляем кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💧 Добавить прием", callback_data="water_intake_250"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="stats")
        ]
    ])
    
    await callback.message.edit_text(
        history_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Назад'"""
    await callback.answer()
    
    # Очищаем состояние
    await state.clear()
    
    # Возвращаемся к главному меню
    await callback_start_journey(callback)

