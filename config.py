"""TestUpUz Bot — Konfiguratsiya"""

BOT_TOKEN = "8911175595:AAGnshXwB_CSY8x0ngi3OMFm-8EA3_rCoMU"

# Bot ma'lumotlari
BOT_NAME = "TestUp"
BOT_USERNAME = "@TestUpUzBot"
BOT_DESCRIPTION = """🎓 TestUp — Universal test platformasi

📚 Turli fanlar bo'yicha test ishlang
🧠 Bilimingizni sinang va kuzating
📊 Real-time natijalar va statistika
⚡ Telegram native quiz formati

🏆 Mavjud fanlar:
• Mobil Ilovalar Ishlab Chiqish (MIICH) — 365+ savol

Boshlash uchun /start ni bosing!"""

BOT_ABOUT = "🎓 Universal test platformasi — bilimingizni sinang va rivojlantiring!"

# Ma'lumotlar bazasi
DB_PATH = "data/testupuz.db"

# Baho tizimi
GRADES = {
    (90, 100): ("🏆 A'lo (5)", "alo"),
    (70, 89): ("📗 Yaxshi (4)", "yaxshi"),
    (60, 69): ("📙 Qoniqarli (3)", "qoniqarli"),
    (0, 59): ("📕 Qoniqarsiz (2)", "qoniqarsiz"),
}

def get_grade(percent: float) -> tuple:
    """Foiz bo'yicha baho qaytarish"""
    for (low, high), (label, key) in GRADES.items():
        if low <= percent <= high:
            return label, key
    return "📕 Qoniqarsiz (2)", "qoniqarsiz"
