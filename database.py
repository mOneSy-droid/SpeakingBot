import asyncio
from datetime import datetime, timezone
import psycopg2

from config import DB_URL, PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_id BIGINT PRIMARY KEY,
    username TEXT,
    joined_at TEXT NOT NULL,
    daily_reminder_time TEXT DEFAULT '08:00',
    last_practice_date TEXT,
    timezone TEXT DEFAULT 'UTC'
);

CREATE TABLE IF NOT EXISTS learned_words (
    telegram_id BIGINT NOT NULL,
    word TEXT NOT NULL,
    learned_at TEXT NOT NULL,
    next_review TEXT,
    review_count INTEGER DEFAULT 0,
    PRIMARY KEY (telegram_id, word)
);

CREATE TABLE IF NOT EXISTS practice_log (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    type TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS voice_recordings (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
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
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    week_start TEXT NOT NULL,
    week_end TEXT NOT NULL,
    total_sessions INTEGER DEFAULT 0,
    words_learned INTEGER DEFAULT 0,
    improvement_score REAL DEFAULT 0.0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS speech_exports (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    file_type TEXT DEFAULT 'pdf',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mock_meeting_sessions (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    questions_count INTEGER DEFAULT 5,
    responses TEXT,
    overall_score REAL DEFAULT 0.0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reminder_logs (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    reminded_at TEXT NOT NULL
);
"""


def _get_connection():
    if DB_URL:
        return psycopg2.connect(DB_URL)
    return psycopg2.connect(
        host=PGHOST,
        port=PGPORT,
        dbname=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD,
    )


async def _run_query(query: str, params: tuple = (), fetch: str | None = None):
    def _execute():
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if fetch == "one":
                    return cur.fetchone()
                if fetch == "all":
                    return cur.fetchall()
                conn.commit()
                return None
        finally:
            conn.close()

    return await asyncio.to_thread(_execute)


async def init_db():
    def _setup():
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(SCHEMA)
            conn.commit()
        finally:
            conn.close()

    await asyncio.to_thread(_setup)


async def ensure_user(telegram_id: int, username: str | None):
    now = datetime.now(timezone.utc).isoformat()
    await _run_query(
        """
        INSERT INTO users (telegram_id, username, joined_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (telegram_id) DO NOTHING
        """,
        (telegram_id, username, now),
    )


async def get_joined_at(telegram_id: int) -> datetime:
    row = await _run_query(
        "SELECT joined_at FROM users WHERE telegram_id = %s",
        (telegram_id,),
        fetch="one",
    )
    return datetime.fromisoformat(row[0]) if row and row[0] else datetime.now(timezone.utc)


async def mark_word_learned(telegram_id: int, word: str):
    await _run_query(
        """
        INSERT INTO learned_words (telegram_id, word, learned_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (telegram_id, word) DO NOTHING
        """,
        (telegram_id, word, datetime.now(timezone.utc).isoformat()),
    )


async def get_learned_words(telegram_id: int) -> set[str]:
    rows = await _run_query(
        "SELECT word FROM learned_words WHERE telegram_id = %s",
        (telegram_id,),
        fetch="all",
    )
    return {r[0] for r in rows or []}


async def log_practice(telegram_id: int, practice_type: str):
    await _run_query(
        "INSERT INTO practice_log (telegram_id, type, created_at) VALUES (%s, %s, %s)",
        (telegram_id, practice_type, datetime.now(timezone.utc).isoformat()),
    )


async def get_progress_stats(telegram_id: int) -> dict:
    words_row = await _run_query(
        "SELECT COUNT(*) FROM learned_words WHERE telegram_id = %s",
        (telegram_id,),
        fetch="one",
    )
    words_learned = words_row[0] if words_row else 0

    practice_rows = await _run_query(
        "SELECT type, COUNT(*) FROM practice_log WHERE telegram_id = %s GROUP BY type",
        (telegram_id,),
        fetch="all",
    )
    practice_counts = {row[0]: row[1] for row in practice_rows or []}

    return {
        "words_learned": words_learned,
        "structure_practice": practice_counts.get("structure", 0),
        "speech_reviews": practice_counts.get("speech", 0),
        "qa_practice": practice_counts.get("qa", 0),
        "speaking_practice": practice_counts.get("speaking", 0),
    }


async def set_next_review(telegram_id: int, word: str, days: int = 3):
    """Set next review date for a learned word (spaced repetition)"""
    from datetime import timedelta

    next_date = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    await _run_query(
        """
        UPDATE learned_words
        SET next_review = %s, review_count = review_count + 1
        WHERE telegram_id = %s AND word = %s
        """,
        (next_date, telegram_id, word),
    )


async def get_words_for_review(telegram_id: int) -> list[str]:
    """Get words that need review today (spaced repetition)"""
    now = datetime.now(timezone.utc).isoformat()
    rows = await _run_query(
        """
        SELECT word FROM learned_words
        WHERE telegram_id = %s AND (next_review IS NULL OR next_review <= %s)
        """,
        (telegram_id, now),
        fetch="all",
    )
    return [r[0] for r in rows or []]


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
    await _run_query(
        """
        INSERT INTO voice_recordings (
            telegram_id, question, transcript, file_path, wpm, filler_words, filler_list, feedback, recorded_at, quality_score
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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


async def get_voice_recordings(telegram_id: int, limit: int = 10) -> list[dict]:
    rows = await _run_query(
        """
        SELECT id, question, transcript, wpm, filler_words, filler_list, quality_score, recorded_at
        FROM voice_recordings WHERE telegram_id = %s ORDER BY recorded_at DESC LIMIT %s
        """,
        (telegram_id, limit),
        fetch="all",
    )
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
        for r in rows or []
    ]


async def create_weekly_report(
    telegram_id: int, week_start: str, week_end: str, total_sessions: int, words_learned: int, improvement_score: float
):
    await _run_query(
        """
        INSERT INTO weekly_reports (
            telegram_id, week_start, week_end, total_sessions, words_learned, improvement_score, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
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


async def get_weekly_report(telegram_id: int) -> dict | None:
    row = await _run_query(
        """
        SELECT total_sessions, words_learned, improvement_score
        FROM weekly_reports WHERE telegram_id = %s ORDER BY created_at DESC LIMIT 1
        """,
        (telegram_id,),
        fetch="one",
    )
    if row:
        return {
            "total_sessions": row[0],
            "words_learned": row[1],
            "improvement_score": row[2],
        }
    return None


async def save_speech_export(telegram_id: int, content: str, file_type: str = "pdf"):
    await _run_query(
        "INSERT INTO speech_exports (telegram_id, content, file_type, created_at) VALUES (%s, %s, %s, %s)",
        (telegram_id, content, file_type, datetime.now(timezone.utc).isoformat()),
    )


async def save_mock_meeting_session(telegram_id: int, questions_count: int, responses: str, overall_score: float):
    await _run_query(
        """
        INSERT INTO mock_meeting_sessions (
            telegram_id, questions_count, responses, overall_score, created_at
        ) VALUES (%s, %s, %s, %s, %s)
        """,
        (
            telegram_id,
            questions_count,
            responses,
            overall_score,
            datetime.now(timezone.utc).isoformat(),
        ),
    )


async def set_reminder_time(telegram_id: int, time_str: str):
    await _run_query(
        "UPDATE users SET daily_reminder_time = %s WHERE telegram_id = %s",
        (time_str, telegram_id),
    )


async def get_reminder_time(telegram_id: int) -> str:
    row = await _run_query(
        "SELECT daily_reminder_time FROM users WHERE telegram_id = %s",
        (telegram_id,),
        fetch="one",
    )
    return row[0] if row and row[0] else "08:00"


async def get_all_users_for_reminder() -> list[tuple]:
    rows = await _run_query("SELECT telegram_id, daily_reminder_time FROM users", fetch="all")
    return rows or []


async def set_last_practice_date(telegram_id: int, date: str):
    await _run_query(
        "UPDATE users SET last_practice_date = %s WHERE telegram_id = %s",
        (date, telegram_id),
    )


async def get_last_practice_date(telegram_id: int) -> str | None:
    row = await _run_query(
        "SELECT last_practice_date FROM users WHERE telegram_id = %s",
        (telegram_id,),
        fetch="one",
    )
    return row[0] if row and row[0] else None
