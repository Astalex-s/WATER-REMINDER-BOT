# Архитектура WaterReminder Bot

## 🏗️ Обзор архитектуры

WaterReminder Bot построен с использованием модульной архитектуры, которая обеспечивает:

- **Разделение ответственности** - каждый модуль отвечает за свою область
- **Легкость тестирования** - модули можно тестировать независимо
- **Расширяемость** - легко добавлять новые функции
- **Поддерживаемость** - код легко понимать и изменять

## 📁 Структура модулей

### 🎯 Основные модули

#### `config/` - Конфигурация
- **`settings.py`** - Основные настройки бота
- **`database_config.py`** - Конфигурация базы данных

#### `src/bot/` - Основной модуль бота
- **`bot.py`** - Создание бота и диспетчера
- **`startup.py`** - Функции запуска и остановки

#### `src/database/` - Работа с данными
- **`models.py`** - Модели данных (User, WaterIntake, Reminder, MotivationLog)
- **`manager.py`** - Менеджер для работы с SQLite

#### `src/motivation/` - Система мотивации
- **`messages.py`** - Хранение мотивационных сообщений
- **`manager.py`** - Логика выбора и отправки сообщений

#### `src/scheduler/` - Планировщик
- **`manager.py`** - Планирование и отправка напоминаний

#### `src/stats/` - Статистика
- **`manager.py`** - Расчет статистики и прогресса

#### `src/handlers/` - Обработчики
- **`commands.py`** - Обработчики команд (/start, /stats, /settings, /motivate)
- **`callbacks.py`** - Обработчики кнопок

#### `src/states/` - FSM состояния
- **`water_reminder_states.py`** - Состояния для напоминаний
- **`settings_states.py`** - Состояния для настроек
- **`motivation_states.py`** - Состояния для мотивации

## 🔄 Поток данных

### 1. Инициализация
```
main.py → src/bot/startup.py → config/settings.py
       → src/database/manager.py → SQLite
       → src/scheduler/manager.py
```

### 2. Обработка команды /start
```
Пользователь → src/handlers/commands.py → src/database/manager.py
            → src/scheduler/manager.py → src/motivation/manager.py
```

### 3. Обработка напоминания
```
src/scheduler/manager.py → src/handlers/commands.py → src/motivation/manager.py
                       → src/database/manager.py
```

### 4. Обработка кнопки "Выпил"
```
Пользователь → src/handlers/callbacks.py → src/database/manager.py
            → src/stats/manager.py → src/motivation/manager.py
```

## 🗄️ База данных

### Схема таблиц

```sql
-- Пользователи
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    daily_goal INTEGER DEFAULT 2000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_motivation_date DATE
);

-- Приемы воды
CREATE TABLE water_intake (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    volume INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reminder_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Напоминания
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    scheduled_time TIMESTAMP,
    reminder_type TEXT DEFAULT 'regular',
    status TEXT DEFAULT 'pending',
    attempt_number INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Логи мотивации
CREATE TABLE motivation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message_type TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_text TEXT,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
```

### Индексы для оптимизации
```sql
CREATE INDEX idx_water_intake_user_date ON water_intake(user_id, DATE(timestamp));
CREATE INDEX idx_reminders_scheduled ON reminders(scheduled_time, status);
CREATE INDEX idx_motivation_log_user_date ON motivation_log(user_id, DATE(sent_at));
```

## 🔧 Зависимости между модулями

### Граф зависимостей

```
main.py
├── src/bot/
│   ├── config/
│   └── src/handlers/
│       ├── src/database/
│       ├── src/motivation/
│       ├── src/stats/
│       └── src/scheduler/
├── src/database/
│   └── config/
├── src/motivation/
│   └── src/database/
├── src/scheduler/
│   ├── config/
│   └── src/database/
└── src/stats/
    ├── src/database/
    └── src/motivation/
```

### Импорты

```python
# Основные импорты
from config import settings
from src.database import db_manager
from src.motivation import motivation_manager
from src.stats import stats_manager
from src.scheduler import scheduler
```

## 🎨 Паттерны проектирования

### 1. Singleton
- `db_manager` - единственный экземпляр менеджера БД
- `motivation_manager` - единственный экземпляр менеджера мотивации
- `scheduler` - единственный экземпляр планировщика

### 2. Factory
- `MotivationMessages` - фабрика для создания мотивационных сообщений
- `DatabaseManager` - фабрика для создания запросов к БД

### 3. Observer
- Планировщик уведомляет обработчики о наступлении времени напоминания

### 4. State Machine (FSM)
- Состояния для сложных взаимодействий (выбор объема, настройки)

## 🔄 Асинхронное программирование

### Основные принципы
- Все операции с БД асинхронные
- Планировщик работает в отдельной задаче
- Обработчики команд и кнопок асинхронные

### Примеры использования
```python
# Асинхронная работа с БД
async def get_user(user_id: int):
    async with aiosqlite.connect(self.db_path) as db:
        # ...

# Асинхронный планировщик
async def _scheduler_loop(self):
    while self.running:
        # ...
        await asyncio.sleep(30)
```

## 🧪 Тестирование

### Структура тестов
```
tests/
├── __init__.py
├── test_database.py      # Тесты БД
├── test_motivation.py    # Тесты мотивации
├── test_stats.py         # Тесты статистики
└── test_handlers.py      # Тесты обработчиков
```

### Покрытие тестами
- Unit тесты для каждого модуля
- Интеграционные тесты для взаимодействия модулей
- Моки для внешних зависимостей

## 📈 Производительность

### Оптимизации
- **Индексы БД** для быстрого поиска
- **Кэширование** часто используемых данных
- **Асинхронные операции** для параллельной обработки
- **Пакетные операции** для массовых вставок

### Мониторинг
- Логирование всех операций
- Метрики производительности
- Отслеживание ошибок

## 🔒 Безопасность

### Меры безопасности
- **Валидация входных данных** от пользователей
- **Обработка ошибок** и исключений
- **Логирование** всех операций
- **Защита от SQL-инъекций** через параметризованные запросы

### Конфиденциальность
- **Локальное хранение** данных в SQLite
- **Минимальный сбор** персональных данных
- **Очистка старых данных** для конфиденциальности

## 🚀 Масштабируемость

### Горизонтальное масштабирование
- Статeless архитектура
- Возможность запуска нескольких экземпляров
- Внешняя база данных (PostgreSQL, MySQL)

### Вертикальное масштабирование
- Оптимизация запросов к БД
- Кэширование в памяти
- Асинхронная обработка

## 🔮 Планы развития

### Краткосрочные цели
- Веб-интерфейс для управления
- Расширенная аналитика
- Уведомления через другие каналы

### Долгосрочные цели
- Мобильное приложение
- Интеграция с фитнес-трекерами
- ИИ для персонализации

---

💧 **Архитектура создана для здоровья и благополучия!** ✨


