import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app.env import load_dotenv
from app.db import ChatDatabase
from app.ems_loader import EmsCorpus
from app.engine import ChatEngine
from app.gemini_client import GeminiClient


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
DATA = ROOT / "data"

load_dotenv(ROOT / ".env")

db = ChatDatabase(os.environ.get("CHATBOT_DB", str(DATA / "chatbot.sqlite3")))
corpus = EmsCorpus(ROOT / "Symptoms")
gemini = GeminiClient()
engine = ChatEngine(db, corpus, gemini)


class Handler(BaseHTTPRequestHandler):
    server_version = "EMSCheckinDemo/0.1"

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            return self._send_file(WEB / "index.html")
        if path.startswith("/web/"):
            rel = path.replace("/web/", "", 1)
            return self._send_file(WEB / rel)
        if path == "/api/bootstrap":
            qs = parse_qs(parsed.query)
            user_id = (qs.get("user_id") or ["U_DEMO"])[0]
            user = db.get_or_create_user(user_id)
            session = db.get_or_start_session(user_id)
            return self._json(
                {
                    "user": self._decode_user(user),
                    "session": self._decode_session(session),
                    "alerts": db.alerts_for_user(user_id),
                    "gemini": gemini.status(),
                    "groups_loaded": len(corpus.groups),
                }
            )
        if path == "/api/memory":
            qs = parse_qs(parsed.query)
            user_id = (qs.get("user_id") or ["U_DEMO"])[0]
            session = db.get_or_start_session(user_id)
            return self._json(
                {
                    "previous_sessions": db.previous_summaries(user_id, limit=10),
                    "recent_chat": db.recent_chat(session["session_id"], limit=30),
                    "alerts": db.alerts_for_user(user_id, limit=20),
                    "llm_stats": db.llm_stats(session["session_id"]),
                }
            )
        if path == "/api/health":
            return self._json(
                {
                    "ok": True,
                    "db": str(db.db_path),
                    "gemini_enabled": gemini.enabled,
                    "gemini_model": gemini.model,
                    "gemini_status": gemini.status(),
                    "groups_loaded": len(corpus.groups),
                }
            )
        return self._not_found()

    def do_POST(self):
        parsed = urlparse(self.path)
        payload = self._read_json()
        if parsed.path == "/api/users":
            user_id = payload.get("user_id") or "U_DEMO"
            config = payload.get("config") or {"daily_summary": True, "line_simulation": True}
            user = db.update_user(
                user_id=user_id,
                display_name=payload.get("display_name") or user_id,
                caregiver_user_id=payload.get("caregiver_user_id") or "",
                consent_to_share=bool(payload.get("consent_to_share", True)),
                personalized_prompt=payload.get("personalized_prompt") or "",
                config_json=config,
            )
            return self._json({"user": self._decode_user(user)})
        if parsed.path == "/api/chat":
            user_id = payload.get("user_id") or "U_DEMO"
            text = payload.get("text") or ""
            result = engine.handle_message(
                user_id=user_id,
                text=text,
                session_mode=payload.get("session_mode") or "self_checkin",
                user_can_chat=bool(payload.get("user_can_chat", True)),
                raw_payload={"channel": "web", "payload": payload},
            )
            return self._json(result)
        if parsed.path == "/api/line/webhook":
            return self._line_webhook(payload)
        if parsed.path == "/api/reset":
            user_id = payload.get("user_id") or "U_DEMO"
            result = engine.handle_message(user_id, "/reset", raw_payload={"channel": "web"})
            return self._json(result)
        return self._not_found()

    def _line_webhook(self, payload):
        results = []
        events = payload.get("events") or []
        for event in events:
            source = event.get("source") or {}
            message = event.get("message") or {}
            user_id = source.get("userId") or payload.get("user_id") or "U_LINE_DEMO"
            text = message.get("text") or ""
            results.append(
                engine.handle_message(
                    user_id=user_id,
                    text=text,
                    session_mode=payload.get("session_mode") or "self_checkin",
                    user_can_chat=bool(payload.get("user_can_chat", True)),
                    raw_payload={"channel": "line_webhook_sim", "payload": event},
                )
            )
        return self._json({"results": results, "event_count": len(events)})

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def _json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path):
        path = Path(path)
        if not path.exists() or not path.is_file():
            return self._not_found()
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type + ("; charset=utf-8" if content_type.startswith("text/") else ""))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _not_found(self):
        return self._json({"error": "not found"}, status=404)

    def _decode_user(self, user):
        data = dict(user)
        try:
            data["config_json"] = json.loads(data.get("config_json") or "{}")
        except Exception:
            data["config_json"] = {}
        data["consent_to_share"] = bool(data.get("consent_to_share"))
        return data

    def _decode_session(self, session):
        data = dict(session)
        try:
            data["state_json"] = json.loads(data.get("state_json") or "{}")
        except Exception:
            data["state_json"] = {}
        return data

    def log_message(self, fmt, *args):
        print("[http] " + fmt % args)


def run():
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "127.0.0.1")
    server = ThreadingHTTPServer((host, port), Handler)
    print("EMS check-in demo running at http://{0}:{1}".format(host, port))
    print("SQLite DB:", db.db_path)
    print("Gemini:", "enabled" if gemini.enabled else "disabled", gemini.model)
    print("Loaded EMS groups:", len(corpus.groups))
    server.serve_forever()


if __name__ == "__main__":
    run()
