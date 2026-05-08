import json
from datetime import datetime
from urllib.parse import urlparse

import pymysql
import pymysql.cursors


def utc_now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class ChatDatabase:
    """MySQL storage via pymysql."""

    def __init__(self, database_url):
        self.database_url = database_url
        self.setup()

    def _get_connection(self):
        url = urlparse(self.database_url)
        return pymysql.connect(
            host=url.hostname,
            port=url.port or 3306,
            user=url.username,
            password=url.password,
            database=url.path.lstrip("/"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    def _run(self, sql, params=None, expect_rows=False):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if expect_rows:
                return cursor.fetchall()
            return cursor
        finally:
            conn.close()

    def _one(self, sql, params=None):
        rows = self._run(sql, params, expect_rows=True)
        return rows[0] if rows else None

    def _many(self, sql, params=None):
        return self._run(sql, params, expect_rows=True)

    def setup(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(255) PRIMARY KEY,
                    display_name VARCHAR(255) DEFAULT '',
                    personalized_prompt TEXT DEFAULT NULL,
                    caregiver_user_id VARCHAR(255) DEFAULT '',
                    consent_to_share INT DEFAULT 1,
                    config_json TEXT,
                    created_at VARCHAR(255) NOT NULL,
                    updated_at VARCHAR(255) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    session_mode VARCHAR(100) NOT NULL DEFAULT 'self_checkin',
                    started_at VARCHAR(255) NOT NULL,
                    ended_at VARCHAR(255),
                    state_json LONGTEXT,
                    short_conclusion TEXT DEFAULT NULL,
                    long_conclusion LONGTEXT DEFAULT NULL,
                    llm_summary_status VARCHAR(100) DEFAULT 'not_requested',
                    KEY idx_sessions_user (user_id, ended_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    role VARCHAR(100) NOT NULL,
                    message LONGTEXT NOT NULL,
                    raw_payload LONGTEXT,
                    created_at VARCHAR(255) NOT NULL,
                    KEY idx_chat_session (session_id, created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS observations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    group_id VARCHAR(255) DEFAULT '',
                    risk_level VARCHAR(100) DEFAULT '',
                    observation_json LONGTEXT,
                    created_at VARCHAR(255) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    caregiver_user_id VARCHAR(255) NOT NULL,
                    risk_level VARCHAR(100) NOT NULL,
                    group_id VARCHAR(255) DEFAULT '',
                    message LONGTEXT NOT NULL,
                    delivered INT DEFAULT 0,
                    blocked_reason TEXT DEFAULT NULL,
                    created_at VARCHAR(255) NOT NULL,
                    KEY idx_alerts_user (user_id, created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_calls (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id INT,
                    user_id VARCHAR(255) DEFAULT '',
                    provider VARCHAR(255) NOT NULL,
                    model VARCHAR(255) NOT NULL,
                    purpose VARCHAR(255) NOT NULL,
                    prompt_tokens INT DEFAULT 0,
                    completion_tokens INT DEFAULT 0,
                    total_tokens INT DEFAULT 0,
                    request_excerpt TEXT DEFAULT NULL,
                    response_excerpt TEXT DEFAULT NULL,
                    error TEXT DEFAULT NULL,
                    created_at VARCHAR(255) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
        finally:
            conn.close()

    def get_or_create_user(self, user_id):
        row = self._one("SELECT * FROM users WHERE user_id = %s", (user_id,))
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
            ) VALUES (%s, %s, %s, 1, %s, %s, %s)
            """,
            (user_id, user_id, "CAREGIVER_DEMO", json.dumps(config, ensure_ascii=False), now, now),
        )
        return self._one("SELECT * FROM users WHERE user_id = %s", (user_id,))

    def update_user(self, user_id, display_name, caregiver_user_id, consent_to_share, personalized_prompt, config_json):
        self.get_or_create_user(user_id)
        now = utc_now()
        self._run(
            """
            UPDATE users
            SET display_name = %s,
                caregiver_user_id = %s,
                consent_to_share = %s,
                personalized_prompt = %s,
                config_json = %s,
                updated_at = %s
            WHERE user_id = %s
            """,
            (
                display_name or user_id,
                caregiver_user_id or "",
                1 if consent_to_share else 0,
                personalized_prompt or "",
                json.dumps(config_json or {}, ensure_ascii=False),
                now,
                user_id,
            ),
        )
        return self.get_or_create_user(user_id)

    def get_active_session(self, user_id):
        return self._one(
            """
            SELECT * FROM sessions
            WHERE user_id = %s AND ended_at IS NULL
            ORDER BY session_id DESC
            LIMIT 1
            """,
            (user_id,),
        )

    def get_session(self, session_id):
        return self._one("SELECT * FROM sessions WHERE session_id = %s", (int(session_id),))

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
        cursor = self._run(
            """
            INSERT INTO sessions (user_id, session_mode, started_at, state_json)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, session_mode, now, json.dumps(state, ensure_ascii=False)),
        )
        session_id = cursor.lastrowid
        return self._one("SELECT * FROM sessions WHERE session_id = %s", (int(session_id),))

    def get_or_start_session(self, user_id, session_mode="self_checkin"):
        session = self.get_active_session(user_id)
        return session or self.start_session(user_id, session_mode)

    def update_session_state(self, session_id, state):
        self._run(
            "UPDATE sessions SET state_json = %s WHERE session_id = %s",
            (json.dumps(state, ensure_ascii=False), int(session_id)),
        )

    def close_session(self, session_id, short_conclusion, long_conclusion="", llm_summary_status="not_requested"):
        self._run(
            """
            UPDATE sessions
            SET ended_at = %s,
                short_conclusion = %s,
                long_conclusion = %s,
                llm_summary_status = %s
            WHERE session_id = %s
            """,
            (utc_now(), short_conclusion, long_conclusion, llm_summary_status, int(session_id)),
        )

    def append_chat(self, session_id, user_id, role, message, raw_payload=None):
        self._run(
            """
            INSERT INTO chat_logs (session_id, user_id, role, message, raw_payload, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                int(session_id),
                user_id,
                role,
                message,
                json.dumps(raw_payload or {}, ensure_ascii=False),
                utc_now(),
            ),
        )

    def recent_chat(self, session_id, limit=20):
        rows = self._many(
            """
            SELECT role, message, created_at FROM chat_logs
            WHERE session_id = %s
            ORDER BY id DESC
            LIMIT %s
            """,
            (int(session_id), int(limit)),
        )
        return list(reversed(rows))

    def previous_summaries(self, user_id, limit=6):
        return self._many(
            """
            SELECT session_id, started_at, ended_at, short_conclusion, long_conclusion
            FROM sessions
            WHERE user_id = %s AND ended_at IS NOT NULL
            ORDER BY session_id DESC
            LIMIT %s
            """,
            (user_id, int(limit)),
        )

    def raw_chatlog(self, session_id):
        return self._many(
            """
            SELECT role, message, raw_payload, created_at FROM chat_logs
            WHERE session_id = %s
            ORDER BY id ASC
            """,
            (int(session_id),),
        )

    def record_observation(self, session_id, user_id, group_id, risk_level, observation):
        self._run(
            """
            INSERT INTO observations (session_id, user_id, group_id, risk_level, observation_json, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                int(session_id),
                user_id,
                group_id or "",
                risk_level or "",
                json.dumps(observation or {}, ensure_ascii=False),
                utc_now(),
            ),
        )

    def record_alert(self, session_id, user_id, caregiver_user_id, risk_level, group_id, message, delivered, blocked_reason=""):
        self._run(
            """
            INSERT INTO alerts (
                session_id, user_id, caregiver_user_id, risk_level, group_id,
                message, delivered, blocked_reason, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                int(session_id),
                user_id,
                caregiver_user_id or "",
                risk_level,
                group_id or "",
                message,
                1 if delivered else 0,
                blocked_reason or "",
                utc_now(),
            ),
        )

    def record_llm_call(self, session_id, user_id, provider, model, purpose, usage, request_excerpt, response_excerpt, error=""):
        sid = None if session_id is None else int(session_id)
        self._run(
            """
            INSERT INTO llm_calls (
                session_id, user_id, provider, model, purpose,
                prompt_tokens, completion_tokens, total_tokens,
                request_excerpt, response_excerpt, error, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                sid,
                user_id or "",
                provider,
                model,
                purpose,
                int(usage.get("prompt_tokens", 0)),
                int(usage.get("completion_tokens", 0)),
                int(usage.get("total_tokens", 0)),
                (request_excerpt or "")[:2000],
                (response_excerpt or "")[:2000],
                (error or "")[:1000],
                utc_now(),
            ),
        )

    def alerts_for_user(self, user_id, limit=20):
        return self._many(
            """
            SELECT * FROM alerts
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT %s
            """,
            (user_id, int(limit)),
        )

    def llm_stats(self, session_id=None):
        if session_id:
            row = self._one(
                "SELECT COUNT(*) AS calls, COALESCE(SUM(total_tokens), 0) AS tokens FROM llm_calls WHERE session_id = %s",
                (int(session_id),),
            )
        else:
            row = self._one(
                "SELECT COUNT(*) AS calls, COALESCE(SUM(total_tokens), 0) AS tokens FROM llm_calls"
            )
        return row or {"calls": 0, "tokens": 0}

    def report_snapshot(self, user_ids=None, group_id=None, limit=12):
        user_ids = [str(user_id).strip() for user_id in (user_ids or []) if str(user_id or "").strip()]
        group_id = str(group_id or "").strip()
        matched_user_ids = list(dict.fromkeys(user_ids + self._user_ids_for_group_payload(group_id)))

        if matched_user_ids:
            placeholders = ", ".join("%s" for _ in matched_user_ids)
            where = "user_id IN ({0})".format(placeholders)
            params = tuple(matched_user_ids)
        elif group_id:
            where = "0=1"
            params = ()
        else:
            where = "1=1"
            params = ()

        sessions = self._many(
            """
            SELECT session_id, user_id, session_mode, started_at, ended_at, state_json, short_conclusion
            FROM sessions
            WHERE {where}
            ORDER BY session_id DESC
            LIMIT %s
            """.format(where=where),
            params + (int(limit),),
        )
        observations = self._many(
            """
            SELECT id, session_id, user_id, group_id, risk_level, observation_json, created_at
            FROM observations
            WHERE {where}
            ORDER BY id DESC
            LIMIT %s
            """.format(where=where),
            params + (int(limit),),
        )
        alerts = self._many(
            """
            SELECT id, session_id, user_id, caregiver_user_id, risk_level, group_id, message, delivered, blocked_reason, created_at
            FROM alerts
            WHERE {where}
            ORDER BY id DESC
            LIMIT %s
            """.format(where=where),
            params + (int(limit),),
        )
        messages = self._many(
            """
            SELECT id, session_id, user_id, role, message, created_at
            FROM chat_logs
            WHERE {where}
            ORDER BY id DESC
            LIMIT %s
            """.format(where=where),
            params + (int(limit),),
        )
        risk_counts = self._many(
            """
            SELECT COALESCE(NULLIF(risk_level, ''), 'unknown') AS risk_level, COUNT(*) AS count
            FROM observations
            WHERE {where}
            GROUP BY COALESCE(NULLIF(risk_level, ''), 'unknown')
            ORDER BY count DESC
            """.format(where=where),
            params,
        )

        counts_sql = """
            SELECT
                (SELECT COUNT(*) FROM users WHERE {where}) AS users,
                (SELECT COUNT(*) FROM sessions WHERE {where}) AS sessions,
                (SELECT COUNT(*) FROM sessions WHERE {where} AND ended_at IS NULL) AS active_sessions,
                (SELECT COUNT(*) FROM chat_logs WHERE {where}) AS messages,
                (SELECT COUNT(*) FROM observations WHERE {where}) AS observations,
                (SELECT COUNT(*) FROM alerts WHERE {where}) AS alerts,
                (SELECT COUNT(*) FROM alerts WHERE {where} AND risk_level = 'red') AS red_alerts,
                (SELECT COUNT(*) FROM alerts WHERE {where} AND risk_level = 'yellow') AS yellow_alerts
        """.format(where=where)
        all_params = params * 8
        counts = self._one(counts_sql, all_params) or {}

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
            WHERE raw_payload LIKE %s
            ORDER BY user_id
            """,
            ("%" + group_id + "%",),
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
