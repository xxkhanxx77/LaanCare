from dotenv import load_dotenv
import time
import os

load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "").strip()
# print(LINE_ACCESS_TOKEN)
# print(LINE_CHANNEL_SECRET)

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("DEBUG", True)
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join("data", "registrations.sqlite3"))
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join("static", "uploads"))
