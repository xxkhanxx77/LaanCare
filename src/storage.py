import json
import os
import sqlite3
from datetime import datetime, timezone

try:
    from .config import DATABASE_PATH
except ImportError:
    from config import DATABASE_PATH


def get_connection():
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                line_user_id TEXT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                gender TEXT NOT NULL,
                role TEXT NOT NULL,
                height_cm REAL,
                weight_kg REAL,
                created_at TEXT NOT NULL
            )
            """
        )
        ensure_column(connection, "registrations", "line_user_id", "TEXT")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                medicine_name TEXT NOT NULL,
                dosage TEXT,
                take_time TEXT,
                instruction TEXT,
                image_path TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ocr_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                detected_type TEXT,
                data_json TEXT,
                interpretation TEXT,
                interaction_report TEXT,
                image_path TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                hospital TEXT,
                department TEXT,
                doctor TEXT,
                appointment_date TEXT,
                appointment_time TEXT,
                appointment_datetime TEXT,
                preparation TEXT,
                reason TEXT,
                interpretation TEXT,
                image_path TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS carebot_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT,
                line_user_id TEXT,
                assessment_type TEXT NOT NULL,
                score INTEGER NOT NULL,
                responses_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS medicine_alert_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                medicine_id INTEGER NOT NULL,
                alert_key TEXT NOT NULL,
                alert_date TEXT NOT NULL,
                scheduled_for TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL,
                error TEXT,
                created_at TEXT NOT NULL,
                sent_at TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_medicine_alert_logs_once
            ON medicine_alert_logs(medicine_id, alert_key, alert_date, target_type, target_id)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_medicine_alert_logs_medicine
            ON medicine_alert_logs(medicine_id)
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS medicine_alert_action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_log_id INTEGER,
                group_id TEXT,
                medicine_id INTEGER,
                action TEXT NOT NULL,
                line_user_id TEXT,
                source_type TEXT,
                source_id TEXT,
                created_at TEXT NOT NULL,
                raw_payload TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_medicine_alert_action_logs_alert
            ON medicine_alert_action_logs(alert_log_id, created_at)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_medicine_alert_action_logs_medicine
            ON medicine_alert_action_logs(medicine_id)
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS appointment_alert_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                appointment_id INTEGER NOT NULL,
                alert_key TEXT NOT NULL,
                alert_date TEXT NOT NULL,
                scheduled_for TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL,
                error TEXT,
                created_at TEXT NOT NULL,
                sent_at TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_appointment_alert_logs_once
            ON appointment_alert_logs(appointment_id, alert_key, alert_date, target_type, target_id)
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS appointment_alert_action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_log_id INTEGER,
                group_id TEXT,
                appointment_id INTEGER,
                action TEXT NOT NULL,
                line_user_id TEXT,
                source_type TEXT,
                source_id TEXT,
                created_at TEXT NOT NULL,
                raw_payload TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_appointment_alert_action_logs_alert
            ON appointment_alert_action_logs(alert_log_id, created_at)
            """
        )
        cleanup_orphan_medicine_alert_records(connection)


def ensure_column(connection, table_name, column_name, column_type):
    columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    if column_name in {column["name"] for column in columns}:
        return

    connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def cleanup_orphan_medicine_alert_records(connection):
    connection.execute(
        """
        DELETE FROM medicine_alert_action_logs
        WHERE
            (
                medicine_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1
                    FROM medicines
                    WHERE medicines.id = medicine_alert_action_logs.medicine_id
                )
            )
            OR (
                alert_log_id IS NOT NULL
                AND EXISTS (
                    SELECT 1
                    FROM medicine_alert_logs
                    WHERE
                        medicine_alert_logs.id = medicine_alert_action_logs.alert_log_id
                        AND NOT EXISTS (
                            SELECT 1
                            FROM medicines
                            WHERE medicines.id = medicine_alert_logs.medicine_id
                        )
                )
            )
        """
    )
    connection.execute(
        """
        DELETE FROM medicine_alert_logs
        WHERE NOT EXISTS (
            SELECT 1
            FROM medicines
            WHERE medicines.id = medicine_alert_logs.medicine_id
        )
        """
    )
    connection.execute(
        """
        DELETE FROM medicine_alert_action_logs
        WHERE
            alert_log_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1
                FROM medicine_alert_logs
                WHERE medicine_alert_logs.id = medicine_alert_action_logs.alert_log_id
            )
        """
    )


