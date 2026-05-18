"""Test ishlash logikasi — ASOSIY handler"""
import asyncio
import time
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, PollAnswer
from aiogram.fsm.context import FSMContext

from states.quiz_states import QuizStates
from keyboards.inline import pause_kb, result_kb, main_menu_kb
from utils.quiz_data import get_questions
from database.db import save_test_result, save_answer
from config import get_grade

router = Router()

# Aktiv quiz sessiyalari: {user_id: {poll_id: question_data}}
active_polls = {}
# Vaqt tugashi uchun tasklar
timeout_tasks = {}


async def send_next_question(bot: Bot, user_id: int, state: FSMContext):
    """Keyingi savolni yuborish"""
    data = await state.get_data()
    questions = data.get("questions", [])
    current = data.get("current_index", 0)
    total = len(questions)
    time_limit = data.get("time_limit", 0)

    if current >= total:
        await finish_quiz(bot, user_id, state)
        return

    q = questions[current]
    options = [q["options"]["A"], q["options"]["B"], q["options"]["C"], q["options"]["D"]]
    answer_map = {"A": 0, "B": 1, "C": 2, "D": 3}
    correct_idx = answer_map.get(q["answer"], 0)

    # Quiz yuborish
    poll_msg = await bot.send_poll(
        chat_id=user_id,
        question=f"#{current + 1}/{total} — {q['question']}"[:300],
        options=options,
        type="quiz",
        correct_option_id=correct_idx,
        is_anonymous=False,
        open_period=time_limit if time_limit > 0 else None,
    )

    # Poll IDni saqlash
    if user_id not in active_polls:
        active_polls[user_id] = {}
    active_polls[user_id][poll_msg.poll.id] = {
        "question_id": q["id"],
        "correct_idx": correct_idx,
        "index": current,
    }

    await state.update_data(
        current_index=current,
        current_poll_id=poll_msg.poll.id,
        waiting_answer=True,
    )

    # Vaqt chegarasi bo'lsa — timeout task
    if time_limit > 0:
        # Oldingi task ni bekor qilish
        old_task = timeout_tasks.get(user_id)
        if old_task and not old_task.done():
            old_task.cancel()

        async def timeout_handler():
            await asyncio.sleep(time_limit + 2)  # +2s buffer
            d = await state.get_data()
            if d.get("waiting_answer") and d.get("current_index") == current:
                await handle_skip(bot, user_id, state)

        timeout_tasks[user_id] = asyncio.create_task(timeout_handler())


async def handle_skip(bot: Bot, user_id: int, state: FSMContext):
    """Savol o'tkazildi"""
    data = await state.get_data()
    skipped = data.get("skipped", 0) + 1
    consecutive_skips = data.get("consecutive_skips", 0) + 1
    skip_limit = data.get("skip_limit", 3)
    current = data.get("current_index", 0)

    await state.update_data(
        skipped=skipped,
        consecutive_skips=consecutive_skips,
        current_index=current + 1,
        waiting_answer=False,
    )

    # Skip limit tekshirish
    if skip_limit > 0 and consecutive_skips >= skip_limit:
        await state.set_state(QuizStates.quiz_paused)
        await bot.send_message(
            user_id,
            f"⚠️ <b>{consecutive_skips} ta savol ketma-ket o'tkazildi!</b>\n\n"
            f"Testni davom ettirasizmi?",
            reply_markup=pause_kb(),
            parse_mode="HTML"
        )
        return

    await send_next_question(bot, user_id, state)


