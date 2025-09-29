"""
Менеджер статистики и прогресса
"""
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Tuple

from src.database import db_manager
from src.motivation import motivation_manager


class StatsManager:
    """Менеджер статистики и прогресса"""
    
    def __init__(self):
        pass
    
    async def get_daily_stats(self, user_id: int, target_date: date = None) -> Dict[str, Any]:
        """Получить статистику за день"""
        if target_date is None:
            target_date = date.today()
        
        # Получаем данные пользователя
        user = await db_manager.get_user(user_id)
        if not user:
            return {}
        
        goal_ml = user.daily_goal
        current_ml = await db_manager.get_daily_intake(user_id, target_date)
        
        # Рассчитываем процент выполнения
        percentage = min((current_ml / goal_ml) * 100, 100)
        
        # Создаем прогресс-бар
        progress_bar = motivation_manager.get_progress_bar(current_ml, goal_ml)
        
        # Определяем статус
        if percentage >= 100:
            status = "goal_achieved"
            status_text = "🎉 Цель достигнута!"
        elif percentage >= 75:
            status = "almost_there"
            status_text = "🔥 Почти у цели!"
        elif percentage >= 50:
            status = "halfway"
            status_text = "⚡ На полпути!"
        elif percentage >= 25:
            status = "getting_started"
            status_text = "🌱 Начали путь!"
        else:
            status = "just_started"
            status_text = "💧 Только начинаем!"
        
        # Получаем историю приемов за день
        intake_history = await self._get_daily_intake_history(user_id, target_date)
        
        # Рассчитываем средний объем за прием
        avg_per_intake = current_ml / len(intake_history) if intake_history else 0
        
        # Рассчитываем время до следующего напоминания
        next_reminder = await self._get_next_reminder_time()
        
        return {
            'current_ml': current_ml,
            'goal_ml': goal_ml,
            'percentage': percentage,
            'progress_bar': progress_bar,
            'status': status,
            'status_text': status_text,
            'intake_count': len(intake_history),
            'avg_per_intake': avg_per_intake,
            'intake_history': intake_history,
            'next_reminder': next_reminder,
            'date': target_date.isoformat()
        }
    
    async def _get_daily_intake_history(self, user_id: int, target_date: date) -> List[Dict[str, Any]]:
        """Получить историю приемов воды за день"""
        history = await db_manager.get_intake_history(user_id, 50)  # Получаем больше записей
        # Фильтруем по дате
        target_date_str = target_date.isoformat()
        return [
            {
                'volume': record.volume,
                'timestamp': record.timestamp.strftime('%H:%M') if record.timestamp else 'Unknown'
            }
            for record in history
            if record.timestamp and record.timestamp.date() == target_date
        ]
    
    async def _get_next_reminder_time(self) -> str:
        """Получить время следующего напоминания"""
        from src.scheduler import scheduler
        schedule = scheduler.get_reminder_schedule()
        now = datetime.now().time()
        
        for reminder_time in schedule:
            if reminder_time > now:
                return reminder_time.strftime("%H:%M")
        
        return "Завтра в 8:00"
    
    async def get_weekly_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику за неделю"""
        # Получаем данные за последние 7 дней
        weekly_data = await db_manager.get_weekly_stats(user_id)
        
        # Рассчитываем общую статистику
        total_ml = sum(day['total'] for day in weekly_data)
        days_with_data = len(weekly_data)
        avg_daily = total_ml / 7 if weekly_data else 0
        
        # Получаем цель пользователя
        user = await db_manager.get_user(user_id)
        goal_ml = user.daily_goal if user else 2000
        
        # Рассчитываем процент выполнения за неделю
        weekly_percentage = min((total_ml / (goal_ml * 7)) * 100, 100)
        
        # Создаем график прогресса
        chart = self._create_weekly_chart(weekly_data, goal_ml)
        
        # Определяем лучший и худший дни
        best_day = max(weekly_data, key=lambda x: x['total']) if weekly_data else None
        worst_day = min(weekly_data, key=lambda x: x['total']) if weekly_data else None
        
        return {
            'total_ml': total_ml,
            'avg_daily': avg_daily,
            'weekly_percentage': weekly_percentage,
            'days_with_data': days_with_data,
            'chart': chart,
            'best_day': best_day,
            'worst_day': worst_day,
            'goal_ml': goal_ml
        }
    
    def _create_weekly_chart(self, weekly_data: List[Dict[str, Any]], goal_ml: int) -> str:
        """Создать текстовый график недельного прогресса"""
        chart_lines = []
        
        # Создаем заголовок
        chart_lines.append("📊 *Прогресс за неделю:*")
        chart_lines.append("")
        
        # Создаем график для каждого дня
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        
        for i, day_name in enumerate(days):
            if i < len(weekly_data):
                day_data = weekly_data[i]
                percentage = min((day_data['total'] / goal_ml) * 100, 100)
                filled_blocks = int(percentage / 10)
                empty_blocks = 10 - filled_blocks
                
                bar = "█" * filled_blocks + "░" * empty_blocks
                chart_lines.append(f"{day_name}: {bar} {percentage:.0f}% ({day_data['total']}мл)")
            else:
                chart_lines.append(f"{day_name}: ░░░░░░░░░░ 0% (0мл)")
        
        return "\n".join(chart_lines)
    
    async def get_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить достижения пользователя"""
        achievements = []
        
        # Получаем статистику за последние 30 дней
        thirty_days_ago = date.today() - timedelta(days=30)
        consecutive_days = await self._get_consecutive_days(user_id, thirty_days_ago)
        
        # Достижение: 7 дней подряд
        if consecutive_days >= 7:
            achievements.append({
                'name': 'Неделя дисциплины',
                'description': '7 дней подряд выполняли цель по воде',
                'icon': '🏆',
                'unlocked': True
            })
        
        # Достижение: 30 дней подряд
        if consecutive_days >= 30:
            achievements.append({
                'name': 'Месяц мастерства',
                'description': '30 дней подряд выполняли цель по воде',
                'icon': '👑',
                'unlocked': True
            })
        
        # Достижение: 100% выполнение за день
        today_stats = await self.get_daily_stats(user_id)
        if today_stats.get('percentage', 0) >= 100:
            achievements.append({
                'name': 'Идеальный день',
                'description': 'Выполнили 100% цели за день',
                'icon': '💎',
                'unlocked': True
            })
        
        return achievements
    
    async def _get_consecutive_days(self, user_id: int, start_date: date) -> int:
        """Получить количество дней подряд выполнения цели"""
        user = await db_manager.get_user(user_id)
        if not user:
            return 0
        
        goal_ml = user.daily_goal
        consecutive_days = 0
        current_date = date.today()
        
        while current_date >= start_date:
            daily_intake = await db_manager.get_daily_intake(user_id, current_date)
            if daily_intake >= goal_ml:
                consecutive_days += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return consecutive_days
    
    async def get_motivational_summary(self, user_id: int) -> str:
        """Получить мотивационное резюме на основе статистики"""
        daily_stats = await self.get_daily_stats(user_id)
        weekly_stats = await self.get_weekly_stats(user_id)
        
        current_ml = daily_stats['current_ml']
        goal_ml = daily_stats['goal_ml']
        percentage = daily_stats['percentage']
        
        # Создаем мотивационное сообщение
        if percentage >= 100:
            return f"🎉 *Поздравляем!* Вы достигли цели дня! Ваше тело благодарит вас за заботу! ✨"
        elif percentage >= 75:
            return f"🔥 *Отлично!* Вы на финишной прямой! Осталось всего {goal_ml - current_ml}мл до цели! 💪"
        elif percentage >= 50:
            return f"⚡ *Хорошая работа!* Вы уже прошли половину пути! Продолжайте в том же духе! 🌟"
        elif percentage >= 25:
            return f"🌱 *Начали путь!* Каждый глоток воды приближает вас к здоровью! Не останавливайтесь! 💧"
        else:
            return f"💧 *Время начать!* Ваше тело ждет первой порции живительной влаги! Давайте сделаем это! 🚀"