def delete_medicine_alert_records(connection, medicine_ids):
    if not medicine_ids:
        return

    placeholders = ", ".join("?" for _ in medicine_ids)
    params = tuple(medicine_ids)
    connection.execute(
        f"""
        DELETE FROM medicine_alert_action_logs
        WHERE
            medicine_id IN ({placeholders})
            OR alert_log_id IN (
                SELECT id
                FROM medicine_alert_logs
                WHERE medicine_id IN ({placeholders})
            )
        """,
        params + params,
    )
    connection.execute(
        f"""
        DELETE FROM medicine_alert_logs
        WHERE medicine_id IN ({placeholders})
        """,
        params,
    )


def save_registration(data):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        existing_id = find_registration_id_by_line_user_id(connection, data.get("line_user_id"))
        if existing_id:
            connection.execute(
                """
                UPDATE registrations
                SET
                    group_id = ?,
                    line_user_id = ?,
                    first_name = ?,
                    last_name = ?,
                    email = ?,
                    phone = ?,
                    gender = ?,
                    role = ?,
                    height_cm = ?,
                    weight_kg = ?,
                    created_at = ?
                WHERE id = ?
                """,
                (
                    data["group_id"],
                    data.get("line_user_id"),
                    data["first_name"],
                    data["last_name"],
                    data["email"],
                    data["phone"],
                    data["gender"],
                    data["role"],
                    data.get("height_cm"),
                    data.get("weight_kg"),
                    created_at,
                    existing_id,
                ),
            )
            return existing_id

        cursor = connection.execute(
            """
            INSERT INTO registrations (
                group_id,
                line_user_id,
                first_name,
                last_name,
                email,
                phone,
                gender,
                role,
                height_cm,
                weight_kg,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["group_id"],
                data.get("line_user_id"),
                data["first_name"],
                data["last_name"],
                data["email"],
                data["phone"],
                data["gender"],
                data["role"],
                data.get("height_cm"),
                data.get("weight_kg"),
                created_at,
            ),
        )
        return cursor.lastrowid


def get_registration(registration_id):
    init_db()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM registrations
            WHERE id = ?
            """,
            (registration_id,),
        ).fetchone()

    return dict(row) if row else None


def get_registration_by_line_user_id(line_user_id):
    if not line_user_id:
        return None

    init_db()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM registrations
            WHERE line_user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (line_user_id,),
        ).fetchone()

    return dict(row) if row else None


def update_registration(registration_id, data):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        existing = connection.execute(
            """
            SELECT id
            FROM registrations
            WHERE id = ?
            """,
            (registration_id,),
        ).fetchone()
        if not existing:
            return None

        connection.execute(
            """
            UPDATE registrations
            SET
                group_id = ?,
                line_user_id = ?,
                first_name = ?,
                last_name = ?,
                email = ?,
                phone = ?,
                gender = ?,
                role = ?,
                height_cm = ?,
                weight_kg = ?,
                created_at = ?
            WHERE id = ?
            """,
            (
                data["group_id"],
                data.get("line_user_id"),
                data["first_name"],
                data["last_name"],
                data["email"],
                data["phone"],
                data["gender"],
                data["role"],
                data.get("height_cm"),
                data.get("weight_kg"),
                created_at,
                registration_id,
            ),
        )
        row = connection.execute(
            """
            SELECT *
            FROM registrations
            WHERE id = ?
            """,
            (registration_id,),
        ).fetchone()

    return dict(row) if row else None


def delete_registration(registration_id):
    init_db()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM registrations
            WHERE id = ?
            """,
            (registration_id,),
        )

    return cursor.rowcount > 0


def find_registration_id_by_line_user_id(connection, line_user_id):
    if not line_user_id:
        return None

    row = connection.execute(
        """
        SELECT id
        FROM registrations
        WHERE line_user_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT 1
        """,
        (line_user_id,),
    ).fetchone()

    return row["id"] if row else None


def list_registrations(group_id=None):
    init_db()

    with get_connection() as connection:
        if group_id:
            rows = connection.execute(
                """
                SELECT *
                FROM registrations
                WHERE group_id = ?
                ORDER BY created_at DESC
                """,
                (group_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM registrations
                ORDER BY created_at DESC
                """
            ).fetchall()

    return [dict(row) for row in rows]


