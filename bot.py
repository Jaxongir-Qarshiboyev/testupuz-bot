"""TestUpUz Bot — Asosiy fayl (Webhook + Polling dual mode)"""
import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from config import BOT_TOKEN, BOT_DESCRIPTION, BOT_ABOUT
from database.db import init_db
from utils.quiz_data import init_all_subjects
from handlers import start, quiz_setup, quiz_play, stats

# Logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Webhook sozlamalari
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
PORT = int(os.getenv("PORT", 8080))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "")  # Render avtomatik beradi


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


async def on_startup(bot: Bot):
    """Webhook o'rnatish"""
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url)
        logger.info(f"✅ Webhook sozlandi: {webhook_url}")


async def on_shutdown(bot: Bot):
    """Webhook o'chirish"""
    await bot.delete_webhook()
    logger.info("Webhook o'chirildi")


# Health check endpoint (UptimeRobot uchun)
async def health_handler(request):
    return web.Response(text="✅ TestUpUz Bot ishlayapti!", status=200)


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

    me = await bot.get_me()
    logger.info(f"🤖 Bot: @{me.username}")

    if RENDER_URL:
        # === WEBHOOK REJIMI (Render uchun) ===
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

        app = web.Application()
        app.router.add_get("/", health_handler)
        app.router.add_get("/health", health_handler)

        webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        logger.info(f"🌐 Webhook rejimi, port: {PORT}")
        await web._run_app(app, host="0.0.0.0", port=PORT)
    else:
        # === POLLING REJIMI (lokal uchun) ===
        logger.info("📡 Polling rejimi (lokal)")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
