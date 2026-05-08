import os
import re
import threading
import time as sleep_time
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from linebot.models import FlexSendMessage, ImageSendMessage

try:
    from .config import (
        APPOINTMENT_ALERT_LEAD_MINUTES,
        APPOINTMENT_ALERT_LIVE_MODE,
        APPOINTMENT_ALERT_POLL_SECONDS,
        APPOINTMENT_ALERT_TIMEZONE,
        APPOINTMENT_ALERT_WINDOW_MINUTES,
        APPOINTMENT_ALERT_WORKER_ENABLED,
        PUBLIC_BASE_URL,
    )
    from .flex import appointment_alert_bubble
    from .storage import (
        list_appointment_alert_logs,
        list_appointments,
        list_registrations,
        reserve_appointment_alert,
        update_appointment_alert_log,
    )
except ImportError:
    from config import (
        APPOINTMENT_ALERT_LEAD_MINUTES,
        APPOINTMENT_ALERT_LIVE_MODE,
        APPOINTMENT_ALERT_POLL_SECONDS,
        APPOINTMENT_ALERT_TIMEZONE,
        APPOINTMENT_ALERT_WINDOW_MINUTES,
        APPOINTMENT_ALERT_WORKER_ENABLED,
        PUBLIC_BASE_URL,
    )
    from flex import appointment_alert_bubble
    from storage import (
        list_appointment_alert_logs,
        list_appointments,
        list_registrations,
        reserve_appointment_alert,
        update_appointment_alert_log,
    )


THAI_MONTHS = {
    "ม.ค.": 1,
    "มกราคม": 1,
    "ก.พ.": 2,
    "กุมภาพันธ์": 2,
    "มี.ค.": 3,
    "มีนาคม": 3,
    "เม.ย.": 4,
    "เมษายน": 4,
    "พ.ค.": 5,
    "พฤษภาคม": 5,
    "มิ.ย.": 6,
    "มิถุนายน": 6,
    "ก.ค.": 7,
    "กรกฎาคม": 7,
    "ส.ค.": 8,
    "สิงหาคม": 8,
    "ก.ย.": 9,
    "กันยายน": 9,
    "ต.ค.": 10,
    "ตุลาคม": 10,
    "พ.ย.": 11,
    "พฤศจิกายน": 11,
    "ธ.ค.": 12,
    "ธันวาคม": 12,
}

_worker_started = False
_worker_lock = threading.Lock()


def build_appointment_alert_schedule(group_id=None):
    schedules = []
    grouped_members = {}

    for appointment in list_appointments(group_id):
        appointment_group_id = appointment.get("group_id")
        if appointment_group_id not in grouped_members:
            grouped_members[appointment_group_id] = split_group_members(appointment_group_id)

        appointment_dt = parse_appointment_datetime(appointment)
        if not appointment_dt:
            continue

        members = grouped_members[appointment_group_id]
        schedule = {
            "group_id": appointment_group_id,
            "appointment_id": appointment["id"],
            "hospital": appointment.get("hospital") or "",
            "department": appointment.get("department") or "",
            "doctor": appointment.get("doctor") or "",
            "appointment_date": appointment.get("appointment_date") or "",
            "appointment_time": appointment.get("appointment_time") or "",
            "appointment_datetime": appointment_dt.isoformat(),
            "appointment_display": format_appointment_display(appointment, appointment_dt),
            "preparation": appointment.get("preparation") or "",
            "reason": appointment.get("reason") or "",
            "image_path": appointment.get("image_path") or "",
            "created_at": appointment.get("created_at") or "",
            "patients": members["patients"],
            "caregivers": members["caregivers"],
            "alert_key": "appointment_reminder",
            "scheduled_for": (appointment_dt - timedelta(minutes=APPOINTMENT_ALERT_LEAD_MINUTES)).isoformat(),
        }
        schedules.append(schedule)

    if is_test_mode():
        schedules = apply_test_alert_times(schedules)

    return sorted(schedules, key=lambda item: (item["scheduled_for"], item.get("hospital") or ""))


