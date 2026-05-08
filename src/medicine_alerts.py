import os
import threading
import time as sleep_time
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from linebot.models import FlexSendMessage, ImageSendMessage

try:
    from .config import (
        DEBUG,
        MEDICINE_ALERT_AFTER_MEAL_MINUTES,
        MEDICINE_ALERT_BEDTIME,
        MEDICINE_ALERT_BEFORE_MEAL_MINUTES,
        MEDICINE_ALERT_EVENING_MEAL,
        MEDICINE_ALERT_LIVE_MODE,
        MEDICINE_ALERT_MORNING_MEAL,
        MEDICINE_ALERT_NOON_MEAL,
        MEDICINE_ALERT_POLL_SECONDS,
        MEDICINE_ALERT_TIMEZONE,
        MEDICINE_ALERT_WINDOW_MINUTES,
        MEDICINE_ALERT_WORKER_ENABLED,
        PUBLIC_BASE_URL,
    )
    from .flex import medicine_alert_bubble
    from .storage import (
        list_medicine_alert_logs,
        list_medicines,
        list_registrations,
        reserve_medicine_alert,
        update_medicine_alert_log,
    )
except ImportError:
    from config import (
        DEBUG,
        MEDICINE_ALERT_AFTER_MEAL_MINUTES,
        MEDICINE_ALERT_BEDTIME,
        MEDICINE_ALERT_BEFORE_MEAL_MINUTES,
        MEDICINE_ALERT_EVENING_MEAL,
        MEDICINE_ALERT_LIVE_MODE,
        MEDICINE_ALERT_MORNING_MEAL,
        MEDICINE_ALERT_NOON_MEAL,
        MEDICINE_ALERT_POLL_SECONDS,
        MEDICINE_ALERT_TIMEZONE,
        MEDICINE_ALERT_WINDOW_MINUTES,
        MEDICINE_ALERT_WORKER_ENABLED,
        PUBLIC_BASE_URL,
    )
    from flex import medicine_alert_bubble
    from storage import (
        list_medicine_alert_logs,
        list_medicines,
        list_registrations,
        reserve_medicine_alert,
        update_medicine_alert_log,
    )


PERIODS = [
    ("morning", "เช้า", ("เช้า", "มื้อเช้า", "ตอนเช้า", "morning", "breakfast")),
    ("noon", "กลางวัน", ("กลางวัน", "เที่ยง", "มื้อกลางวัน", "noon", "lunch")),
    ("evening", "เย็น", ("เย็น", "ค่ำ", "มื้อเย็น", "evening", "dinner")),
]
RELATIONS = [
    ("before_meal", "ก่อนอาหาร", ("ก่อนอาหาร", "ก่อน อาหาร", "ก่อนกิน", "ก่อนมื้อ", "before meal")),
    ("after_meal", "หลังอาหาร", ("หลังอาหาร", "หลัง อาหาร", "หลังกิน", "หลังมื้อ", "after meal")),
]
AS_NEEDED_TOKENS = (
    "เมื่อมีอาการ",
    "เวลาปวด",
    "มีไข้",
    "ตามอาการ",
    "as needed",
    "prn",
)
BEDTIME_TOKENS = ("ก่อนนอน", "เวลานอน", "bedtime", "before bed")

_worker_started = False
_worker_lock = threading.Lock()


def build_medicine_alert_schedule(group_id=None):
    medicines = list_medicines(group_id)
    grouped_members = {}
    schedules = []

    for medicine in medicines:
        medicine_group_id = medicine.get("group_id")
        if medicine_group_id not in grouped_members:
            grouped_members[medicine_group_id] = split_group_members(medicine_group_id)

        members = grouped_members[medicine_group_id]
        for event in parse_medicine_events(medicine):
            event.update(
                {
                    "group_id": medicine_group_id,
                    "medicine_id": medicine["id"],
                    "medicine_name": medicine.get("medicine_name") or "",
                    "dosage": medicine.get("dosage") or "",
                    "instruction": medicine.get("instruction") or "",
                    "take_time": medicine.get("take_time") or "",
                    "created_at": medicine.get("created_at") or "",
                    "image_path": medicine.get("image_path") or "",
                    "patients": members["patients"],
                    "caregivers": members["caregivers"],
                }
            )
            schedules.append(event)

    sorted_schedules = sorted(
        schedules,
        key=lambda item: (
            item.get("group_id") or "",
            item.get("time") or "",
            item.get("medicine_name") or "",
        ),
    )

    if is_test_mode():
        return apply_test_alert_times(sorted_schedules)

    return sorted_schedules


