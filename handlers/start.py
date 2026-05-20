"""/start va bosh menyu handler'lari"""
from contextlib import suppress
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from keyboards.inline import main_menu_kb, subjects_kb
from database.db import save_user
from config import BOT_DESCRIPTION

router = Router()

WELCOME_TEXT = """🎓 <b>TestUp</b> ga xush kelibsiz!

📚 Universal test platformasi — bilimingizni sinang va rivojlantiring!

🏆 <b>Mavjud fanlar:</b>
• 📘 MIICH — Mobil Ilovalar Ishlab Chiqish (365 savol)
• 📗 DT Sifati — Dasturiy Ta'minot Sifati (256 savol)
• 📙 Ekspert Tizimlar — Sun'iy Intellekt (200 savol)

⬇️ Quyidagi tugmalardan birini tanlang:"""

HELP_TEXT = """ℹ️ <b>TestUp — Yordam</b>

🤖 <b>Bot haqida:</b>
TestUp — turli fanlar bo'yicha test ishlash platformasi. Telegram native quiz formatida ishlaydi.

📋 <b>Qanday ishlash kerak:</b>
1️⃣ «📚 Test boshlash» tugmasini bosing
2️⃣ Fan tanlang (MIICH)
3️⃣ Rejim tanlang (mavzu/aralash)
4️⃣ Sozlamalarni belgilang (savol soni, vaqt, tartib)
5️⃣ Testni ishlang!

⚙️ <b>Sozlamalar:</b>
• <b>Savol soni:</b> 10, 25, 50, 100 yoki barchasi
• <b>Tartib:</b> Ketma-ket yoki aralash
• <b>Vaqt:</b> Cheksiz, 15s, 30s, 60s, 120s
• <b>O'tkazish:</b> 3 ta, 5 ta yoki cheksiz

📊 <b>Baho tizimi:</b>
🏆 90-100% — A'lo (5)
📗 70-89% — Yaxshi (4)
📙 60-69% — Qoniqarli (3)
📕 0-59% — Qoniqarsiz (2)

📊 /stats — Statistikangizni ko'ring
🏠 /start — Bosh menyu"""


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await save_user(message.from_user.id,
                    message.from_user.username or "",
                    message.from_user.full_name or "")
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(WELCOME_TEXT, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "start_test")
async def start_test(callback: CallbackQuery, state: FSMContext):
    from states.quiz_states import QuizStates
    await state.set_state(QuizStates.choosing_subject)
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            "📚 <b>Fan tanlang:</b>",
            reply_markup=subjects_kb(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            HELP_TEXT,
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, reply_markup=main_menu_kb(), parse_mode="HTML")
