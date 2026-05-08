import json
from datetime import datetime, timezone
from urllib.parse import urlparse

import pymysql
import pymysql.cursors

try:
    from .config import DATABASE_URL
except ImportError:
    from config import DATABASE_URL


class _ConnectionWrapper:
    """Wraps pymysql connection to provide a sqlite3-like interface."""

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        cursor = self._conn.cursor()
        cursor.execute(sql, params)
        return cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self._conn.commit()
            else:
                self._conn.rollback()
        finally:
            self._conn.close()
        return False


def get_connection():
    url = urlparse(DATABASE_URL)
    conn = pymysql.connect(
        host=url.hostname,
        port=url.port or 3306,
        user=url.username,
        password=url.password,
        database=url.path.lstrip("/"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return _ConnectionWrapper(conn)


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id VARCHAR(255) NOT NULL,
                line_user_id VARCHAR(255),
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(255) NOT NULL,
                gender VARCHAR(50) NOT NULL,
                role VARCHAR(100) NOT NULL,
                height_cm DOUBLE,
                weight_kg DOUBLE,
                created_at VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        ensure_column(connection, "registrations", "line_user_id", "VARCHAR(255)")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS medicines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id VARCHAR(255) NOT NULL,
                medicine_name VARCHAR(255) NOT NULL,
                dosage TEXT,
                take_time TEXT,
                instruction TEXT,
                image_path TEXT,
                created_at VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ocr_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id VARCHAR(255) NOT NULL,
                detected_type VARCHAR(255),
                data_json LONGTEXT,
                interpretation LONGTEXT,
                interaction_report LONGTEXT,
                image_path TEXT,
                created_at VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id VARCHAR(255) NOT NULL,
                hospital TEXT,
                department TEXT,
                doctor TEXT,
                appointment_date VARCHAR(255),
                appointment_time VARCHAR(255),
                appointment_datetime VARCHAR(255),
                preparation TEXT,
                reason TEXT,
                interpretation LONGTEXT,
                image_path TEXT,
                created_at VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS carebot_assessments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id VARCHAR(255),
                line_user_id VARCHAR(255),
                assessment_type VARCHAR(255) NOT NULL,
                score INT NOT NULL,
                responses_json LONGTEXT NOT NULL,
                created_at VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS carebot_chat_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id VARCHAR(255),
                line_user_id VARCHAR(255),
                role VARCHAR(100) NOT NULL,
                message LONGTEXT NOT NULL,
                context_json LONGTEXT,
                created_at VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS medicine_alert_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id VARCHAR(255) NOT NULL,
                medicine_id INT NOT NULL,
                alert_key VARCHAR(100) NOT NULL,
                alert_date VARCHAR(50) NOT NULL,
                scheduled_for VARCHAR(255) NOT NULL,
                target_type VARCHAR(50) NOT NULL,
                target_id VARCHAR(255) NOT NULL,
                message LONGTEXT NOT NULL,
                status VARCHAR(100) NOT NULL,
                error TEXT,
                created_at VARCHAR(255) NOT NULL,
                sent_at VARCHAR(255),
                UNIQUE KEY idx_medicine_alert_logs_once (medicine_id, alert_key, alert_date, target_type, target_id),
                KEY idx_medicine_alert_logs_medicine (medicine_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS medicine_alert_action_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                alert_log_id INT,
                group_id VARCHAR(255),
                medicine_id INT,
                action VARCHAR(255) NOT NULL,
                line_user_id VARCHAR(255),
                source_type VARCHAR(255),
                source_id VARCHAR(255),
                created_at VARCHAR(255) NOT NULL,
                raw_payload LONGTEXT,
                KEY idx_medicine_alert_action_logs_alert (alert_log_id, created_at),
                KEY idx_medicine_alert_action_logs_medicine (medicine_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS appointment_alert_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id VARCHAR(255) NOT NULL,
                appointment_id INT NOT NULL,
                alert_key VARCHAR(100) NOT NULL,
                alert_date VARCHAR(50) NOT NULL,
                scheduled_for VARCHAR(255) NOT NULL,
                target_type VARCHAR(50) NOT NULL,
                target_id VARCHAR(255) NOT NULL,
                message LONGTEXT NOT NULL,
                status VARCHAR(100) NOT NULL,
                error TEXT,
                created_at VARCHAR(255) NOT NULL,
                sent_at VARCHAR(255),
                UNIQUE KEY idx_appointment_alert_logs_once (appointment_id, alert_key, alert_date, target_type, target_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS appointment_alert_action_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                alert_log_id INT,
                group_id VARCHAR(255),
                appointment_id INT,
                action VARCHAR(255) NOT NULL,
                line_user_id VARCHAR(255),
                source_type VARCHAR(255),
                source_id VARCHAR(255),
                created_at VARCHAR(255) NOT NULL,
                raw_payload LONGTEXT,
                KEY idx_appointment_alert_action_logs_alert (alert_log_id, created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        cleanup_orphan_medicine_alert_records(connection)


def ensure_column(connection, table_name, column_name, column_type):
    cursor = connection.execute("SHOW COLUMNS FROM %s" % table_name)
    columns = cursor.fetchall()
    if column_name in {col["Field"] for col in columns}:
        return

    connection.execute(
        "ALTER TABLE %s ADD COLUMN %s %s" % (table_name, column_name, column_type)
    )


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

    placeholders = ", ".join("%s" for _ in medicine_ids)
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
                    group_id = %s,
                    line_user_id = %s,
                    first_name = %s,
                    last_name = %s,
                    email = %s,
                    phone = %s,
                    gender = %s,
                    role = %s,
                    height_cm = %s,
                    weight_kg = %s,
                    created_at = %s
                WHERE id = %s
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            WHERE id = %s
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
            WHERE line_user_id = %s
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
            WHERE id = %s
            """,
            (registration_id,),
        ).fetchone()
        if not existing:
            return None

        connection.execute(
            """
            UPDATE registrations
            SET
                group_id = %s,
                line_user_id = %s,
                first_name = %s,
                last_name = %s,
                email = %s,
                phone = %s,
                gender = %s,
                role = %s,
                height_cm = %s,
                weight_kg = %s,
                created_at = %s
            WHERE id = %s
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
            WHERE id = %s
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
            WHERE id = %s
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
        WHERE line_user_id = %s
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
                WHERE group_id = %s
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
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                WHERE group_id = %s
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
                WHERE id = %s AND group_id = %s
                """,
                (appointment_id, group_id),
            ).fetchone()
        else:
            appointment = connection.execute(
                """
                SELECT id
                FROM appointments
                WHERE id = %s
                """,
                (appointment_id,),
            ).fetchone()

        if not appointment:
            return False

        connection.execute(
            """
            DELETE FROM appointment_alert_action_logs
            WHERE
                appointment_id = %s
                OR alert_log_id IN (
                    SELECT id
                    FROM appointment_alert_logs
                    WHERE appointment_id = %s
                )
            """,
            (appointment_id, appointment_id),
        )
        connection.execute(
            """
            DELETE FROM appointment_alert_logs
            WHERE appointment_id = %s
            """,
            (appointment_id,),
        )
        cursor = connection.execute(
            """
            DELETE FROM appointments
            WHERE id = %s
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
                WHERE group_id = %s
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
                WHERE id = %s AND group_id = %s
                """,
                (medicine_id, group_id),
            ).fetchone()
        else:
            medicine = connection.execute(
                """
                SELECT id
                FROM medicines
                WHERE id = %s
                """,
                (medicine_id,),
            ).fetchone()

        if not medicine:
            return False

        delete_medicine_alert_records(connection, [medicine_id])
        cursor = connection.execute(
            """
            DELETE FROM medicines
            WHERE id = %s
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
            WHERE id = %s AND group_id = %s
            """,
            (alert["medicine_id"], alert["group_id"]),
        ).fetchone()
        if not active_medicine:
            return None

        cursor = connection.execute(
            """
            INSERT IGNORE INTO medicine_alert_logs (
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            SET status = %s, error = %s, sent_at = %s
            WHERE id = %s
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
                WHERE medicine_alert_logs.group_id = %s
                ORDER BY medicine_alert_logs.created_at DESC, medicine_alert_logs.id DESC
                LIMIT %s
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
                LIMIT %s
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                WHERE group_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (group_id, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM medicine_alert_action_logs
                ORDER BY created_at DESC, id DESC
                LIMIT %s
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
            WHERE id = %s AND group_id = %s
            """,
            (alert["appointment_id"], alert["group_id"]),
        ).fetchone()
        if not active_appointment:
            return None

        cursor = connection.execute(
            """
            INSERT IGNORE INTO appointment_alert_logs (
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            SET status = %s, error = %s, sent_at = %s
            WHERE id = %s
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
                WHERE appointment_alert_logs.group_id = %s
                ORDER BY appointment_alert_logs.created_at DESC, appointment_alert_logs.id DESC
                LIMIT %s
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
                LIMIT %s
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                WHERE group_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (group_id, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM appointment_alert_action_logs
                ORDER BY created_at DESC, id DESC
                LIMIT %s
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
            VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                WHERE group_id = %s
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
            VALUES (%s, %s, %s, %s, %s, %s)
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


def list_carebot_assessments(group_id=None, line_user_ids=None):
    init_db()
    line_user_ids = [str(user_id).strip() for user_id in (line_user_ids or []) if str(user_id or "").strip()]

    with get_connection() as connection:
        if group_id and line_user_ids:
            placeholders = ", ".join("%s" for _ in line_user_ids)
            rows = connection.execute(
                f"""
                SELECT *
                FROM carebot_assessments
                WHERE group_id = %s OR line_user_id IN ({placeholders})
                ORDER BY created_at DESC, id DESC
                """,
                (group_id, *line_user_ids),
            ).fetchall()
        elif group_id:
            rows = connection.execute(
                """
                SELECT *
                FROM carebot_assessments
                WHERE group_id = %s
                ORDER BY created_at DESC, id DESC
                """,
                (group_id,),
            ).fetchall()
        elif line_user_ids:
            placeholders = ", ".join("%s" for _ in line_user_ids)
            rows = connection.execute(
                f"""
                SELECT *
                FROM carebot_assessments
                WHERE line_user_id IN ({placeholders})
                ORDER BY created_at DESC, id DESC
                """,
                tuple(line_user_ids),
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


def save_carebot_chat_log(data):
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()
    context_json = json.dumps(data.get("context", {}), ensure_ascii=False)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO carebot_chat_logs (
                group_id,
                line_user_id,
                role,
                message,
                context_json,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data.get("group_id"),
                data.get("line_user_id"),
                data["role"],
                data["message"],
                context_json,
                created_at,
            ),
        )

    return cursor.lastrowid


def list_carebot_chat_logs(group_id=None, line_user_ids=None, limit=100):
    init_db()
    line_user_ids = [str(user_id).strip() for user_id in (line_user_ids or []) if str(user_id or "").strip()]
    params = []
    where = ""
    if group_id and line_user_ids:
        placeholders = ", ".join("%s" for _ in line_user_ids)
        where = f"WHERE group_id = %s OR line_user_id IN ({placeholders})"
        params = [group_id, *line_user_ids]
    elif group_id:
        where = "WHERE group_id = %s"
        params = [group_id]
    elif line_user_ids:
        placeholders = ", ".join("%s" for _ in line_user_ids)
        where = f"WHERE line_user_id IN ({placeholders})"
        params = list(line_user_ids)

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT *
            FROM carebot_chat_logs
            {where}
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (*params, int(limit)),
        ).fetchall()

    logs = []
    for row in rows:
        log = dict(row)
        log["context"] = json.loads(log.pop("context_json") or "{}")
        logs.append(log)

    return logs
