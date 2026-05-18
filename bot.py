"""TestUpUz Bot — Asosiy fayl"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, BOT_DESCRIPTION, BOT_ABOUT
from database.db import init_db
from utils.quiz_data import init_all_subjects
from handlers import start, quiz_setup, quiz_play, stats

# Logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


async def set_bot_info(bot: Bot):
    """Bot tavsifi va buyruqlarini sozlash"""
    from aiogram.types import BotCommand
    try:
        await bot.set_my_description(BOT_DESCRIPTION)
        await bot.set_my_short_description(BOT_ABOUT)
        await bot.set_my_commands([
            BotCommand(command="start", description="🏠 Bosh menyu"),
            BotCommand(command="help", description="ℹ️ Yordam"),
            BotCommand(command="stats", description="📊 Statistikam"),
        ])
        logger.info("✅ Bot info sozlandi")
    except Exception as e:
        logger.warning(f"Bot info sozlashda xato: {e}")


async def main():
    # Bot va Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Router'larni ulash
    dp.include_router(start.router)
    dp.include_router(quiz_setup.router)
    dp.include_router(quiz_play.router)
    dp.include_router(stats.router)

    # Ma'lumotlar bazasini yaratish
    await init_db()
    logger.info("✅ Database tayyor")

    # Savollar bazasini yuklash
    init_all_subjects()
    logger.info("✅ Quiz data yuklandi")

    # Bot ma'lumotlarini sozlash
    await set_bot_info(bot)

    # Botni ishga tushirish
    me = await bot.get_me()
    logger.info(f"🤖 Bot ishga tushdi: @{me.username}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
