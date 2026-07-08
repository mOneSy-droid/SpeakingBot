import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
import database as db
from handlers import start, vocab, practice, speech, qa, progress, speaking, pronunciation, review, practice_modes, reports, settings
from reminder_scheduler import init_scheduler, start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)


async def main():
    await db.init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(start.router)
    dp.include_router(vocab.router)
    dp.include_router(pronunciation.router)
    dp.include_router(review.router)
    dp.include_router(practice.router)
    dp.include_router(speech.router)
    dp.include_router(qa.router)
    dp.include_router(speaking.router)
    dp.include_router(practice_modes.router)
    dp.include_router(reports.router)
    dp.include_router(settings.router)
    dp.include_router(progress.router)

    # Initialize and start reminder scheduler
    init_scheduler(bot)
    await start_scheduler()

    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        await dp.start_polling(bot)
    finally:
        await stop_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
