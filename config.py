import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

DB_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL") or os.getenv("POSTGRES_URL")
PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = int(os.getenv("PGPORT", "5432"))
PGDATABASE = os.getenv("PGDATABASE", "speech_bot")
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD", "postgres")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi. .env faylini tekshiring.")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY topilmadi. .env faylini tekshiring.")
