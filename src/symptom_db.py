import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def utc_now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def sql_quote(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


class ChatDatabase:
    """SQLite storage via sqlite3 CLI.

    The local Python/conda sqlite3 module in this environment crashes on
    sqlite3.connect(), so this adapter keeps the required SQLite backend while
    avoiding the broken Python binding.
    """

    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.sqlite_bin = shutil.which("sqlite3")
        if not self.sqlite_bin:
            raise RuntimeError("sqlite3 CLI was not found in PATH")
        self.setup()

    def _run(self, script, expect_json=False):
        if expect_json:
            script = ".mode json\n.headers on\n" + script
        proc = subprocess.run(
            [self.sqlite_bin, str(self.db_path)],
            input=script,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
        if not expect_json:
            return []
        out = proc.stdout.strip()
        if not out:
            return []
        return json.loads(out)

    def setup(self):
        self._run(
            """
            CREATE TABLE IF NOT EXISTS users (
              user_id TEXT PRIMARY KEY,
              display_name TEXT DEFAULT '',
              personalized_prompt TEXT DEFAULT '',
              caregiver_user_id TEXT DEFAULT '',
              consent_to_share INTEGER DEFAULT 1,
              config_json TEXT DEFAULT '{}',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
              session_id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id TEXT NOT NULL,
              session_mode TEXT NOT NULL DEFAULT 'self_checkin',
              started_at TEXT NOT NULL,
              ended_at TEXT,
              state_json TEXT DEFAULT '{}',
              short_conclusion TEXT DEFAULT '',
              long_conclusion TEXT DEFAULT '',
              llm_summary_status TEXT DEFAULT 'not_requested'
            );

            CREATE TABLE IF NOT EXISTS chat_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id INTEGER NOT NULL,
              user_id TEXT NOT NULL,
              role TEXT NOT NULL,
              message TEXT NOT NULL,
              raw_payload TEXT DEFAULT '{}',
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS observations (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id INTEGER NOT NULL,
              user_id TEXT NOT NULL,
              group_id TEXT DEFAULT '',
              risk_level TEXT DEFAULT '',
              observation_json TEXT DEFAULT '{}',
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS alerts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id INTEGER NOT NULL,
              user_id TEXT NOT NULL,
              caregiver_user_id TEXT NOT NULL,
              risk_level TEXT NOT NULL,
              group_id TEXT DEFAULT '',
              message TEXT NOT NULL,
              delivered INTEGER DEFAULT 0,
              blocked_reason TEXT DEFAULT '',
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS llm_calls (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id INTEGER,
              user_id TEXT DEFAULT '',
              provider TEXT NOT NULL,
              model TEXT NOT NULL,
              purpose TEXT NOT NULL,
              prompt_tokens INTEGER DEFAULT 0,
              completion_tokens INTEGER DEFAULT 0,
              total_tokens INTEGER DEFAULT 0,
              request_excerpt TEXT DEFAULT '',
              response_excerpt TEXT DEFAULT '',
              error TEXT DEFAULT '',
              created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id, ended_at);
            CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_logs(session_id, created_at);
            CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id, created_at);
            """
        )

    def _one(self, sql):
        rows = self._run(sql, expect_json=True)
        return rows[0] if rows else None

    def _many(self, sql):
        return self._run(sql, expect_json=True)

    def get_or_create_user(self, user_id):
        row = self._one("SELECT * FROM users WHERE user_id = {0};".format(sql_quote(user_id)))
        if row:
            return row
        now = utc_now()
        config = {
            "daily_summary": True,
            "line_simulation": True,
            "llm_retrieval_assist": False,
            "llm_first": True,
            "llm_group_selection": False,
            "llm_session_summary": False,
        }
        self._run(
            """
            INSERT INTO users (
              user_id, display_name, caregiver_user_id, consent_to_share,
              config_json, created_at, updated_at
            ) VALUES ({user_id}, {display_name}, {caregiver}, 1, {config}, {now}, {now});
            """.format(
                user_id=sql_quote(user_id),
                display_name=sql_quote(user_id),
                caregiver=sql_quote("CAREGIVER_DEMO"),
                config=sql_quote(json.dumps(config, ensure_ascii=False)),
                now=sql_quote(now),
            )
        )
        return self._one("SELECT * FROM users WHERE user_id = {0};".format(sql_quote(user_id)))

    def update_user(self, user_id, display_name, caregiver_user_id, consent_to_share, personalized_prompt, config_json):
        self.get_or_create_user(user_id)
        now = utc_now()
        self._run(
            """
            UPDATE users
            SET display_name = {display_name},
                caregiver_user_id = {caregiver},
                consent_to_share = {consent},
                personalized_prompt = {prompt},
                config_json = {config},
                updated_at = {now}
            WHERE user_id = {user_id};
            """.format(
                display_name=sql_quote(display_name or user_id),
                caregiver=sql_quote(caregiver_user_id or ""),
                consent=1 if consent_to_share else 0,
                prompt=sql_quote(personalized_prompt or ""),
                config=sql_quote(json.dumps(config_json or {}, ensure_ascii=False)),
                now=sql_quote(now),
                user_id=sql_quote(user_id),
            )
        )
        return self.get_or_create_user(user_id)

    def get_active_session(self, user_id):
        return self._one(
            """
            SELECT * FROM sessions
            WHERE user_id = {user_id} AND ended_at IS NULL
            ORDER BY session_id DESC
            LIMIT 1;
            """.format(user_id=sql_quote(user_id))
        )

    def get_session(self, session_id):
        return self._one("SELECT * FROM sessions WHERE session_id = {0};".format(int(session_id)))

    def start_session(self, user_id, session_mode="self_checkin"):
        now = utc_now()
        state = {
            "active_group_id": "",
            "active_group_ids": [],
            "risk_level": "insufficient",
            "asked_rule_ids": [],
            "pending_rule_id": "",
            "pending_question": "",
            "observations": [],
            "matched_rules": [],
            "red_bundle_done": False,
            "red_checked_rule_ids": [],
            "yellow_done": False,
            "yellow_answers": {},
            "yellow_current_rule_ids": [],
            "yellow_detail_questions": [],
            "yellow_details": {},
            "pending_detail_key": "",
            "flow_phase": "",
            "session_mode": session_mode,
            "user_can_chat": True,
        }
        rows = self._many(
            """
            INSERT INTO sessions (user_id, session_mode, started_at, state_json)
            VALUES ({user_id}, {mode}, {now}, {state});
            SELECT last_insert_rowid() AS session_id;
            """.format(
                user_id=sql_quote(user_id),
                mode=sql_quote(session_mode),
                now=sql_quote(now),
                state=sql_quote(json.dumps(state, ensure_ascii=False)),
            )
        )
        session_id = rows[-1]["session_id"]
        return self._one("SELECT * FROM sessions WHERE session_id = {0};".format(int(session_id)))

    def get_or_start_session(self, user_id, session_mode="self_checkin"):
        session = self.get_active_session(user_id)
        return session or self.start_session(user_id, session_mode)

    def update_session_state(self, session_id, state):
        self._run(
            "UPDATE sessions SET state_json = {state} WHERE session_id = {sid};".format(
                state=sql_quote(json.dumps(state, ensure_ascii=False)),
                sid=int(session_id),
            )
        )

    def close_session(self, session_id, short_conclusion, long_conclusion="", llm_summary_status="not_requested"):
        self._run(
            """
            UPDATE sessions
            SET ended_at = {ended_at},
                short_conclusion = {short},
                long_conclusion = {long},
                llm_summary_status = {status}
            WHERE session_id = {sid};
            """.format(
                ended_at=sql_quote(utc_now()),
                short=sql_quote(short_conclusion),
                long=sql_quote(long_conclusion),
                status=sql_quote(llm_summary_status),
                sid=int(session_id),
            )
        )

    def append_chat(self, session_id, user_id, role, message, raw_payload=None):
        self._run(
            """
            INSERT INTO chat_logs (session_id, user_id, role, message, raw_payload, created_at)
            VALUES ({sid}, {user_id}, {role}, {message}, {raw}, {now});
            """.format(
                sid=int(session_id),
                user_id=sql_quote(user_id),
                role=sql_quote(role),
                message=sql_quote(message),
                raw=sql_quote(json.dumps(raw_payload or {}, ensure_ascii=False)),
                now=sql_quote(utc_now()),
            )
        )

    def recent_chat(self, session_id, limit=20):
        rows = self._many(
            """
            SELECT role, message, created_at FROM chat_logs
            WHERE session_id = {sid}
            ORDER BY id DESC
            LIMIT {limit};
            """.format(sid=int(session_id), limit=int(limit))
        )
        return list(reversed(rows))

    def previous_summaries(self, user_id, limit=6):
        return self._many(
            """
            SELECT session_id, started_at, ended_at, short_conclusion, long_conclusion
            FROM sessions
            WHERE user_id = {user_id} AND ended_at IS NOT NULL
            ORDER BY session_id DESC
            LIMIT {limit};
            """.format(user_id=sql_quote(user_id), limit=int(limit))
        )

    def raw_chatlog(self, session_id):
        return self._many(
            """
            SELECT role, message, raw_payload, created_at FROM chat_logs
            WHERE session_id = {sid}
            ORDER BY id ASC;
            """.format(sid=int(session_id))
        )

    def record_observation(self, session_id, user_id, group_id, risk_level, observation):
        self._run(
            """
            INSERT INTO observations (session_id, user_id, group_id, risk_level, observation_json, created_at)
            VALUES ({sid}, {user_id}, {group_id}, {risk}, {obs}, {now});
            """.format(
                sid=int(session_id),
                user_id=sql_quote(user_id),
                group_id=sql_quote(group_id or ""),
                risk=sql_quote(risk_level or ""),
                obs=sql_quote(json.dumps(observation or {}, ensure_ascii=False)),
                now=sql_quote(utc_now()),
            )
        )

    def record_alert(self, session_id, user_id, caregiver_user_id, risk_level, group_id, message, delivered, blocked_reason=""):
        self._run(
            """
            INSERT INTO alerts (
              session_id, user_id, caregiver_user_id, risk_level, group_id,
              message, delivered, blocked_reason, created_at
            ) VALUES ({sid}, {user_id}, {caregiver}, {risk}, {group_id}, {message}, {delivered}, {blocked}, {now});
            """.format(
                sid=int(session_id),
                user_id=sql_quote(user_id),
                caregiver=sql_quote(caregiver_user_id or ""),
                risk=sql_quote(risk_level),
                group_id=sql_quote(group_id or ""),
                message=sql_quote(message),
                delivered=1 if delivered else 0,
                blocked=sql_quote(blocked_reason or ""),
                now=sql_quote(utc_now()),
            )
        )

    def record_llm_call(self, session_id, user_id, provider, model, purpose, usage, request_excerpt, response_excerpt, error=""):
        sid = "NULL" if session_id is None else str(int(session_id))
        self._run(
            """
            INSERT INTO llm_calls (
              session_id, user_id, provider, model, purpose,
              prompt_tokens, completion_tokens, total_tokens,
              request_excerpt, response_excerpt, error, created_at
            ) VALUES ({sid}, {user_id}, {provider}, {model}, {purpose}, {pt}, {ct}, {tt}, {req}, {res}, {err}, {now});
            """.format(
                sid=sid,
                user_id=sql_quote(user_id or ""),
                provider=sql_quote(provider),
                model=sql_quote(model),
                purpose=sql_quote(purpose),
                pt=int(usage.get("prompt_tokens", 0)),
                ct=int(usage.get("completion_tokens", 0)),
                tt=int(usage.get("total_tokens", 0)),
                req=sql_quote((request_excerpt or "")[:2000]),
                res=sql_quote((response_excerpt or "")[:2000]),
                err=sql_quote((error or "")[:1000]),
                now=sql_quote(utc_now()),
            )
        )

    def alerts_for_user(self, user_id, limit=20):
        return self._many(
            """
            SELECT * FROM alerts
            WHERE user_id = {user_id}
            ORDER BY id DESC
            LIMIT {limit};
            """.format(user_id=sql_quote(user_id), limit=int(limit))
        )

    def llm_stats(self, session_id=None):
        where = ""
        if session_id:
            where = " WHERE session_id = {0}".format(int(session_id))
        row = self._one(
            "SELECT COUNT(*) AS calls, COALESCE(SUM(total_tokens), 0) AS tokens FROM llm_calls{0};".format(
                where
            )
        )
        return row or {"calls": 0, "tokens": 0}

    def report_snapshot(self, user_ids=None, group_id=None, limit=12):
        user_ids = [str(user_id).strip() for user_id in (user_ids or []) if str(user_id or "").strip()]
        group_id = str(group_id or "").strip()
        matched_user_ids = list(dict.fromkeys(user_ids + self._user_ids_for_group_payload(group_id)))

        if matched_user_ids:
            where = "user_id IN ({0})".format(", ".join(sql_quote(user_id) for user_id in matched_user_ids))
        elif group_id:
            where = "0=1"
        else:
            where = "1=1"

        sessions = self._many(
            """
            SELECT session_id, user_id, session_mode, started_at, ended_at, state_json, short_conclusion
            FROM sessions
            WHERE {where}
            ORDER BY session_id DESC
            LIMIT {limit};
            """.format(where=where, limit=int(limit))
        )
        observations = self._many(
            """
            SELECT id, session_id, user_id, group_id, risk_level, observation_json, created_at
            FROM observations
            WHERE {where}
            ORDER BY id DESC
            LIMIT {limit};
            """.format(where=where, limit=int(limit))
        )
        alerts = self._many(
            """
            SELECT id, session_id, user_id, caregiver_user_id, risk_level, group_id, message, delivered, blocked_reason, created_at
            FROM alerts
            WHERE {where}
            ORDER BY id DESC
            LIMIT {limit};
            """.format(where=where, limit=int(limit))
        )
        messages = self._many(
            """
            SELECT id, session_id, user_id, role, message, created_at
            FROM chat_logs
            WHERE {where}
            ORDER BY id DESC
            LIMIT {limit};
            """.format(where=where, limit=int(limit))
        )
        risk_counts = self._many(
            """
            SELECT COALESCE(NULLIF(risk_level, ''), 'unknown') AS risk_level, COUNT(*) AS count
            FROM observations
            WHERE {where}
            GROUP BY COALESCE(NULLIF(risk_level, ''), 'unknown')
            ORDER BY count DESC;
            """.format(where=where)
        )
        counts = self._one(
            """
            SELECT
              (SELECT COUNT(*) FROM users WHERE {where}) AS users,
              (SELECT COUNT(*) FROM sessions WHERE {where}) AS sessions,
              (SELECT COUNT(*) FROM sessions WHERE {where} AND ended_at IS NULL) AS active_sessions,
              (SELECT COUNT(*) FROM chat_logs WHERE {where}) AS messages,
              (SELECT COUNT(*) FROM observations WHERE {where}) AS observations,
              (SELECT COUNT(*) FROM alerts WHERE {where}) AS alerts,
              (SELECT COUNT(*) FROM alerts WHERE {where} AND risk_level = 'red') AS red_alerts,
              (SELECT COUNT(*) FROM alerts WHERE {where} AND risk_level = 'yellow') AS yellow_alerts;
            """.format(where=where)
        ) or {}

        return {
            "summary": counts,
            "user_ids": matched_user_ids,
            "risk_counts": risk_counts,
            "sessions": [self._decode_session(row) for row in sessions],
            "observations": [self._decode_observation(row) for row in observations],
            "alerts": alerts,
            "messages": messages,
        }

    def _user_ids_for_group_payload(self, group_id):
        if not group_id:
            return []
        rows = self._many(
            """
            SELECT DISTINCT user_id
            FROM chat_logs
            WHERE raw_payload LIKE {pattern}
            ORDER BY user_id;
            """.format(pattern=sql_quote("%" + group_id + "%"))
        )
        return [row.get("user_id") for row in rows if row.get("user_id")]

    def _decode_session(self, row):
        session = dict(row)
        try:
            session["state"] = json.loads(session.pop("state_json") or "{}")
        except Exception:
            session["state"] = {}
        return session

    def _decode_observation(self, row):
        observation = dict(row)
        try:
            observation["observation"] = json.loads(observation.pop("observation_json") or "{}")
        except Exception:
            observation["observation"] = {}
        return observation