def collect_due_appointment_alerts(group_id=None, at=None, window_minutes=None):
    tz = get_alert_timezone()
    now = coerce_local_datetime(at, tz)
    window = timedelta(minutes=window_minutes or APPOINTMENT_ALERT_WINDOW_MINUTES)
    start = now - window
    due_alerts = []

    for schedule in build_appointment_alert_schedule(group_id):
        scheduled_for = datetime.fromisoformat(schedule["scheduled_for"])
        scheduled_for = scheduled_for.astimezone(tz) if scheduled_for.tzinfo else scheduled_for.replace(tzinfo=tz)
        if start <= scheduled_for <= now:
            alert = dict(schedule)
            alert.update(
                {
                    "alert_date": scheduled_for.date().isoformat(),
                    "scheduled_for": scheduled_for.isoformat(),
                    "scheduled_time": scheduled_for.strftime("%H:%M"),
                    "target_type": "group",
                    "target_id": schedule["group_id"],
                }
            )
            alert["message"] = build_alert_message(alert)
            due_alerts.append(alert)

    return due_alerts


def run_appointment_alerts(line_bot_api, group_id=None, at=None, window_minutes=None, dry_run=False):
    due_alerts = collect_due_appointment_alerts(
        group_id=group_id,
        at=at,
        window_minutes=window_minutes,
    )
    results = []

    if dry_run:
        return {"success": True, "dry_run": True, "alerts": due_alerts, "results": results}

    for alert in due_alerts:
        alert_log_id = reserve_appointment_alert(alert)
        if not alert_log_id:
            results.append({"status": "skipped_duplicate", "alert": alert})
            continue

        try:
            line_bot_api.push_message(
                to=alert["target_id"],
                messages=build_line_messages(alert, alert_log_id),
            )
        except Exception as error:
            update_appointment_alert_log(alert_log_id, "failed", str(error))
            results.append({"status": "failed", "error": str(error), "alert": alert})
            continue

        update_appointment_alert_log(alert_log_id, "sent")
        results.append({"status": "sent", "alert_log_id": alert_log_id, "alert": alert})

    return {"success": True, "dry_run": False, "alerts": due_alerts, "results": results}


def start_appointment_alert_worker(line_bot_api, logger=None):
    global _worker_started

    if not APPOINTMENT_ALERT_WORKER_ENABLED:
        return False

    if os.environ.get("WERKZEUG_RUN_MAIN") == "false":
        return False

    with _worker_lock:
        if _worker_started:
            return False

        _worker_started = True
        worker = threading.Thread(
            target=_worker_loop,
            args=(line_bot_api, logger),
            name="appointment-alert-worker",
            daemon=True,
        )
        worker.start()
        return True


def recent_appointment_alert_logs(group_id=None, limit=50):
    return list_appointment_alert_logs(group_id=group_id, limit=limit)


def _worker_loop(line_bot_api, logger=None):
    while True:
        try:
            run_appointment_alerts(line_bot_api)
        except Exception as error:
            if logger:
                logger.exception("Appointment alert worker failed: %s", error)
        sleep_time.sleep(max(15, APPOINTMENT_ALERT_POLL_SECONDS))


def build_line_messages(alert, alert_log_id=None):
    messages = []
    image_url = build_public_image_url(alert.get("image_path"))
    if image_url:
        messages.append(
            ImageSendMessage(
                original_content_url=image_url,
                preview_image_url=image_url,
            )
        )

    messages.append(
        FlexSendMessage(
            alt_text=f"แจ้งเตือนนัดหมาย: {alert.get('hospital') or 'ใบนัดหมอ'}",
            contents=appointment_alert_bubble(alert, alert_log_id=alert_log_id),
        )
    )
    return messages


def build_alert_message(alert):
    return (
        "แจ้งเตือนนัดหมาย\n"
        f"โรงพยาบาล: {alert.get('hospital') or '-'}\n"
        f"วันเวลา: {alert.get('appointment_display') or '-'}\n"
        f"แผนก: {alert.get('department') or '-'}\n"
        f"แพทย์: {alert.get('doctor') or '-'}"
    )


def parse_appointment_datetime(appointment):
    if appointment.get("appointment_datetime"):
        try:
            return coerce_local_datetime(appointment["appointment_datetime"], get_alert_timezone())
        except ValueError:
            pass

    date_text = appointment.get("appointment_date") or ""
    time_text = appointment.get("appointment_time") or ""
    parsed_date = parse_thai_date(date_text)
    parsed_time = parse_time_range_start(time_text) or time(9, 0)
    if not parsed_date:
        return None

    tz = get_alert_timezone()
    return datetime.combine(parsed_date, parsed_time, tzinfo=tz)


