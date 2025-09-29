"""
Мотивационные сообщения для бота WaterReminder
"""
import random
from typing import List, Dict, Any


class MotivationMessages:
    """Класс для хранения мотивационных сообщений"""
    
    def __init__(self):
        self.messages = {
            # Напоминания о воде (категория A)
            'water_reminders': [
                "💧 *Время пить воду!* Выпейте 250мл чистой воды. Ваше тело скажет вам спасибо! ✨",
                "🚰 *Водная пауза!* 250мл воды помогут сохранить энергию и ясность ума на весь день! 🌟",
                "💦 *Глоток здоровья!* Не забывайте - вода ускоряет метаболизм и улучшает работу мозга! 🧠",
                "🌊 *Перерыв на гидратацию!* 250мл воды = заряд бодрости + красивая кожа + здоровые органы! 💫"
            ],
            
            # Подтверждения приема (категория B)
            'intake_confirmations': {
                'low': "✅ *Отлично!* Вы выпили 250мл. Всего сегодня: {current}/2000мл\n*Продолжайте в том же духе!* 💪",
                'medium': "🎉 *Супер!* Еще 250мл на пути к здоровью! Всего: {current}/2000мл\n*Вы на полпути к цели!* 🌟",
                'high': "🔥 *Великолепно!* {current}мл уже выпито! Ваши клетки танцуют от радости! 💃",
                'almost': "💎 *Идеально!* {current}мл пройдено! Ваша кожа сияет, органы работают как часы! ✨"
            },
            
            # Вехи прогресса (категория C)
            'milestones': {
                50: "🏆 *50% пройдено!* Вы уже на середине пути к 2 литрам! Осталось всего 1000мл! 🚀",
                75: "⭐ *75% выполнено!* Всего 500мл до полной победы! Вы почти у цели! 💫",
                95: "🎊 *95% достигнуто!* Финишная прямая! Всего один глоток до полного успеха! 🌈"
            },
            
            # Достижение цели (категория D)
            'goal_achieved': "🌈 *ПОБЕДА!* Вы достигли цели дня - 2000мл воды! 🎉\n*Ваше тело благодарит вас за:*\n• 💆‍♂️ Увлажненную кожу\n• 🧠 Ясное мышление\n• 💪 Энергию на весь день\n• 🏃‍♂️ Ускоренный метаболизм\n*Гордитесь собой! Завтра повторим!* ✨",
            
            # Повторные напоминания (категория E)
            'follow_ups': [
                "⏰ *Напоминаем о воде!* Прошло 5 минут - не пропустите прием 250мл воды для вашего здоровья! 💧",
                "💡 *Не забыли о воде?* Всего 250мл помогут сохранить продуктивность и хорошее самочувствие! 🌟"
            ],
            
            # Утренние мотивации (категория F)
            'morning': "🌅 *Доброе утро!* Начните день с 250мл воды натощак - это запустит метаболизм и очистит организм! 💫",
            
            # Вечерние статистики (категория G)
            'evening_stats': "📊 *Итоги дня:* Вы выпили {current}/2000мл! {motivational_phrase}",
            
            # Особые мотивации (категория H)
            'special': [
                "💝 *Любите себя!* Каждый глоток воды - это забота о своем здоровье и красоте! ✨",
                "🎯 *Дисциплина = свобода!* Регулярное питье воды дает энергию для достижения всех целей! 🚀",
                "🌿 *Природа благодарит!* Пить воду - значит помогать своему телу работать в гармонии с природой! 💚"
            ],
            
            # Научные факты (категория I)
            'facts': [
                "🔬 *Знаете ли вы?* Всего 2% обезвоживания снижают концентрацию на 20%. Пейте воду для ясного ума! 🧠",
                "🧪 *Интересный факт!* Вода составляет 60% массы тела взрослого человека. Поддерживайте этот баланс! ⚖️",
                "🔍 *Научно доказано!* Питье воды натощак ускоряет метаболизм на 30%! Начните день правильно! 🚀"
            ]
        }
        
        # Мотивационные фразы для вечерней статистики
        self.evening_phrases = {
            'excellent': "Отличная работа! Вы на правильном пути к здоровью! 🌟",
            'good': "Хороший результат! Завтра будет еще лучше! 💪",
            'average': "Неплохо! Попробуйте увеличить количество воды завтра! 🌱",
            'low': "Не расстраивайтесь! Каждый день - новая возможность! 🌈"
        }
    
    def get_water_reminder(self) -> str:
        """Получить случайное напоминание о воде"""
        return random.choice(self.messages['water_reminders'])
    
    def get_intake_confirmation(self, percentage: float) -> str:
        """Получить сообщение подтверждения приема воды"""
        if percentage <= 25:
            category = 'low'
        elif percentage <= 50:
            category = 'medium'
        elif percentage <= 75:
            category = 'high'
        else:
            category = 'almost'
        
        return self.messages['intake_confirmations'][category]
    
    def get_milestone_message(self, percentage: int) -> str:
        """Получить сообщение о достижении вехи"""
        return self.messages['milestones'].get(percentage, "")
    
    def get_goal_achieved_message(self) -> str:
        """Получить сообщение о достижении цели"""
        return self.messages['goal_achieved']
    
    def get_follow_up_reminder(self) -> str:
        """Получить повторное напоминание"""
        return random.choice(self.messages['follow_ups'])
    
    def get_morning_motivation(self) -> str:
        """Получить утреннее мотивационное сообщение"""
        return self.messages['morning']
    
    def get_evening_stats(self, current_ml: int, goal_ml: int) -> str:
        """Получить вечернюю статистику"""
        percentage = (current_ml / goal_ml) * 100
        
        if percentage >= 100:
            phrase = self.evening_phrases['excellent']
        elif percentage >= 75:
            phrase = self.evening_phrases['good']
        elif percentage >= 50:
            phrase = self.evening_phrases['average']
        else:
            phrase = self.evening_phrases['low']
        
        return self.messages['evening_stats'].format(
            current=current_ml, 
            motivational_phrase=phrase
        )
    
    def get_special_motivation(self) -> str:
        """Получить особую мотивацию"""
        return random.choice(self.messages['special'])
    
    def get_scientific_fact(self) -> str:
        """Получить научный факт"""
        return random.choice(self.messages['facts'])
    
    def get_random_motivation(self) -> str:
        """Получить случайное мотивационное сообщение"""
        all_messages = []
        all_messages.extend(self.messages['water_reminders'])
        all_messages.extend(self.messages['intake_confirmations'].values())
        all_messages.extend(self.messages['milestones'].values())
        all_messages.extend(self.messages['follow_ups'])
        all_messages.extend(self.messages['special'])
        all_messages.extend(self.messages['facts'])
        
        return random.choice(all_messages)
    
    def get_progress_bar(self, current_ml: int, goal_ml: int) -> str:
        """Создать прогресс-бар"""
        percentage = min((current_ml / goal_ml) * 100, 100)
        filled_blocks = int(percentage / 10)
        empty_blocks = 10 - filled_blocks
        
        bar = "💧" * filled_blocks + "⚪" * empty_blocks
        return f"[{bar}] {percentage:.0f}% ({current_ml}/{goal_ml} мл)"