def save_medicine_items(group_id, items):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()
    inserted_ids = []

    with get_connection() as connection:
        for item in items:
            cursor = connection.execute(
                """
                INSERT INTO medicines (
                    group_id,
                    medicine_name,
                    dosage,
                    take_time,
                    instruction,
                    image_path,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    group_id,
                    item["medicine_name"],
                    item.get("dosage"),
                    item.get("take_time"),
                    item.get("instruction"),
                    item.get("image_path"),
                    created_at,
                ),
            )
            inserted_ids.append(cursor.lastrowid)

    return inserted_ids


def save_medicine_item(group_id, item):
    return save_medicine_items(group_id, [item])[0]


def save_appointment_item(group_id, item):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO appointments (
                group_id,
                hospital,
                department,
                doctor,
                appointment_date,
                appointment_time,
                appointment_datetime,
                preparation,
                reason,
                interpretation,
                image_path,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                group_id,
                item.get("hospital"),
                item.get("department"),
                item.get("doctor"),
                item.get("appointment_date"),
                item.get("appointment_time"),
                item.get("appointment_datetime"),
                item.get("preparation"),
                item.get("reason"),
                item.get("interpretation"),
                item.get("image_path"),
                created_at,
            ),
        )

    return cursor.lastrowid


def list_appointments(group_id=None):
    init_db()

    with get_connection() as connection:
        if group_id:
            rows = connection.execute(
                """
                SELECT *
                FROM appointments
                WHERE group_id = ?
                ORDER BY appointment_datetime IS NULL, appointment_datetime ASC, created_at DESC, id DESC
                """,
                (group_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM appointments
                ORDER BY appointment_datetime IS NULL, appointment_datetime ASC, created_at DESC, id DESC
                """
            ).fetchall()

    return [dict(row) for row in rows]


def delete_appointment(appointment_id, group_id=None):
    init_db()

    with get_connection() as connection:
        if group_id:
            appointment = connection.execute(
                """
                SELECT id
                FROM appointments
                WHERE id = ? AND group_id = ?
                """,
                (appointment_id, group_id),
            ).fetchone()
        else:
            appointment = connection.execute(
                """
                SELECT id
                FROM appointments
                WHERE id = ?
                """,
                (appointment_id,),
            ).fetchone()

        if not appointment:
            return False

        connection.execute(
            """
            DELETE FROM appointment_alert_action_logs
            WHERE
                appointment_id = ?
                OR alert_log_id IN (
                    SELECT id
                    FROM appointment_alert_logs
                    WHERE appointment_id = ?
                )
            """,
            (appointment_id, appointment_id),
        )
        connection.execute(
            """
            DELETE FROM appointment_alert_logs
            WHERE appointment_id = ?
            """,
            (appointment_id,),
        )
        cursor = connection.execute(
            """
            DELETE FROM appointments
            WHERE id = ?
            """,
            (appointment_id,),
        )

    return cursor.rowcount > 0


