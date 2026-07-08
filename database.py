import aiosqlite
from datetime import datetime, timezone
from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    username TEXT,
    joined_at TEXT NOT NULL,
    daily_reminder_time TEXT DEFAULT '08:00',
    last_practice_date TEXT,
    timezone TEXT DEFAULT 'UTC'
);

CREATE TABLE IF NOT EXISTS learned_words (
    telegram_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    learned_at TEXT NOT NULL,
    next_review TEXT,
    review_count INTEGER DEFAULT 0,
    PRIMARY KEY (telegram_id, word)
);

CREATE TABLE IF NOT EXISTS practice_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    type TEXT NOT NULL,      -- 'structure' | 'speech' | 'qa' | 'mock_meeting' | 'timed'
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS voice_recordings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    transcript TEXT NOT NULL,
    file_path TEXT,
    wpm REAL,
    filler_words INTEGER DEFAULT 0,
    filler_list TEXT,
    feedback TEXT,
    recorded_at TEXT NOT NULL,
    quality_score INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS weekly_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    week_start TEXT NOT NULL,
    week_end TEXT NOT NULL,
    total_sessions INTEGER DEFAULT 0,
    words_learned INTEGER DEFAULT 0,
    improvement_score REAL DEFAULT 0.0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS speech_exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    file_type TEXT DEFAULT 'pdf',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mock_meeting_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    questions_count INTEGER DEFAULT 5,
    responses TEXT,
    overall_score REAL DEFAULT 0.0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reminder_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    reminded_at TEXT NOT NULL
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def ensure_user(telegram_id: int, username: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()
        if row is None:
            await db.execute(
                "INSERT INTO users (telegram_id, username, joined_at) VALUES (?, ?, ?)",
                (telegram_id, username, datetime.now(timezone.utc).isoformat()),
            )
            await db.commit()


async def get_joined_at(telegram_id: int) -> datetime:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT joined_at FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()
        return datetime.fromisoformat(row[0]) if row else datetime.now(timezone.utc)


async def mark_word_learned(telegram_id: int, word: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO learned_words (telegram_id, word, learned_at) VALUES (?, ?, ?)",
            (telegram_id, word, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()


async def get_learned_words(telegram_id: int) -> set[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT word FROM learned_words WHERE telegram_id = ?", (telegram_id,))
        rows = await cursor.fetchall()
        return {r[0] for r in rows}


async def log_practice(telegram_id: int, practice_type: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO practice_log (telegram_id, type, created_at) VALUES (?, ?, ?)",
            (telegram_id, practice_type, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()


async def get_progress_stats(telegram_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM learned_words WHERE telegram_id = ?", (telegram_id,)
        )
        words_learned = (await cursor.fetchone())[0]

        cursor = await db.execute(
            "SELECT type, COUNT(*) FROM practice_log WHERE telegram_id = ? GROUP BY type",
            (telegram_id,),
        )
        practice_counts = {row[0]: row[1] for row in await cursor.fetchall()}

    return {
        "words_learned": words_learned,
        "structure_practice": practice_counts.get("structure", 0),
        "speech_reviews": practice_counts.get("speech", 0),
        "qa_practice": practice_counts.get("qa", 0),
        "speaking_practice": practice_counts.get("speaking", 0),
    }


# ===== New functions for new features =====

# Spaced Repetition
async def set_next_review(telegram_id: int, word: str, days: int = 3):
    """Set next review date for a learned word (spaced repetition)"""
    from datetime import timedelta
    next_date = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE learned_words SET next_review = ?, review_count = review_count + 1 WHERE telegram_id = ? AND word = ?",
            (next_date, telegram_id, word),
        )
        await db.commit()


async def get_words_for_review(telegram_id: int) -> list[str]:
    """Get words that need review today (spaced repetition)"""
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT word FROM learned_words WHERE telegram_id = ? AND (next_review IS NULL OR next_review <= ?)",
            (telegram_id, now),
        )
        rows = await cursor.fetchall()
        return [r[0] for r in rows]


# Voice Recording & Filler Word Counter
async def save_voice_recording(
    telegram_id: int,
    question: str,
    transcript: str,
    file_path: str,
    wpm: float,
    filler_count: int,
    filler_list: str,
    feedback: str,
    quality_score: int = 0,
):
    """Save a voice recording with transcription and analysis"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO voice_recordings 
            (telegram_id, question, transcript, file_path, wpm, filler_words, filler_list, feedback, recorded_at, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                question,
                transcript,
                file_path,
                wpm,
                filler_count,
                filler_list,
                feedback,
                datetime.now(timezone.utc).isoformat(),
                quality_score,
            ),
        )
        await db.commit()


async def get_voice_recordings(telegram_id: int, limit: int = 10) -> list[dict]:
    """Get recent voice recordings for a user"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, question, transcript, wpm, filler_words, filler_list, quality_score, recorded_at
            FROM voice_recordings WHERE telegram_id = ? ORDER BY recorded_at DESC LIMIT ?
            """,
            (telegram_id, limit),
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": r[0],
                "question": r[1],
                "transcript": r[2],
                "wpm": r[3],
                "filler_count": r[4],
                "filler_list": r[5],
                "quality_score": r[6],
                "recorded_at": r[7],
            }
            for r in rows
        ]


# Weekly Report
async def create_weekly_report(
    telegram_id: int, week_start: str, week_end: str, total_sessions: int, words_learned: int, improvement_score: float
):
    """Create a weekly report"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO weekly_reports 
            (telegram_id, week_start, week_end, total_sessions, words_learned, improvement_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                week_start,
                week_end,
                total_sessions,
                words_learned,
                improvement_score,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await db.commit()


async def get_weekly_report(telegram_id: int) -> dict | None:
    """Get latest weekly report"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT total_sessions, words_learned, improvement_score 
            FROM weekly_reports WHERE telegram_id = ? ORDER BY created_at DESC LIMIT 1
            """,
            (telegram_id,),
        )
        row = await cursor.fetchone()
        if row:
            return {
                "total_sessions": row[0],
                "words_learned": row[1],
                "improvement_score": row[2],
            }
        return None


# Speech Export
async def save_speech_export(telegram_id: int, content: str, file_type: str = "pdf"):
    """Save exported speech"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO speech_exports (telegram_id, content, file_type, created_at) VALUES (?, ?, ?, ?)",
            (telegram_id, content, file_type, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()


# Mock Meeting Session
async def save_mock_meeting_session(telegram_id: int, questions_count: int, responses: str, overall_score: float):
    """Save a mock meeting session"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO mock_meeting_sessions 
            (telegram_id, questions_count, responses, overall_score, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                questions_count,
                responses,
                overall_score,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await db.commit()


# Reminder Settings
async def set_reminder_time(telegram_id: int, time_str: str):
    """Set daily reminder time (HH:MM format)"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET daily_reminder_time = ? WHERE telegram_id = ?",
            (time_str, telegram_id),
        )
        await db.commit()


async def get_reminder_time(telegram_id: int) -> str:
    """Get user's reminder time"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT daily_reminder_time FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()
        return row[0] if row else "08:00"


async def get_all_users_for_reminder() -> list[tuple]:
    """Get all users for daily reminder check"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT telegram_id, daily_reminder_time FROM users")
        return await cursor.fetchall()


async def set_last_practice_date(telegram_id: int, date: str):
    """Set last practice date"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET last_practice_date = ? WHERE telegram_id = ?",
            (date, telegram_id),
        )
        await db.commit()


async def get_last_practice_date(telegram_id: int) -> str | None:
    """Get last practice date"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT last_practice_date FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()
        return row[0] if row else None
