from dotenv import load_dotenv
import time
import os

load_dotenv()


def _env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name, default):
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default

LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "").strip()
# print(LINE_ACCESS_TOKEN)
# print(LINE_CHANNEL_SECRET)

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "5000"))
DEBUG = _env_bool("DEBUG", True)
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join("data", "registrations.sqlite3"))
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join("static", "uploads"))

MEDICINE_ALERT_TIMEZONE = os.getenv("MEDICINE_ALERT_TIMEZONE", "Asia/Bangkok").strip()
MEDICINE_ALERT_LIVE_MODE = _env_bool("MEDICINE_ALERT_LIVE_MODE", True)
MEDICINE_ALERT_WINDOW_MINUTES = _env_int("MEDICINE_ALERT_WINDOW_MINUTES", 10)
MEDICINE_ALERT_POLL_SECONDS = _env_int("MEDICINE_ALERT_POLL_SECONDS", 60)
MEDICINE_ALERT_WORKER_ENABLED = _env_bool("MEDICINE_ALERT_WORKER_ENABLED", False)
MEDICINE_ALERT_MORNING_MEAL = os.getenv("MEDICINE_ALERT_MORNING_MEAL", "08:00").strip()
MEDICINE_ALERT_NOON_MEAL = os.getenv("MEDICINE_ALERT_NOON_MEAL", "12:00").strip()
MEDICINE_ALERT_EVENING_MEAL = os.getenv("MEDICINE_ALERT_EVENING_MEAL", "18:00").strip()
MEDICINE_ALERT_BEFORE_MEAL_MINUTES = _env_int("MEDICINE_ALERT_BEFORE_MEAL_MINUTES", 30)
MEDICINE_ALERT_AFTER_MEAL_MINUTES = _env_int("MEDICINE_ALERT_AFTER_MEAL_MINUTES", 30)
MEDICINE_ALERT_BEDTIME = os.getenv("MEDICINE_ALERT_BEDTIME", "21:00").strip()

APPOINTMENT_ALERT_TIMEZONE = os.getenv("APPOINTMENT_ALERT_TIMEZONE", MEDICINE_ALERT_TIMEZONE).strip()
APPOINTMENT_ALERT_LIVE_MODE = _env_bool("APPOINTMENT_ALERT_LIVE_MODE", MEDICINE_ALERT_LIVE_MODE)
APPOINTMENT_ALERT_WORKER_ENABLED = _env_bool("APPOINTMENT_ALERT_WORKER_ENABLED", MEDICINE_ALERT_WORKER_ENABLED)
APPOINTMENT_ALERT_POLL_SECONDS = _env_int("APPOINTMENT_ALERT_POLL_SECONDS", MEDICINE_ALERT_POLL_SECONDS)
APPOINTMENT_ALERT_WINDOW_MINUTES = _env_int("APPOINTMENT_ALERT_WINDOW_MINUTES", MEDICINE_ALERT_WINDOW_MINUTES)
APPOINTMENT_ALERT_LEAD_MINUTES = _env_int("APPOINTMENT_ALERT_LEAD_MINUTES", 1440)
