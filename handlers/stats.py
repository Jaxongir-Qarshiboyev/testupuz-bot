"""Statistika handler"""
from contextlib import suppress
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from database.db import get_user_stats, get_user_created_at
from keyboards.inline import main_menu_kb

router = Router()


def make_bar(percent: float, length: int = 10) -> str:
    """Progress bar yaratish"""
    filled = int(percent / (100 / length))
    return "█" * filled + "░" * (length - filled)


async def show_stats_message(user_id: int, full_name: str):
    """Statistika xabarini tayyorlash"""
    general, topic_stats = await get_user_stats(user_id)
    created = await get_user_created_at(user_id)

    total_tests = general.get("total_tests", 0)
    total_correct = general.get("total_correct", 0)
    total_questions = general.get("total_questions", 0)
    avg_score = general.get("avg_score", 0)
    best_score = general.get("best_score", 0)

    if total_tests == 0:
        text = (
            f"📊 <b>Statistikangiz</b>\n\n"
            f"👤 {full_name}\n\n"
            f"😔 Siz hali test ishlamagansiz.\n"
            f"📚 Boshlash uchun «Test boshlash» tugmasini bosing!"
        )
        return text

    created_date = created[:10] if created else "Nomalum"

    text = (
        f"📊 <b>Statistikangiz</b>\n\n"
        f"👤 {full_name}\n"
        f"📅 Royxatdan: {created_date}\n\n"
        f"━━━━ <b>UMUMIY</b> ━━━━\n"
        f"📝 Ishlangan testlar: <b>{total_tests}</b>\n"
        f"✅ Togri javoblar: <b>{total_correct}/{total_questions}</b>\n"
        f"📈 Ortacha ball: <b>{avg_score:.1f}%</b>\n"
        f"🏆 Eng yaxshi: <b>{best_score:.1f}%</b>\n"
    )

    if topic_stats:
        text += "\n━━━━ <b>MIICH mavzulari</b> ━━━━\n"
        for t in topic_stats:
            name = t["topic_name"]
            if ":" in name:
                name = name.split(":")[0].strip()
            elif len(name) > 25:
                name = name[:22] + "..."
            pct = t["avg_score"]
            bar = make_bar(pct, 8)
            text += f"📘 {name}: {bar} {pct:.0f}%\n"

    return text


@router.callback_query(F.data == "my_stats")
async def stats_callback(callback: CallbackQuery):
    text = await show_stats_message(
        callback.from_user.id,
        callback.from_user.full_name
    )
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text, reply_markup=main_menu_kb(), parse_mode="HTML"
        )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    text = await show_stats_message(
        message.from_user.id,
        message.from_user.full_name
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")
