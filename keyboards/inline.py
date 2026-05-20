"""Barcha inline keyboard'lar"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb():
    """Bosh menyu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Test boshlash", callback_data="start_test")],
        [InlineKeyboardButton(text="📊 Natijalarim", callback_data="my_stats"),
         InlineKeyboardButton(text="ℹ️ Yordam", callback_data="help")],
    ])


def subjects_kb():
    """Fan tanlash"""
    from utils.quiz_data import SUBJECTS
    buttons = []
    for sid, subj in SUBJECTS.items():
        emoji = {"miich": "📘", "dt_sifati": "📗", "ekspert": "📙"}.get(sid, "📚")
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {subj['name']} ({subj['total']} savol)",
            callback_data=f"sub:{sid}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def mode_kb():
    """Test rejimi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Mavzu bo'yicha", callback_data="mode:topic")],
        [InlineKeyboardButton(text="🔀 Aralash (barcha mavzulardan)", callback_data="mode:mixed")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="start_test")],
    ])


def topics_kb(topics_with_counts: list, subject_id: str = "miich"):
    """Mavzular ro'yxati"""
    buttons = []
    for i, (name, count) in enumerate(topics_with_counts):
        short = name.split(":")[0].strip() if ":" in name else name[:30]
        buttons.append([InlineKeyboardButton(
            text=f"📘 {short} ({count})",
            callback_data=f"topic:{i}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"sub:{subject_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def count_kb(max_count: int):
    """Savol soni tanlash"""
    buttons = []
    options = [10, 25, 50, 100]
    row = []
    for n in options:
        if n <= max_count:
            row.append(InlineKeyboardButton(text=f"📝 {n} ta", callback_data=f"count:{n}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text=f"📚 Barchasi ({max_count} ta)", callback_data=f"count:{max_count}")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_mode")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def order_kb():
    """Tartib tanlash"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Ketma-ket (1, 2, 3...)", callback_data="order:sequential")],
        [InlineKeyboardButton(text="🔀 Aralash (random)", callback_data="order:random")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_count")],
    ])


def time_kb():
    """Vaqt chegarasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♾ Cheksiz", callback_data="time:0")],
        [InlineKeyboardButton(text="⚡ 15 soniya", callback_data="time:15"),
         InlineKeyboardButton(text="⏱ 30 soniya", callback_data="time:30")],
        [InlineKeyboardButton(text="🕐 60 soniya", callback_data="time:60"),
         InlineKeyboardButton(text="🕐 120 soniya", callback_data="time:120")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_order")],
    ])


def skip_limit_kb():
    """O'tkazish limiti"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="3️⃣ 3 ta ketma-ket", callback_data="skip:3")],
        [InlineKeyboardButton(text="5️⃣ 5 ta ketma-ket", callback_data="skip:5")],
        [InlineKeyboardButton(text="♾ Cheksiz (to'xtatmaslik)", callback_data="skip:0")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_time")],
    ])


def pause_kb():
    """Test to'xtatilganda"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Davom etish", callback_data="quiz:resume")],
        [InlineKeyboardButton(text="⏹ Yakunlash", callback_data="quiz:finish")],
    ])


def result_kb():
    """Natija ekranida"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Qayta ishlash", callback_data="quiz:retry")],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_main")],
    ])
