"""Quiz sozlamalari — fan, mavzu, rejim, savol soni, tartib, vaqt, skip"""
from contextlib import suppress
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from states.quiz_states import QuizStates
from keyboards.inline import (mode_kb, topics_kb, count_kb, order_kb,
                               time_kb, skip_limit_kb, subjects_kb)
from utils.quiz_data import get_subject, get_topics_with_counts

router = Router()


# ===== FAN TANLASH =====
@router.callback_query(F.data.startswith("sub:"))
async def choose_subject(callback: CallbackQuery, state: FSMContext):
    subject_id = callback.data.split(":")[1]
    if subject_id == "locked":
        await callback.answer("🔒 Tez orada qo'shiladi!", show_alert=True)
        return

    subj = get_subject(subject_id)
    if not subj:
        await callback.answer("❌ Fan topilmadi", show_alert=True)
        return

    await state.update_data(subject_id=subject_id)
    await state.set_state(QuizStates.choosing_mode)
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            f"📘 <b>{subj['full_name']}</b>\n"
            f"📊 {subj['total']} ta savol | {subj['total_topics']} ta mavzu\n\n"
            f"📝 <b>Test rejimini tanlang:</b>",
            reply_markup=mode_kb(),
            parse_mode="HTML"
        )


# ===== REJIM TANLASH =====
@router.callback_query(F.data.startswith("mode:"))
async def choose_mode(callback: CallbackQuery, state: FSMContext):
    mode = callback.data.split(":")[1]
    data = await state.get_data()
    subject_id = data.get("subject_id", "miich")
    await state.update_data(test_mode=mode)

    if mode == "topic":
        await state.set_state(QuizStates.choosing_topic)
        topics = get_topics_with_counts(subject_id)
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(
                "📘 <b>Mavzuni tanlang:</b>",
                reply_markup=topics_kb(topics, subject_id),
                parse_mode="HTML"
            )
    else:
        # Aralash — mavzu tanlanmaydi, to'g'ridan-to'g'ri savol soniga
        subj = get_subject(subject_id)
        await state.update_data(topic_index=None, topic_name="Aralash")
        await state.set_state(QuizStates.choosing_count)
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(
                "📊 <b>Nechta savol ishlaysiz?</b>",
                reply_markup=count_kb(subj["total"]),
                parse_mode="HTML"
            )


# ===== MAVZU TANLASH =====
@router.callback_query(F.data.startswith("topic:"))
async def choose_topic(callback: CallbackQuery, state: FSMContext):
    topic_idx = int(callback.data.split(":")[1])
    data = await state.get_data()
    subject_id = data.get("subject_id", "miich")
    subj = get_subject(subject_id)
    topic_name = subj["topic_names"][topic_idx]
    topic_count = len(subj["topics"][topic_name])

    await state.update_data(topic_index=topic_idx, topic_name=topic_name)
    await state.set_state(QuizStates.choosing_count)
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            f"📘 <b>{topic_name}</b>\n"
            f"📊 {topic_count} ta savol mavjud\n\n"
            f"📊 <b>Nechta savol ishlaysiz?</b>",
            reply_markup=count_kb(topic_count),
            parse_mode="HTML"
        )


# ===== SAVOL SONI =====
@router.callback_query(F.data.startswith("count:"))
async def choose_count(callback: CallbackQuery, state: FSMContext):
    count = int(callback.data.split(":")[1])
    await state.update_data(question_count=count)
    await state.set_state(QuizStates.choosing_order)
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            f"📝 Savollar soni: <b>{count} ta</b>\n\n"
            f"🔄 <b>Savollar tartibini tanlang:</b>",
            reply_markup=order_kb(),
            parse_mode="HTML"
        )


# ===== TARTIB =====
@router.callback_query(F.data.startswith("order:"))
async def choose_order(callback: CallbackQuery, state: FSMContext):
    order = callback.data.split(":")[1]
    order_text = "Ketma-ket" if order == "sequential" else "Aralash"
    await state.update_data(question_order=order)
    await state.set_state(QuizStates.choosing_time)
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            f"🔄 Tartib: <b>{order_text}</b>\n\n"
            f"⏱ <b>Har bir savol uchun vaqt chegarasi:</b>",
            reply_markup=time_kb(),
            parse_mode="HTML"
        )


# ===== VAQT =====
@router.callback_query(F.data.startswith("time:"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    time_limit = int(callback.data.split(":")[1])
    time_text = "Cheksiz" if time_limit == 0 else f"{time_limit} soniya"
    await state.update_data(time_limit=time_limit)
    await state.set_state(QuizStates.choosing_skip_limit)
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            f"⏱ Vaqt: <b>{time_text}</b>\n\n"
            f"⚠️ <b>Ketma-ket nechta savol o'tkazilsa test to'xtasin?</b>",
            reply_markup=skip_limit_kb(),
            parse_mode="HTML"
        )


# ===== O'TKAZISH LIMITI =====
@router.callback_query(F.data.startswith("skip:"))
async def choose_skip_limit(callback: CallbackQuery, state: FSMContext):
    skip_limit = int(callback.data.split(":")[1])
    await state.update_data(skip_limit=skip_limit)

    # Xulosa va testni boshlash
    data = await state.get_data()
    time_text = "Cheksiz" if data["time_limit"] == 0 else f"{data['time_limit']}s"
    order_text = "Ketma-ket" if data["question_order"] == "sequential" else "Aralash"
    skip_text = "Cheksiz" if skip_limit == 0 else f"{skip_limit} ta"

    from keyboards.inline import InlineKeyboardMarkup, InlineKeyboardButton
    start_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Testni boshlash!", callback_data="quiz:start")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_time")],
    ])

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            f"⚙️ <b>Test sozlamalari:</b>\n\n"
            f"📘 Fan: <b>{data.get('topic_name', 'Aralash')}</b>\n"
            f"📊 Savollar: <b>{data['question_count']} ta</b>\n"
            f"🔄 Tartib: <b>{order_text}</b>\n"
            f"⏱ Vaqt: <b>{time_text}</b>\n"
            f"⚠️ O'tkazish: <b>{skip_text}</b>\n\n"
            f"Tayyor bo'lsangiz, boshlang! 👇",
            reply_markup=start_kb,
            parse_mode="HTML"
        )


# ===== ORQAGA TUGMALARI =====
@router.callback_query(F.data == "back_mode")
async def back_to_mode(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subject_id = data.get("subject_id", "miich")
    subj = get_subject(subject_id)
    await state.set_state(QuizStates.choosing_mode)
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            f"📘 <b>{subj['full_name']}</b>\n\n📝 <b>Test rejimini tanlang:</b>",
            reply_markup=mode_kb(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "back_count")
async def back_to_count(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subject_id = data.get("subject_id", "miich")
    subj = get_subject(subject_id)
    topic_idx = data.get("topic_index")
    if topic_idx is not None:
        max_c = len(subj["topics"][subj["topic_names"][topic_idx]])
    else:
        max_c = subj["total"]
    await state.set_state(QuizStates.choosing_count)
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            "📊 <b>Nechta savol ishlaysiz?</b>",
            reply_markup=count_kb(max_c),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "back_order")
async def back_to_order(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.choosing_order)
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            "🔄 <b>Savollar tartibini tanlang:</b>",
            reply_markup=order_kb(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "back_time")
async def back_to_time(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.choosing_time)
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            "⏱ <b>Har bir savol uchun vaqt chegarasi:</b>",
            reply_markup=time_kb(),
            parse_mode="HTML"
        )
