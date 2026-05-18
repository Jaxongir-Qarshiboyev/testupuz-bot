"""SQLite ma'lumotlar bazasi"""
import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "testupuz.db")


async def init_db():
    """Ma'lumotlar bazasini yaratish"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject_id TEXT,
                topic_name TEXT,
                test_mode TEXT,
                question_order TEXT,
                time_limit INTEGER,
                total_questions INTEGER,
                correct_answers INTEGER,
                wrong_answers INTEGER,
                skipped INTEGER,
                score_percent REAL,
                grade TEXT,
                duration_seconds INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject_id TEXT,
                question_id INTEGER,
                is_correct BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def save_user(user_id: int, username: str, full_name: str):
    """Foydalanuvchini saqlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        await db.commit()


async def save_test_result(user_id: int, subject_id: str, topic_name: str,
                           test_mode: str, question_order: str, time_limit: int,
                           total: int, correct: int, wrong: int, skipped: int,
                           score: float, grade: str, duration: int):
    """Test natijasini saqlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO test_results 
            (user_id, subject_id, topic_name, test_mode, question_order, 
             time_limit, total_questions, correct_answers, wrong_answers, 
             skipped, score_percent, grade, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, subject_id, topic_name, test_mode, question_order,
              time_limit, total, correct, wrong, skipped, score, grade, duration))
        await db.commit()


async def save_answer(user_id: int, subject_id: str, question_id: int, is_correct: bool):
    """Javobni saqlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO user_answers (user_id, subject_id, question_id, is_correct) VALUES (?, ?, ?, ?)",
            (user_id, subject_id, question_id, is_correct)
        )
        await db.commit()


async def get_user_stats(user_id: int):
    """Foydalanuvchi statistikasi"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Umumiy statistika
        row = await db.execute_fetchall("""
            SELECT COUNT(*) as total_tests,
                   COALESCE(SUM(correct_answers), 0) as total_correct,
                   COALESCE(SUM(total_questions), 0) as total_questions,
                   COALESCE(AVG(score_percent), 0) as avg_score,
                   COALESCE(MAX(score_percent), 0) as best_score
            FROM test_results WHERE user_id = ?
        """, (user_id,))
        general = dict(row[0]) if row else {}

        # Mavzular bo'yicha
        topics = await db.execute_fetchall("""
            SELECT topic_name,
                   COUNT(*) as attempts,
                   COALESCE(AVG(score_percent), 0) as avg_score,
                   COALESCE(SUM(correct_answers), 0) as correct,
                   COALESCE(SUM(total_questions), 0) as total
            FROM test_results 
            WHERE user_id = ? AND subject_id = 'miich'
            GROUP BY topic_name
            ORDER BY topic_name
        """, (user_id,))
        topic_stats = [dict(t) for t in topics]

        return general, topic_stats


async def get_user_created_at(user_id: int):
    """Foydalanuvchi ro'yxatdan o'tgan sana"""
    async with aiosqlite.connect(DB_PATH) as db:
        row = await db.execute_fetchall(
            "SELECT created_at FROM users WHERE user_id = ?", (user_id,)
        )
        return row[0][0] if row else None
