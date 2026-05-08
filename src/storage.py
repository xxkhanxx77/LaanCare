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


def ensure_column(connection, table_name, column_name, column_type):
    columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    if column_name in {column["name"] for column in columns}:
        return

    connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


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


def delete_medicine(medicine_id):
    init_db()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM medicines
            WHERE id = ?
            """,
            (medicine_id,),
        )

    return cursor.rowcount > 0


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
