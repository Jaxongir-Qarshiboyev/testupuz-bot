# 🎓 TestUpUz Bot

<p align="center">
  <img src="assets/logo.png" alt="TestUp Logo" width="200">
</p>

<p align="center">
  <b>Universal test platformasi — Bilimingizni sinang va rivojlantiring!</b>
</p>

<p align="center">
  <a href="https://t.me/TestUpUzBot">
    <img src="https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram" alt="Telegram Bot">
  </a>
  <img src="https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/aiogram-3.x-blue?style=for-the-badge" alt="aiogram">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

---

## 📋 Loyiha haqida

**TestUpUz** — Telegram platformasida ishlaydigan universal test/quiz bot. Telegram native quiz formatidan foydalanib, foydalanuvchilarga turli fanlar bo'yicha bilimlarini sinash imkonini beradi.

### 🏆 Mavjud fanlar:
| Fan | Savollar | Mavzular |
|---|---|---|
| 📘 MIICH — Mobil Ilovalar Ishlab Chiqish | 365+ | 17 |

---

## ✨ Xususiyatlar

- 🧠 **Telegram Native Quiz** — Telegram'ning o'z quiz formati
- 📋 **Mavzu bo'yicha test** — 17 ta mavzudan tanlash
- 🔀 **Aralash test** — barcha mavzulardan random
- ⚙️ **Moslashuvchan sozlamalar:**
  - 📊 Savol soni: 10 / 25 / 50 / 100 / barchasi
  - 🔄 Tartib: Ketma-ket / Aralash
  - ⏱ Vaqt: Cheksiz / 15s / 30s / 60s / 120s
  - ⚠️ O'tkazish limiti: 3 / 5 / cheksiz
- 📊 **Statistika** — mavzular bo'yicha progress bar
- 🏆 **Baho tizimi** — A'lo / Yaxshi / Qoniqarli / Qoniqarsiz
- 💾 **SQLite** — barcha natijalar saqlanadi
- 🔄 **Universal arxitektura** — yangi fan qo'shish oson

---

## 🏗 Arxitektura

```
testupuz_bot/
├── bot.py              # Asosiy ishga tushirish
├── config.py           # Token va sozlamalar
├── data/
│   └── miich_quiz.json # 365 ta savol
├── database/
│   └── db.py           # SQLite (users, results, answers)
├── handlers/
│   ├── start.py        # /start, bosh menyu
│   ├── quiz_setup.py   # Sozlamalar
│   ├── quiz_play.py    # Test logikasi
│   └── stats.py        # Statistika
├── keyboards/
│   └── inline.py       # Inline keyboard'lar
├── states/
│   └── quiz_states.py  # FSM holatlari
├── utils/
│   └── quiz_data.py    # Quiz data loader
└── assets/
    ├── logo.png        # Bot logosi
    └── banner.png      # Description banner
```

---

## 🚀 O'rnatish

### 1. Repository'ni klonlash
```bash
git clone https://github.com/YOUR_USERNAME/testupuz-bot.git
cd testupuz-bot
```

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. Tokenni sozlash
`config.py` faylida `BOT_TOKEN` ni o'zgartiring.

### 4. Ishga tushirish
```bash
python bot.py
```

---

## 📊 Baho tizimi

| Foiz | Baho |
|---|---|
| 🏆 90-100% | A'lo (5) |
| 📗 70-89% | Yaxshi (4) |
| 📙 60-69% | Qoniqarli (3) |
| 📕 0-59% | Qoniqarsiz (2) |

---

## 🔧 Texnologiyalar

- **Python 3.10+**
- **aiogram 3.x** — async Telegram bot framework
- **aiosqlite** — async SQLite
- **Telegram Bot API** — native quiz polls

---

## 📄 Litsenziya

MIT License

---

<p align="center">
  <b>Yaratuvchi:</b> Jaxongir<br>
  <a href="https://t.me/TestUpUzBot">🤖 @TestUpUzBot</a>
</p>