def parse_thai_date(value):
    text = normalize_text(value)
    numeric_match = re.search(r"(\d{1,4})[/-](\d{1,2})[/-](\d{1,4})", text)
    if numeric_match:
        first = int(numeric_match.group(1))
        month = int(numeric_match.group(2))
        last = int(numeric_match.group(3))
        if first > 31:
            year = normalize_year(first)
            day = last
        else:
            day = first
            year = normalize_year(last)
        return safe_date(year, month, day)

    for month_name, month_number in THAI_MONTHS.items():
        if month_name in text:
            year_match = re.search(r"(\d{4})", text)
            day_match = re.search(r"(\d{1,2})", text)
            if year_match and day_match:
                return safe_date(
                    normalize_year(int(year_match.group(1))),
                    month_number,
                    int(day_match.group(1)),
                )

    return None


def parse_time_range_start(value):
    match = re.search(r"(\d{1,2})[:.](\d{2})", str(value or ""))
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2))
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return time(hour, minute)
    return None


def normalize_year(year):
    if year < 100:
        year += 2500
    return year - 543 if year > 2400 else year


def safe_date(year, month, day):
    try:
        return datetime(year, month, day).date()
    except ValueError:
        return None


def format_appointment_display(appointment, appointment_dt):
    date_text = appointment.get("appointment_date") or appointment_dt.strftime("%Y-%m-%d")
    time_text = appointment.get("appointment_time") or appointment_dt.strftime("%H:%M")
    return f"{date_text} {time_text}".strip()


def apply_test_alert_times(schedules):
    shifted_schedules = []
    tz = get_alert_timezone()
    counters = {}

    for schedule in schedules:
        appointment_id = schedule.get("appointment_id")
        slot_index = counters.get(appointment_id, 0)
        counters[appointment_id] = slot_index + 1
        base = parse_created_at(schedule.get("created_at"), tz)
        scheduled_for = base + timedelta(minutes=1 + (slot_index % 3))
        shifted = dict(schedule)
        shifted.update(
            {
                "test_mode": True,
                "live_mode": False,
                "scheduled_for": scheduled_for.isoformat(),
                "alert_key": f"test:{base.strftime('%Y%m%d%H%M')}:appointment_reminder",
            }
        )
        shifted_schedules.append(shifted)

    return shifted_schedules


def parse_created_at(value, tz):
    if value:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            local_created_at = parsed.astimezone(tz) if parsed.tzinfo else parsed.replace(tzinfo=tz)
            return local_created_at.replace(second=0, microsecond=0)
        except ValueError:
            pass
    return datetime.now(tz).replace(second=0, microsecond=0)


def split_group_members(group_id):
    patients = []
    caregivers = []
    for member in list_registrations(group_id):
        person = {
            "id": member.get("id"),
            "name": " ".join(part for part in (member.get("first_name"), member.get("last_name")) if part).strip(),
            "line_user_id": member.get("line_user_id") or "",
            "phone": member.get("phone") or "",
        }
        if (member.get("role") or "").strip().lower() == "patient":
            patients.append(person)
        elif (member.get("role") or "").strip().lower() == "caregiver":
            caregivers.append(person)
    return {"patients": patients, "caregivers": caregivers}


def coerce_local_datetime(value, tz):
    if value is None or value == "":
        return datetime.now(tz)
    if isinstance(value, datetime):
        return value.astimezone(tz) if value.tzinfo else value.replace(tzinfo=tz)

    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed.astimezone(tz) if parsed.tzinfo else parsed.replace(tzinfo=tz)


def get_alert_timezone():
    try:
        return ZoneInfo(APPOINTMENT_ALERT_TIMEZONE or "Asia/Bangkok")
    except ZoneInfoNotFoundError:
        return ZoneInfo("Asia/Bangkok")


def build_public_image_url(image_path):
    if not image_path:
        return None
    if image_path.startswith(("http://", "https://")):
        return image_path
    if not PUBLIC_BASE_URL:
        return None
    path = image_path if image_path.startswith("/") else f"/{image_path}"
    return f"{PUBLIC_BASE_URL}{path}"


def is_test_mode():
    return not APPOINTMENT_ALERT_LIVE_MODE


def normalize_text(value):
    return " ".join(str(value or "").replace(",", " ").split())