async def finish_quiz(bot: Bot, user_id: int, state: FSMContext):
    """Testni yakunlash"""
    data = await state.get_data()
    total = len(data.get("questions", []))
    correct = data.get("correct", 0)
    wrong = data.get("wrong", 0)
    skipped = data.get("skipped", 0)
    start_time = data.get("start_time", time.time())
    duration = int(time.time() - start_time)

    # Foiz va baho
    score = round((correct / total * 100) if total > 0 else 0, 1)
    grade_label, grade_key = get_grade(score)

    # Vaqtni formatlash
    minutes = duration // 60
    seconds = duration % 60
    time_str = f"{minutes} daqiqa {seconds} soniya" if minutes > 0 else f"{seconds} soniya"

    # Natijani bazaga saqlash
    subject_id = data.get("subject_id", "miich")
    await save_test_result(
        user_id, subject_id,
        data.get("topic_name", "Aralash"),
        data.get("test_mode", "mixed"),
        data.get("question_order", "random"),
        data.get("time_limit", 0),
        total, correct, wrong, skipped,
        score, grade_key, duration
    )

    # Progress bar
    filled = int(score / 10)
    bar = "█" * filled + "░" * (10 - filled)

    time_text = "Cheksiz" if data.get("time_limit", 0) == 0 else f"{data['time_limit']}s"
    order_text = "Ketma-ket" if data.get("question_order") == "sequential" else "Aralash"

    await state.set_state(QuizStates.choosing_subject)
    await bot.send_message(
        user_id,
        f"🏁 <b>Test yakunlandi!</b>\n\n"
        f"📘 Mavzu: <b>{data.get('topic_name', 'Aralash')}</b>\n"
        f"⚙️ {order_text} | ⏱ {time_text}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"✅ To'g'ri: <b>{correct}</b>\n"
        f"❌ Noto'g'ri: <b>{wrong}</b>\n"
        f"⏭ O'tkazilgan: <b>{skipped}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📈 Ball: <b>{correct}/{total} ({score}%)</b>\n"
        f"{bar}\n"
        f"{grade_label}\n"
        f"⏱ Vaqt: <b>{time_str}</b>",
        reply_markup=result_kb(),
        parse_mode="HTML"
    )

    # Tozalash
    active_polls.pop(user_id, None)
    old_task = timeout_tasks.pop(user_id, None)
    if old_task and not old_task.done():
        old_task.cancel()


# ===== TESTNI BOSHLASH =====
@router.callback_query(F.data == "quiz:start")
async def start_quiz(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    subject_id = data.get("subject_id", "miich")
    topic_idx = data.get("topic_index")
    count = data.get("question_count", 10)
    order = data.get("question_order", "sequential")

    questions = get_questions(subject_id, topic_idx, count, order)
    if not questions:
        await callback.answer("❌ Savollar topilmadi!", show_alert=True)
        return

    await state.set_state(QuizStates.in_quiz)
    await state.update_data(
        questions=questions,
        current_index=0,
        correct=0,
        wrong=0,
        skipped=0,
        consecutive_skips=0,
        start_time=time.time(),
        waiting_answer=False,
    )

    time_text = "Cheksiz" if data.get("time_limit", 0) == 0 else f"{data['time_limit']}s"

    await callback.message.edit_text(
        f"🚀 <b>Test boshlandi!</b>\n\n"
        f"📊 {len(questions)} ta savol | ⏱ {time_text}\n"
        f"Omad tilaymiz! 🍀",
        parse_mode="HTML"
    )

    await asyncio.sleep(1)
    await send_next_question(bot, callback.from_user.id, state)


# ===== POLL JAVOBINI QAYTA ISHLASH =====
@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer, state: FSMContext, bot: Bot):
    user_id = poll_answer.user.id
    poll_id = poll_answer.poll_id

    user_polls = active_polls.get(user_id, {})
    poll_data = user_polls.get(poll_id)
    if not poll_data:
        return

    data = await state.get_data()
    cur_state = await state.get_state()
    if cur_state != QuizStates.in_quiz.state:
        return

    # Timeout task bekor qilish
    old_task = timeout_tasks.get(user_id)
    if old_task and not old_task.done():
        old_task.cancel()

    selected = poll_answer.option_ids[0] if poll_answer.option_ids else -1
    is_correct = selected == poll_data["correct_idx"]

    correct = data.get("correct", 0)
    wrong = data.get("wrong", 0)

    if is_correct:
        correct += 1
    else:
        wrong += 1

    # Javobni bazaga saqlash
    subject_id = data.get("subject_id", "miich")
    await save_answer(user_id, subject_id, poll_data["question_id"], is_correct)

    current = data.get("current_index", 0)
    await state.update_data(
        correct=correct,
        wrong=wrong,
        consecutive_skips=0,  # Javob berildi — reset
        current_index=current + 1,
        waiting_answer=False,
    )

    # Biroz kutish
    await asyncio.sleep(1.5)

    await send_next_question(bot, user_id, state)


# ===== PAUSE — DAVOM/YAKUNLASH =====
@router.callback_query(F.data == "quiz:resume")
async def resume_quiz(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(QuizStates.in_quiz)
    await state.update_data(consecutive_skips=0)
    await callback.message.edit_text("▶️ <b>Test davom etmoqda...</b>", parse_mode="HTML")
    await asyncio.sleep(0.5)
    await send_next_question(bot, callback.from_user.id, state)


@router.callback_query(F.data == "quiz:finish")
async def finish_early(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.delete()
    await finish_quiz(bot, callback.from_user.id, state)


# ===== QAYTA ISHLASH =====
@router.callback_query(F.data == "quiz:retry")
async def retry_quiz(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    # Oldingi sozlamalar bilan qayta boshlash
    await start_quiz(callback, state, bot)