def list_medicines(group_id=None):
    init_db()

    with get_connection() as connection:
        if group_id:
            rows = connection.execute(
                """
                SELECT *
                FROM medicines
                WHERE group_id = ?
                ORDER BY created_at DESC, id DESC
                """,
                (group_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM medicines
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()

    return [dict(row) for row in rows]


def delete_medicine(medicine_id, group_id=None):
    init_db()

    with get_connection() as connection:
        if group_id:
            medicine = connection.execute(
                """
                SELECT id
                FROM medicines
                WHERE id = ? AND group_id = ?
                """,
                (medicine_id, group_id),
            ).fetchone()
        else:
            medicine = connection.execute(
                """
                SELECT id
                FROM medicines
                WHERE id = ?
                """,
                (medicine_id,),
            ).fetchone()

        if not medicine:
            return False

        delete_medicine_alert_records(connection, [medicine_id])
        cursor = connection.execute(
            """
            DELETE FROM medicines
            WHERE id = ?
            """,
            (medicine_id,),
        )

    return cursor.rowcount > 0


def reserve_medicine_alert(alert):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        active_medicine = connection.execute(
            """
            SELECT id
            FROM medicines
            WHERE id = ? AND group_id = ?
            """,
            (alert["medicine_id"], alert["group_id"]),
        ).fetchone()
        if not active_medicine:
            return None

        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO medicine_alert_logs (
                group_id,
                medicine_id,
                alert_key,
                alert_date,
                scheduled_for,
                target_type,
                target_id,
                message,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                alert["group_id"],
                alert["medicine_id"],
                alert["alert_key"],
                alert["alert_date"],
                alert["scheduled_for"],
                alert.get("target_type", "group"),
                alert.get("target_id") or alert["group_id"],
                alert["message"],
                "pending",
                created_at,
            ),
        )

        if cursor.rowcount == 0:
            return None

        return cursor.lastrowid


def update_medicine_alert_log(alert_log_id, status, error=None):
    init_db()
    sent_at = datetime.now(timezone.utc).isoformat() if status == "sent" else None

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE medicine_alert_logs
            SET status = ?, error = ?, sent_at = ?
            WHERE id = ?
            """,
            (status, error, sent_at, alert_log_id),
        )


def list_medicine_alert_logs(group_id=None, limit=50):
    init_db()
    limit = max(1, min(int(limit or 50), 200))

    with get_connection() as connection:
        if group_id:
            rows = connection.execute(
                """
                SELECT medicine_alert_logs.*
                FROM medicine_alert_logs
                INNER JOIN medicines
                    ON medicines.id = medicine_alert_logs.medicine_id
                WHERE medicine_alert_logs.group_id = ?
                ORDER BY medicine_alert_logs.created_at DESC, medicine_alert_logs.id DESC
                LIMIT ?
                """,
                (group_id, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT medicine_alert_logs.*
                FROM medicine_alert_logs
                INNER JOIN medicines
                    ON medicines.id = medicine_alert_logs.medicine_id
                ORDER BY medicine_alert_logs.created_at DESC, medicine_alert_logs.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    return [dict(row) for row in rows]


def record_medicine_alert_action(data):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()
    raw_payload = data.get("raw_payload")
    if raw_payload is not None and not isinstance(raw_payload, str):
        raw_payload = json.dumps(raw_payload, ensure_ascii=False)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO medicine_alert_action_logs (
                alert_log_id,
                group_id,
                medicine_id,
                action,
                line_user_id,
                source_type,
                source_id,
                created_at,
                raw_payload
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("alert_log_id"),
                data.get("group_id"),
                data.get("medicine_id"),
                data["action"],
                data.get("line_user_id"),
                data.get("source_type"),
                data.get("source_id"),
                created_at,
                raw_payload,
            ),
        )

    return cursor.lastrowid


def list_medicine_alert_action_logs(group_id=None, limit=50):
    init_db()
    limit = max(1, min(int(limit or 50), 200))

    with get_connection() as connection:
        if group_id:
            rows = connection.execute(
                """
                SELECT *
                FROM medicine_alert_action_logs
                WHERE group_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (group_id, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM medicine_alert_action_logs
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    return [dict(row) for row in rows]


def reserve_appointment_alert(alert):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        active_appointment = connection.execute(
            """
            SELECT id
            FROM appointments
            WHERE id = ? AND group_id = ?
            """,
            (alert["appointment_id"], alert["group_id"]),
        ).fetchone()
        if not active_appointment:
            return None

        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO appointment_alert_logs (
                group_id,
                appointment_id,
                alert_key,
                alert_date,
                scheduled_for,
                target_type,
                target_id,
                message,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                alert["group_id"],
                alert["appointment_id"],
                alert["alert_key"],
                alert["alert_date"],
                alert["scheduled_for"],
                alert.get("target_type", "group"),
                alert.get("target_id") or alert["group_id"],
                alert["message"],
                "pending",
                created_at,
            ),
        )

        if cursor.rowcount == 0:
            return None

        return cursor.lastrowid


def update_appointment_alert_log(alert_log_id, status, error=None):
    init_db()
    sent_at = datetime.now(timezone.utc).isoformat() if status == "sent" else None

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE appointment_alert_logs
            SET status = ?, error = ?, sent_at = ?
            WHERE id = ?
            """,
            (status, error, sent_at, alert_log_id),
        )


def list_appointment_alert_logs(group_id=None, limit=50):
    init_db()
    limit = max(1, min(int(limit or 50), 200))

    with get_connection() as connection:
        if group_id:
            rows = connection.execute(
                """
                SELECT appointment_alert_logs.*
                FROM appointment_alert_logs
                INNER JOIN appointments
                    ON appointments.id = appointment_alert_logs.appointment_id
                WHERE appointment_alert_logs.group_id = ?
                ORDER BY appointment_alert_logs.created_at DESC, appointment_alert_logs.id DESC
                LIMIT ?
                """,
                (group_id, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT appointment_alert_logs.*
                FROM appointment_alert_logs
                INNER JOIN appointments
                    ON appointments.id = appointment_alert_logs.appointment_id
                ORDER BY appointment_alert_logs.created_at DESC, appointment_alert_logs.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    return [dict(row) for row in rows]


def record_appointment_alert_action(data):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()
    raw_payload = data.get("raw_payload")
    if raw_payload is not None and not isinstance(raw_payload, str):
        raw_payload = json.dumps(raw_payload, ensure_ascii=False)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO appointment_alert_action_logs (
                alert_log_id,
                group_id,
                appointment_id,
                action,
                line_user_id,
                source_type,
                source_id,
                created_at,
                raw_payload
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("alert_log_id"),
                data.get("group_id"),
                data.get("appointment_id"),
                data["action"],
                data.get("line_user_id"),
                data.get("source_type"),
                data.get("source_id"),
                created_at,
                raw_payload,
            ),
        )

    return cursor.lastrowid


def list_appointment_alert_action_logs(group_id=None, limit=50):
    init_db()
    limit = max(1, min(int(limit or 50), 200))

    with get_connection() as connection:
        if group_id:
            rows = connection.execute(
                """
                SELECT *
                FROM appointment_alert_action_logs
                WHERE group_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (group_id, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM appointment_alert_action_logs
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    return [dict(row) for row in rows]


def save_ocr_result(group_id, result, image_path=None):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()
    data = result.get("data")
    data_json = json.dumps(data, ensure_ascii=False) if data is not None else None

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO ocr_results (
                group_id,
                detected_type,
                data_json,
                interpretation,
                interaction_report,
                image_path,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                group_id,
                result.get("detected_type"),
                data_json,
                result.get("interpretation"),
                result.get("interaction_report"),
                image_path,
                created_at,
            ),
        )

    return cursor.lastrowid


def list_ocr_results(group_id=None):
    init_db()

    with get_connection() as connection:
        if group_id:
            rows = connection.execute(
                """
                SELECT *
                FROM ocr_results
                WHERE group_id = ?
                ORDER BY created_at DESC, id DESC
                """,
                (group_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM ocr_results
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()

    results = []
    for row in rows:
        result = dict(row)
        result["data"] = json.loads(result.pop("data_json") or "null")
        results.append(result)

    return results


def save_carebot_assessment(data):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()
    responses_json = json.dumps(data.get("responses", {}), ensure_ascii=False)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO carebot_assessments (
                group_id,
                line_user_id,
                assessment_type,
                score,
                responses_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("group_id"),
                data.get("line_user_id"),
                data["assessment_type"],
                int(data["score"]),
                responses_json,
                created_at,
            ),
        )

    return cursor.lastrowid


def list_carebot_assessments(group_id=None):
    init_db()

    with get_connection() as connection:
        if group_id:
            rows = connection.execute(
                """
                SELECT *
                FROM carebot_assessments
                WHERE group_id = ?
                ORDER BY created_at DESC, id DESC
                """,
                (group_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM carebot_assessments
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()

    assessments = []
    for row in rows:
        assessment = dict(row)
        assessment["responses"] = json.loads(assessment.pop("responses_json") or "{}")
        assessments.append(assessment)

    return assessments