def collect_due_medicine_alerts(group_id=None, at=None, window_minutes=None):
    tz = get_alert_timezone()
    now = coerce_local_datetime(at, tz)
    window = timedelta(minutes=window_minutes or MEDICINE_ALERT_WINDOW_MINUTES)
    start = now - window
    candidate_dates = [now.date()]
    if start.date() != now.date():
        candidate_dates.append(start.date())

    due_alerts = []
    for schedule in build_medicine_alert_schedule(group_id):
        for scheduled_for in scheduled_datetimes_for(schedule, candidate_dates, tz):
            if start <= scheduled_for <= now:
                alert = dict(schedule)
                alert_date = scheduled_for.date().isoformat()
                alert.update(
                    {
                        "alert_date": alert_date,
                        "alert_key": schedule["alert_key"],
                        "scheduled_for": scheduled_for.isoformat(),
                        "scheduled_time": scheduled_for.strftime("%H:%M"),
                        "target_type": "group",
                        "target_id": schedule["group_id"],
                    }
                )
                alert["message"] = build_alert_message(alert)
                due_alerts.append(alert)

    return due_alerts


def run_medicine_alerts(line_bot_api, group_id=None, at=None, window_minutes=None, dry_run=False):
    due_alerts = collect_due_medicine_alerts(
        group_id=group_id,
        at=at,
        window_minutes=window_minutes,
    )
    results = []

    if dry_run:
        return {"success": True, "dry_run": True, "alerts": due_alerts, "results": results}

    for alert in due_alerts:
        alert_log_id = reserve_medicine_alert(alert)
        if not alert_log_id:
            results.append({"status": "skipped_duplicate", "alert": alert})
            continue

        try:
            line_bot_api.push_message(
                to=alert["target_id"],
                messages=build_line_messages(alert, alert_log_id),
            )
        except Exception as error:
            update_medicine_alert_log(alert_log_id, "failed", str(error))
            results.append({"status": "failed", "error": str(error), "alert": alert})
            continue

        update_medicine_alert_log(alert_log_id, "sent")
        results.append({"status": "sent", "alert_log_id": alert_log_id, "alert": alert})

    return {"success": True, "dry_run": False, "alerts": due_alerts, "results": results}


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
            alt_text=f"แจ้งเตือนกินยา: {alert.get('medicine_name') or 'รายการยา'}",
            contents=medicine_alert_bubble(alert, alert_log_id=alert_log_id),
        )
    )
    return messages


def build_public_image_url(image_path):
    if not image_path:
        return None

    if image_path.startswith(("http://", "https://")):
        return image_path

    if not PUBLIC_BASE_URL:
        return None

    path = image_path if image_path.startswith("/") else f"/{image_path}"
    return f"{PUBLIC_BASE_URL}{path}"


def recent_medicine_alert_logs(group_id=None, limit=50):
    return list_medicine_alert_logs(group_id=group_id, limit=limit)


def start_medicine_alert_worker(line_bot_api, logger=None):
    global _worker_started

    if not MEDICINE_ALERT_WORKER_ENABLED:
        return False

    if is_debug_reloader_parent():
        return False

    with _worker_lock:
        if _worker_started:
            return False

        _worker_started = True
        worker = threading.Thread(
            target=_worker_loop,
            args=(line_bot_api, logger),
            name="medicine-alert-worker",
            daemon=True,
        )
        worker.start()
        return True


def is_debug_reloader_parent():
    return os.environ.get("WERKZEUG_RUN_MAIN") == "false"


def _worker_loop(line_bot_api, logger=None):
    while True:
        try:
            run_medicine_alerts(line_bot_api)
        except Exception as error:
            if logger:
                logger.exception("Medicine alert worker failed: %s", error)
        sleep_time.sleep(max(15, MEDICINE_ALERT_POLL_SECONDS))


