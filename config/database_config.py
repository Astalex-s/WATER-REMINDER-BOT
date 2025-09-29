"""
Конфигурация базы данных
"""

# SQL запросы для создания таблиц
CREATE_TABLES = {
    'users': """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            daily_goal INTEGER DEFAULT 2000,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_motivation_date DATE
        )
    """,
    
    'water_intake': """
        CREATE TABLE IF NOT EXISTS water_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            volume INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reminder_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """,
    
    'reminders': """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            scheduled_time TIMESTAMP,
            reminder_type TEXT DEFAULT 'regular',
            status TEXT DEFAULT 'pending',
            attempt_number INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """,
    
    'motivation_log': """
        CREATE TABLE IF NOT EXISTS motivation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message_type TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_text TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """
}

# Индексы для оптимизации
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_water_intake_user_date ON water_intake(user_id, DATE(timestamp))",
    "CREATE INDEX IF NOT EXISTS idx_reminders_scheduled ON reminders(scheduled_time, status)",
    "CREATE INDEX IF NOT EXISTS idx_motivation_log_user_date ON motivation_log(user_id, DATE(sent_at))"
]


