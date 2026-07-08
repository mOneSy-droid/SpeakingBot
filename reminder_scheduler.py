"""Daily reminder scheduler"""
import asyncio
from datetime import datetime, time, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

import database as db


scheduler = None
bot = None


def init_scheduler(bot_instance: Bot):
    """Initialize the scheduler with bot instance"""
    global scheduler, bot
    bot = bot_instance
    scheduler = AsyncIOScheduler()


async def start_scheduler():
    """Start the reminder scheduler"""
    if scheduler:
        scheduler.add_job(
            check_and_send_reminders,
            'interval',
            minutes=5,  # Check every 5 minutes
            id='daily_reminder_check',
        )
        scheduler.start()
        print("✅ Reminder scheduler started")


async def stop_scheduler():
    """Stop the reminder scheduler"""
    if scheduler and scheduler.running:
        scheduler.shutdown()
        print("⛔ Reminder scheduler stopped")


async def check_and_send_reminders():
    """Check if any users need daily reminder and send it"""
    if not bot:
        return
    
    users = await db.get_all_users_for_reminder()
    now = datetime.now(timezone.utc)
    
    for telegram_id, reminder_time_str in users:
        try:
            # Parse reminder time (HH:MM format)
            reminder_hour, reminder_minute = map(int, reminder_time_str.split(':'))
            
            # Get current time in user's context
            current_hour = now.hour
            current_minute = now.minute
            
            # Check if it's time to send reminder (within this minute)
            if current_hour == reminder_hour and current_minute == reminder_minute:
                # Check if already sent today
                last_practice = await db.get_last_practice_date(telegram_id)
                today = now.strftime('%Y-%m-%d')
                
                if last_practice != today:
                    # Send reminder
                    try:
                        await bot.send_message(
                            chat_id=telegram_id,
                            text=(
                                "🔔 **Bugun mashq qilmadingiz!**\n\n"
                                "Bugungi mashqlarga vaqtingiz barmisada?\n\n"
                                "🎤 Speaking Practice\n"
                                "📚 Vocabulary\n"
                                "✍️ Speech Tuzatish\n\n"
                                "Urinib ko'ring!"
                            ),
                            parse_mode='HTML'
                        )
                        
                        # Log reminder
                        async with __import__('aiosqlite').connect(__import__('config').DB_PATH) as db_conn:
                            await db_conn.execute(
                                "INSERT INTO reminder_logs (telegram_id, reminded_at) VALUES (?, ?)",
                                (telegram_id, now.isoformat()),
                            )
                            await db_conn.commit()
                    except Exception as e:
                        print(f"Error sending reminder to {telegram_id}: {e}")
        except Exception as e:
            print(f"Error processing reminder for user {telegram_id}: {e}")


async def set_reminder_time(telegram_id: int, time_str: str) -> bool:
    """
    Set reminder time for user
    
    Args:
        telegram_id: User's telegram ID
        time_str: Time in HH:MM format
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate time format
        hour, minute = map(int, time_str.split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            return False
        
        await db.set_reminder_time(telegram_id, time_str)
        return True
    except:
        return False


def get_reminder_help() -> str:
    """Get help text for setting reminders"""
    return """⏰ **Kunlik Eslatma (Daily Reminder)**

Bu xususiyat sizga har kuni soat 8:00 da (yoki siz belgilagan vaqtda) "Bugun mashq qilmadingiz" deb xabar yuboradi.

🎯 Foydalanish:
1. /set_reminder komondasini kiriting
2. Istalgan soatni kiriting (masalan: 08:00)
3. Shundan beri har o'sha soatda xabar olasiz

💡 Foydasi:
• Kunlik mashqni o'tkazib yuborisdan saqlaydi
• Routining qismi bo'lib qoladi
• Progres qilish uchun motivatsiya

✏️ Misollar:
/set_reminder 08:00 - Ertalab 8:00
/set_reminder 14:30 - Tushdan so'ng 14:30
/set_reminder 19:00 - Kechqurun 19:00
"""