def split_group_members(group_id):
    members = list_registrations(group_id)
    patients = []
    caregivers = []

    for member in members:
        role = (member.get("role") or "").strip().lower()
        person = {
            "id": member.get("id"),
            "name": format_member_name(member),
            "line_user_id": member.get("line_user_id") or "",
            "phone": member.get("phone") or "",
        }
        if role == "patient":
            patients.append(person)
        elif role == "caregiver":
            caregivers.append(person)

    return {"patients": patients, "caregivers": caregivers}


def parse_medicine_events(medicine):
    take_time = medicine.get("take_time") or ""
    instruction = medicine.get("instruction") or ""
    text = normalize_schedule_text(f"{take_time} {instruction}")

    if is_as_needed_only(text):
        return []

    periods = []
    for period_key, period_label, tokens in PERIODS:
        if has_any_token(text, tokens):
            periods.append((period_key, period_label))

    relations = []
    for relation_key, relation_label, tokens in RELATIONS:
        if has_any_token(text, tokens):
            relations.append((relation_key, relation_label))

    assumed_periods = False
    if not periods and relations:
        periods = [(period_key, period_label) for period_key, period_label, _ in PERIODS]
        assumed_periods = True

    if periods and not relations:
        relations = [("at_meal", "เวลาอาหาร")]

    events = []
    for period_key, period_label in periods:
        for relation_key, relation_label in relations:
            alert_time = alert_time_for(period_key, relation_key)
            events.append(
                {
                    "period": period_key,
                    "relation": relation_key,
                    "time": alert_time,
                    "slot_label": f"{relation_label}{period_label}" if relation_key != "at_meal" else f"{period_label}",
                    "alert_key": f"{period_key}:{relation_key}",
                    "assumed_periods": assumed_periods,
                }
            )

    if has_any_token(text, BEDTIME_TOKENS):
        events.append(
            {
                "period": "bedtime",
                "relation": "bedtime",
                "time": normalize_hhmm(MEDICINE_ALERT_BEDTIME, "21:00"),
                "slot_label": "ก่อนนอน",
                "alert_key": "bedtime",
                "assumed_periods": False,
            }
        )

    return dedupe_events(events)


def build_alert_message(alert):
    patient_names = names_or_fallback(alert.get("patients"), "ยังไม่มีข้อมูล Patient")
    caregiver_names = names_or_fallback(alert.get("caregivers"), "ยังไม่มีข้อมูล Caregiver")
    dosage_line = f"\nขนาดยา: {alert['dosage']}" if alert.get("dosage") else ""
    mode_line = "[TEST MODE]\n" if alert.get("test_mode") else ""

    return (
        f"{mode_line}แจ้งเตือนกินยา\n"
        f"ผู้ป่วย: {patient_names}\n"
        f"ผู้ดูแล: {caregiver_names}\n"
        f"เวลา: {alert['slot_label']} ({alert['scheduled_time']})\n"
        f"ยา: {alert['medicine_name']}"
        f"{dosage_line}\n"
        "กรุณาช่วยเช็กว่าผู้ป่วยได้รับยาตามเวลานี้แล้ว"
    )


def coerce_local_datetime(value, tz):
    if isinstance(value, datetime):
        return value.astimezone(tz) if value.tzinfo else value.replace(tzinfo=tz)

    if isinstance(value, str) and value.strip():
        raw_value = value.strip()
        if ":" in raw_value and "T" not in raw_value and len(raw_value) <= 5:
            hour, minute = parse_hour_minute(raw_value, default=(0, 0))
            now = datetime.now(tz)
            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
        return parsed.astimezone(tz) if parsed.tzinfo else parsed.replace(tzinfo=tz)

    return datetime.now(tz)


def get_alert_timezone():
    try:
        return ZoneInfo(MEDICINE_ALERT_TIMEZONE or "Asia/Bangkok")
    except ZoneInfoNotFoundError:
        return ZoneInfo("Asia/Bangkok")


def scheduled_datetimes_for(schedule, candidate_dates, tz):
    if schedule.get("test_scheduled_for"):
        parsed = datetime.fromisoformat(schedule["test_scheduled_for"])
        return [parsed.astimezone(tz) if parsed.tzinfo else parsed.replace(tzinfo=tz)]

    scheduled_time = parse_hhmm(schedule["time"], default=time(8, 0))
    return [
        datetime.combine(candidate_date, scheduled_time, tzinfo=tz)
        for candidate_date in candidate_dates
    ]


def apply_test_alert_times(schedules):
    if not schedules:
        return schedules

    tz = get_alert_timezone()
    shifted_schedules = []
    slot_indexes_by_medicine = {}

    for schedule in schedules:
        medicine_id = schedule.get("medicine_id")
        slot_index = slot_indexes_by_medicine.get(medicine_id, 0)
        slot_indexes_by_medicine[medicine_id] = slot_index + 1
        test_base = get_test_alert_base(schedule, tz)
        anchor_key = test_base.strftime("%Y%m%d%H%M")
        shifted = dict(schedule)
        scheduled_for = test_base + timedelta(minutes=1 + (slot_index % 3))
        shifted.update(
            {
                "time": scheduled_for.strftime("%H:%M"),
                "test_mode": True,
                "live_mode": False,
                "test_scheduled_for": scheduled_for.isoformat(),
                "alert_key": f"test:{anchor_key}:{schedule['alert_key']}",
            }
        )
        shifted_schedules.append(shifted)

    return sorted(
        shifted_schedules,
        key=lambda item: (
            item.get("test_scheduled_for") or "",
            item.get("medicine_name") or "",
        ),
    )


def get_test_alert_base(schedule, tz):
    created_at = schedule.get("created_at")
    if created_at:
        try:
            parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            local_created_at = parsed.astimezone(tz) if parsed.tzinfo else parsed.replace(tzinfo=tz)
            return local_created_at.replace(second=0, microsecond=0)
        except ValueError:
            pass

    return datetime.now(tz).replace(second=0, microsecond=0)


def is_test_mode():
    return not MEDICINE_ALERT_LIVE_MODE


def alert_time_for(period_key, relation_key):
    meal_times = {
        "morning": MEDICINE_ALERT_MORNING_MEAL,
        "noon": MEDICINE_ALERT_NOON_MEAL,
        "evening": MEDICINE_ALERT_EVENING_MEAL,
    }
    meal_time = parse_hhmm(meal_times.get(period_key), default=time(8, 0))
    base_dt = datetime.combine(datetime.today(), meal_time)

    if relation_key == "before_meal":
        base_dt -= timedelta(minutes=MEDICINE_ALERT_BEFORE_MEAL_MINUTES)
    elif relation_key == "after_meal":
        base_dt += timedelta(minutes=MEDICINE_ALERT_AFTER_MEAL_MINUTES)

    return base_dt.strftime("%H:%M")


def parse_hhmm(value, default):
    hour, minute = parse_hour_minute(value, default=(default.hour, default.minute))
    return time(hour=hour, minute=minute)


def parse_hour_minute(value, default):
    try:
        hour_text, minute_text = str(value or "").strip().split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute
    except (TypeError, ValueError):
        pass

    return default


def normalize_hhmm(value, default):
    hour, minute = parse_hour_minute(value, parse_hour_minute(default, (21, 0)))
    return f"{hour:02d}:{minute:02d}"


def normalize_schedule_text(value):
    text = str(value or "").strip().lower()
    for separator in (",", "，", "/", "\\", "|", ";", "\n", "\t"):
        text = text.replace(separator, " ")
    return " ".join(text.split())


def has_any_token(text, tokens):
    compact_text = text.replace(" ", "")
    for token in tokens:
        normalized_token = normalize_schedule_text(token)
        if normalized_token in text or normalized_token.replace(" ", "") in compact_text:
            return True
    return False


def is_as_needed_only(text):
    return has_any_token(text, AS_NEEDED_TOKENS) and not any(
        has_any_token(text, tokens) for _, _, tokens in PERIODS
    )


def dedupe_events(events):
    seen = set()
    unique_events = []
    for event in events:
        key = event["alert_key"]
        if key in seen:
            continue
        seen.add(key)
        unique_events.append(event)
    return unique_events


def format_member_name(member):
    return " ".join(
        part
        for part in (member.get("first_name"), member.get("last_name"))
        if part
    ).strip()


def names_or_fallback(members, fallback):
    names = [member["name"] for member in members or [] if member.get("name")]
    return ", ".join(names) if names else fallback
