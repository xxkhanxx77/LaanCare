try:
    from .carebot import CareBotError, generate_carebot_reply, get_carebot_payload, get_phq9_result
    from .config import *
    from .flex import *
    from .medguard_ocr import OCRServiceError, perform_health_ocr
    from .medicine_alerts import (
        build_medicine_alert_schedule,
        collect_due_medicine_alerts,
        recent_medicine_alert_logs,
        run_medicine_alerts,
        start_medicine_alert_worker,
    )
    from .ocr_engine import check_interactions
    from .symptom_db import ChatDatabase
    from .symptom_ems_loader import EmsCorpus
    from .symptom_engine import ChatEngine
    from .symptom_openai_client import OpenAIJsonClient
    from .storage import (
        delete_medicine,
        delete_registration,
        get_registration,
        get_registration_by_line_user_id,
        list_carebot_assessments,
        list_medicine_alert_action_logs,
        list_medicines,
        list_ocr_results,
        list_registrations,
        record_medicine_alert_action,
        save_carebot_assessment,
        save_medicine_item,
        save_medicine_items,
        save_ocr_result,
        save_registration,
        update_registration,
    )
except ImportError:
    from carebot import CareBotError, generate_carebot_reply, get_carebot_payload, get_phq9_result
    from config import *
    from flex import *
    from medguard_ocr import OCRServiceError, perform_health_ocr
    from medicine_alerts import (
        build_medicine_alert_schedule,
        collect_due_medicine_alerts,
        recent_medicine_alert_logs,
        run_medicine_alerts,
        start_medicine_alert_worker,
    )
    from ocr_engine import check_interactions
    from symptom_db import ChatDatabase
    from symptom_ems_loader import EmsCorpus
    from symptom_engine import ChatEngine
    from symptom_openai_client import OpenAIJsonClient
    from storage import (
        delete_medicine,
        delete_registration,
        get_registration,
        get_registration_by_line_user_id,
        list_carebot_assessments,
        list_medicine_alert_action_logs,
        list_medicines,
        list_ocr_results,
        list_registrations,
        record_medicine_alert_action,
        save_carebot_assessment,
        save_medicine_item,
        save_medicine_items,
        save_ocr_result,
        save_registration,
        update_registration,
    )


import json
import os
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlencode

from flask import Flask, abort, jsonify, redirect, request, render_template, url_for
from werkzeug.utils import secure_filename
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent,
    StickerMessage,
    TextMessage,
    ImageMessage,
    ImageSendMessage,
    TextSendMessage,
    FollowEvent,
    UnfollowEvent,
    PostbackEvent,
    FlexSendMessage,
    JoinEvent
)
from linebot.exceptions import (
    InvalidSignatureError
)

app = Flask(__name__, template_folder="../templates", static_folder="../static")
ROOT_DIR = Path(__file__).resolve().parents[1]
SYMPTOM_DB_PATH = os.environ.get("CHATBOT_DB", str(ROOT_DIR / "data" / "symptom_chatbot.sqlite3"))
SYMPTOM_DIR = ROOT_DIR / "src" / "symptoms"
_symptom_engine = None


def get_symptom_engine():
    global _symptom_engine
    if _symptom_engine is None:
        symptom_db = ChatDatabase(SYMPTOM_DB_PATH)
        symptom_corpus = EmsCorpus(SYMPTOM_DIR)
        symptom_llm = OpenAIJsonClient()
        _symptom_engine = ChatEngine(symptom_db, symptom_corpus, symptom_llm)
    return _symptom_engine


def decode_symptom_user(user):
    data = dict(user)
    try:
        data["config_json"] = json.loads(data.get("config_json") or "{}")
    except (TypeError, json.JSONDecodeError):
        data["config_json"] = {}
    data["consent_to_share"] = bool(data.get("consent_to_share"))
    return data


def decode_symptom_session(session):
    data = dict(session)
    try:
        data["state_json"] = json.loads(data.get("state_json") or "{}")
    except (TypeError, json.JSONDecodeError):
        data["state_json"] = {}
    return data
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
line_bot_api = LineBotApi(channel_access_token=LINE_ACCESS_TOKEN, timeout=3)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
start_medicine_alert_worker(line_bot_api, app.logger)

@app.route('/')
def home():
    return abort(404)

# TEST
# TEST
# TEST


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        group_id = request.args.get("group_id", "").strip()
        line_user_id = request.args.get("line_user_id", "").strip()
        if not group_id:
            abort(400, "Missing group_id")

        return render_template(
            "register.html",
            group_id=group_id,
            errors={},
            values={"line_user_id": line_user_id},
        )

    values = {
        "group_id": request.form.get("group_id", "").strip(),
        "line_user_id": request.form.get("line_user_id", "").strip(),
        "first_name": request.form.get("first_name", "").strip(),
        "last_name": request.form.get("last_name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "gender": request.form.get("gender", "").strip(),
        "role": request.form.get("role", "").strip(),
        "height_cm": request.form.get("height_cm", "").strip(),
        "weight_kg": request.form.get("weight_kg", "").strip(),
    }
    errors = validate_registration(values)

    if errors:
        return render_template(
            "register.html",
            group_id=values["group_id"],
            errors=errors,
            values=values,
        ), 400

    registration_id = save_registration(
        {
            "group_id": values["group_id"],
            "line_user_id": values["line_user_id"] or None,
            "first_name": values["first_name"],
            "last_name": values["last_name"],
            "email": values["email"],
            "phone": values["phone"],
            "gender": values["gender"],
            "role": values["role"],
            "height_cm": to_float_or_none(values["height_cm"]),
            "weight_kg": to_float_or_none(values["weight_kg"]),
        }
    )

    return redirect(url_for("register_success", registration_id=registration_id))


@app.get("/register/success/<int:registration_id>")
def register_success(registration_id):
    return render_template("register_success.html", registration_id=registration_id)


@app.route("/api/registrations", methods=["GET", "POST"])
def registrations_api():
    if request.method == "POST":
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"success": False, "error": "Expected JSON object"}), 400

        values = registration_values_from_payload(payload)
        errors = validate_registration(values)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        data = registration_data_from_values(values)
        existing = get_registration_by_line_user_id(data.get("line_user_id"))
        registration_id = save_registration(data)

        return jsonify(
            {
                "success": True,
                "registration": get_registration(registration_id),
            }
        ), 200 if existing else 201

    group_id = request.args.get("group_id", "").strip() or None
    return jsonify({"registrations": list_registrations(group_id)})


@app.route("/api/registrations/<int:registration_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def registration_detail_api(registration_id):
    registration = get_registration(registration_id)
    if not registration:
        return jsonify({"success": False, "error": "Registration not found"}), 404

    if request.method == "GET":
        return jsonify({"registration": registration})

    if request.method == "DELETE":
        delete_registration(registration_id)
        return jsonify({"success": True, "deleted_id": registration_id})

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"success": False, "error": "Expected JSON object"}), 400

    existing_values = registration if request.method == "PATCH" else None
    values = registration_values_from_payload(payload, existing_values)
    errors = validate_registration(values)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    updated_registration = update_registration(
        registration_id,
        registration_data_from_values(values),
    )

    return jsonify({"success": True, "registration": updated_registration})


@app.get("/carebot")
def carebot():
    return render_template(
        "carebot.html",
        group_id=request.args.get("group_id", "").strip(),
        line_user_id=request.args.get("line_user_id", "").strip(),
        carebot_payload=get_carebot_payload(),
    )


@app.route("/api/carebot/assessments", methods=["GET", "POST"])
def carebot_assessments_api():
    if request.method == "POST":
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"success": False, "error": "Expected JSON object"}), 400

        responses = payload.get("responses")
        assessment_type = normalize_registration_input(payload.get("type") or payload.get("assessment_type"))
        score = payload.get("score")
        if not isinstance(responses, dict):
            return jsonify({"success": False, "error": "responses must be an object"}), 400
        if assessment_type not in {"PHQ-2", "PHQ-9"}:
            return jsonify({"success": False, "error": "assessment type must be PHQ-2 or PHQ-9"}), 400

        try:
            score = int(score)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "score must be a number"}), 400

        assessment_id = save_carebot_assessment(
            {
                "group_id": normalize_registration_input(payload.get("group_id")) or None,
                "line_user_id": normalize_registration_input(payload.get("line_user_id")) or None,
                "assessment_type": assessment_type,
                "score": score,
                "responses": responses,
            }
        )
        return jsonify({"success": True, "assessment_id": assessment_id}), 201

    group_id = request.args.get("group_id", "").strip() or None
    return jsonify({"assessments": list_carebot_assessments(group_id)})


@app.post("/api/carebot/chat")
def carebot_chat_api():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"success": False, "error": "Expected JSON object"}), 400

    message = normalize_registration_input(payload.get("message"))
    history = payload.get("history") if isinstance(payload.get("history"), list) else []
    context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
    if not message:
        return jsonify({"success": False, "error": "message is required"}), 400

    try:
        response_text = generate_carebot_reply(message, history, context)
    except CareBotError as error:
        return jsonify({"success": False, "error": str(error)}), 502

    return jsonify({"success": True, "response": response_text})


@app.get("/symptom-chat")
def symptom_chat():
    return render_template(
        "symptom_chat.html",
        group_id=request.args.get("group_id", "").strip(),
        line_user_id=request.args.get("line_user_id", "").strip(),
    )


@app.get("/api/symptom-chat/health")
def symptom_chat_health_api():
    symptom_engine = get_symptom_engine()
    return jsonify(
        {
            "ok": True,
            "db": str(symptom_engine.db.db_path),
            "llm_status": symptom_engine.llm.status(),
            "groups_loaded": len(symptom_engine.corpus.groups),
        }
    )


@app.get("/api/symptom-chat/bootstrap")
def symptom_chat_bootstrap_api():
    user_id = request.args.get("user_id") or request.args.get("line_user_id") or "U_DEMO"
    symptom_engine = get_symptom_engine()
    user = symptom_engine.db.get_or_create_user(user_id)
    session = symptom_engine.db.get_or_start_session(user_id)

    return jsonify(
        {
            "user": decode_symptom_user(user),
            "session": decode_symptom_session(session),
            "alerts": symptom_engine.db.alerts_for_user(user_id),
            "llm": symptom_engine.llm.status(),
            "groups_loaded": len(symptom_engine.corpus.groups),
        }
    )


@app.get("/api/symptom-chat/memory")
def symptom_chat_memory_api():
    user_id = request.args.get("user_id") or request.args.get("line_user_id") or "U_DEMO"
    symptom_engine = get_symptom_engine()
    session = symptom_engine.db.get_or_start_session(user_id)

    return jsonify(
        {
            "previous_sessions": symptom_engine.db.previous_summaries(user_id, limit=10),
            "recent_chat": symptom_engine.db.recent_chat(session["session_id"], limit=30),
            "alerts": symptom_engine.db.alerts_for_user(user_id, limit=20),
            "llm_stats": symptom_engine.db.llm_stats(session["session_id"]),
        }
    )


@app.post("/api/symptom-chat/users")
def symptom_chat_users_api():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id") or "U_DEMO"
    config = payload.get("config") or {"daily_summary": True, "line_simulation": True}
    symptom_engine = get_symptom_engine()
    user = symptom_engine.db.update_user(
        user_id=user_id,
        display_name=payload.get("display_name") or user_id,
        caregiver_user_id=payload.get("caregiver_user_id") or "",
        consent_to_share=bool(payload.get("consent_to_share", True)),
        personalized_prompt=payload.get("personalized_prompt") or "",
        config_json=config,
    )

    return jsonify({"user": decode_symptom_user(user)})


@app.post("/api/symptom-chat/chat")
def symptom_chat_api():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id") or payload.get("line_user_id") or "U_DEMO"
    symptom_engine = get_symptom_engine()
    result = symptom_engine.handle_message(
        user_id=user_id,
        text=payload.get("text") or "",
        session_mode=payload.get("session_mode") or "self_checkin",
        user_can_chat=bool(payload.get("user_can_chat", True)),
        raw_payload={"channel": "web", "payload": payload},
    )

    return jsonify(result)


@app.post("/api/symptom-chat/reset")
def symptom_chat_reset_api():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id") or payload.get("line_user_id") or "U_DEMO"
    symptom_engine = get_symptom_engine()
    result = symptom_engine.handle_message(
        user_id=user_id,
        text="/reset",
        raw_payload={"channel": "web", "payload": payload},
    )

    return jsonify(result)


@app.post("/save-assessment")
def legacy_save_assessment_api():
    payload = request.get_json(silent=True) or {}
    payload.setdefault("assessment_type", payload.get("type"))
    if "group_id" not in payload:
        payload["group_id"] = None
    if "line_user_id" not in payload:
        payload["line_user_id"] = None

    responses = payload.get("responses")
    assessment_type = normalize_registration_input(payload.get("type") or payload.get("assessment_type"))
    try:
        score = int(payload.get("score"))
    except (TypeError, ValueError):
        return jsonify({"detail": "score must be a number"}), 400

    if not isinstance(responses, dict):
        return jsonify({"detail": "responses must be an object"}), 400
    if assessment_type not in {"PHQ-2", "PHQ-9"}:
        return jsonify({"detail": "assessment type must be PHQ-2 or PHQ-9"}), 400

    save_carebot_assessment(
        {
            "group_id": normalize_registration_input(payload.get("group_id")) or None,
            "line_user_id": normalize_registration_input(payload.get("line_user_id")) or None,
            "assessment_type": assessment_type,
            "score": score,
            "responses": responses,
        }
    )
    return jsonify({"status": "success", "message": "Assessment saved successfully"})


@app.get("/results")
def legacy_carebot_results_api():
    return jsonify(list_carebot_assessments())


@app.post("/chat")
def legacy_carebot_chat_api():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"detail": "Expected JSON object"}), 400

    message = normalize_registration_input(payload.get("message"))
    history = payload.get("history") if isinstance(payload.get("history"), list) else []
    context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
    if not message:
        return jsonify({"detail": "message is required"}), 400

    try:
        response_text = generate_carebot_reply(message, history, context)
    except CareBotError as error:
        return jsonify({"detail": str(error)}), 502

    return jsonify({"response": response_text})


@app.route("/medicines", methods=["GET", "POST"])
def medicines():
    if request.method == "GET":
        group_id = request.args.get("group_id", "").strip()
        if not group_id:
            abort(400, "Missing group_id")

        return render_template(
            "medicine_register.html",
            group_id=group_id,
            errors=[],
            items=[empty_medicine_item()],
        )

    group_id = request.form.get("group_id", "").strip()
    items, errors = parse_medicine_items(request)

    if not group_id:
        errors.append("Missing group_id")

    if errors:
        return render_template(
            "medicine_register.html",
            group_id=group_id,
            errors=errors,
            items=items or [empty_medicine_item()],
        ), 400

    interaction_reports = []
    for item in items:
        report = check_interactions(item["medicine_name"], group_id)
        if "คำเตือน" in report:
            interaction_reports.append({"medicine": item["medicine_name"], "report": report})

    saved_items = []
    files = request.files.getlist("medicine_image[]")
    for index, item in enumerate(items):
        image_file = files[index] if index < len(files) else None
        image_path = save_uploaded_medicine_image(image_file)
        item["image_path"] = image_path
        saved_items.append(item)

    medicine_ids = save_medicine_items(group_id, saved_items)

    return render_template(
        "medicine_success.html",
        count=len(medicine_ids),
        group_id=group_id,
        interaction_reports=interaction_reports,
    )


@app.get("/medicines/success")
def medicines_success():
    count = int(request.args.get("count", "0"))
    group_id = request.args.get("group_id", "").strip()
    return render_template("medicine_success.html", count=count, group_id=group_id)


@app.route("/api/medicines", methods=["GET", "POST"])
def medicines_api():
    if request.method == "POST":
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"success": False, "error": "Expected JSON object"}), 400

        group_id = normalize_registration_input(payload.get("group_id"))
        item = medicine_item_from_payload(payload)
        errors = validate_medicine_payload(group_id, item)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        interaction_report = check_interactions(item["medicine_name"], group_id)
        medicine_id = save_medicine_item(group_id, item)
        return jsonify({"success": True, "medicine_id": medicine_id, "interaction_report": interaction_report}), 201

    group_id = request.args.get("group_id", "").strip() or None
    return jsonify({"medicines": list_medicines(group_id)})


@app.delete("/api/medicines/<int:medicine_id>")
def medicine_delete_api(medicine_id):
    group_id = request.args.get("group_id", "").strip() or None
    if not delete_medicine(medicine_id, group_id=group_id):
        return jsonify({"success": False, "error": "Medicine not found"}), 404

    return jsonify({"success": True, "deleted_id": medicine_id})


@app.get("/api/medicine-alerts/schedule")
def medicine_alert_schedule_api():
    group_id = request.args.get("group_id", "").strip() or None
    return jsonify({"schedule": build_medicine_alert_schedule(group_id)})


@app.get("/api/medicine-alerts/due")
def medicine_alert_due_api():
    group_id = request.args.get("group_id", "").strip() or None
    now = request.args.get("now", "").strip() or None
    window_minutes = request.args.get("window_minutes", "").strip() or None

    try:
        window_minutes = int(window_minutes) if window_minutes else None
        alerts = collect_due_medicine_alerts(group_id=group_id, at=now, window_minutes=window_minutes)
    except (TypeError, ValueError) as error:
        return jsonify({"success": False, "error": str(error)}), 400

    return jsonify({"success": True, "alerts": alerts})


@app.post("/api/medicine-alerts/run")
def medicine_alert_run_api():
    payload = request.get_json(silent=True) or {}
    group_id = normalize_registration_input(payload.get("group_id") or request.args.get("group_id")) or None
    now = normalize_registration_input(payload.get("now") or request.args.get("now")) or None
    window_minutes = payload.get("window_minutes") or request.args.get("window_minutes")
    dry_run = truthy(payload.get("dry_run") if "dry_run" in payload else request.args.get("dry_run"))

    try:
        window_minutes = int(window_minutes) if window_minutes else None
        result = run_medicine_alerts(
            line_bot_api,
            group_id=group_id,
            at=now,
            window_minutes=window_minutes,
            dry_run=dry_run,
        )
    except (TypeError, ValueError) as error:
        return jsonify({"success": False, "error": str(error)}), 400

    return jsonify(result)


@app.get("/api/medicine-alerts/logs")
def medicine_alert_logs_api():
    group_id = request.args.get("group_id", "").strip() or None
    limit = request.args.get("limit", "50").strip() or "50"

    try:
        limit = int(limit)
    except ValueError:
        limit = 50

    return jsonify({"logs": recent_medicine_alert_logs(group_id=group_id, limit=limit)})


@app.get("/api/medicine-alerts/action-logs")
def medicine_alert_action_logs_api():
    group_id = request.args.get("group_id", "").strip() or None
    limit = request.args.get("limit", "50").strip() or "50"

    try:
        limit = int(limit)
    except ValueError:
        limit = 50

    return jsonify({"logs": list_medicine_alert_action_logs(group_id=group_id, limit=limit)})


@app.post("/api/health-ocr")
def health_ocr_api():
    group_id = request.form.get("group_id", "").strip()
    image_file = request.files.get("file")

    if not group_id:
        return jsonify({"success": False, "error": "Missing group_id"}), 400

    if not image_file or not image_file.filename:
        return jsonify({"success": False, "error": "Missing file"}), 400

    if not allowed_image_file(image_file.filename):
        return jsonify({"success": False, "error": "Unsupported image file"}), 400

    image_bytes = image_file.read()
    if not image_bytes:
        return jsonify({"success": False, "error": "Empty file"}), 400

    original_filename = secure_filename(image_file.filename) or "health-image.jpg"
    mimetype = image_file.mimetype or "application/octet-stream"
    image_file.stream.seek(0)
    image_path = save_uploaded_medicine_image(image_file)
    stored_image_path = static_url_to_disk_path(image_path)

    try:
        result, ocr_source = perform_health_ocr(
            stored_image_path,
            image_bytes,
            original_filename,
            mimetype,
            group_id=group_id,
        )
    except OCRServiceError as error:
        payload = {"success": False, "error": error.message}
        if error.details:
            payload["details"] = error.details
        return jsonify(payload), error.status_code

    ocr_result_id = save_ocr_result(group_id, result, image_path)

    return jsonify(
        {
            "success": True,
            "ocr_result_id": ocr_result_id,
            "image_path": image_path,
            "ocr_source": ocr_source,
            "result": result,
        }
    )


@app.get("/api/ocr-results")
def ocr_results_api():
    group_id = request.args.get("group_id", "").strip() or None
    return jsonify({"ocr_results": list_ocr_results(group_id)})


def medicine_item_from_payload(payload):
    return {
        "medicine_name": normalize_registration_input(payload.get("medicine_name")),
        "dosage": normalize_registration_input(payload.get("dosage")),
        "take_time": normalize_registration_input(payload.get("take_time")),
        "instruction": normalize_registration_input(payload.get("instruction")),
        "image_path": normalize_registration_input(payload.get("image_path")) or None,
    }


def validate_medicine_payload(group_id, item):
    errors = {}

    if not group_id:
        errors["group_id"] = "Missing group_id"

    if not item["medicine_name"]:
        errors["medicine_name"] = "กรุณากรอกชื่อยา"

    return errors


def empty_medicine_item():
    return {
        "medicine_name": "",
        "dosage": "",
        "take_time": "",
        "instruction": "",
    }


def parse_medicine_items(form_request):
    names = form_request.form.getlist("medicine_name[]")
    dosages = form_request.form.getlist("dosage[]")
    take_times = form_request.form.getlist("take_time[]")
    instructions = form_request.form.getlist("instruction[]")
    files = form_request.files.getlist("medicine_image[]")
    row_count = max(len(names), len(dosages), len(take_times), len(instructions), len(files), 1)
    items = []
    errors = []

    for index in range(row_count):
        item = {
            "medicine_name": get_list_value(names, index).strip(),
            "dosage": get_list_value(dosages, index).strip(),
            "take_time": get_list_value(take_times, index).strip(),
            "instruction": get_list_value(instructions, index).strip(),
        }
        image_file = files[index] if index < len(files) else None
        has_image = bool(image_file and image_file.filename)

        if not any(item.values()) and not has_image:
            continue

        if not item["medicine_name"]:
            errors.append(f"รายการที่ {index + 1}: กรุณากรอกชื่อยา")

        if has_image and not allowed_image_file(image_file.filename):
            errors.append(f"รายการที่ {index + 1}: รองรับเฉพาะไฟล์รูปภาพ")

        items.append(item)

    if not items:
        errors.append("กรุณาเพิ่มรายการยาอย่างน้อย 1 รายการ")

    return items, errors


def get_list_value(values, index):
    return values[index] if index < len(values) else ""


def allowed_image_file(filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return extension in {"jpg", "jpeg", "png", "webp", "gif", "heic", "heif"}


def save_uploaded_medicine_image(image_file):
    if not image_file or not image_file.filename:
        return None

    if not allowed_image_file(image_file.filename):
        return None

    filename = secure_filename(image_file.filename)
    extension = filename.rsplit(".", 1)[-1].lower()
    stored_filename = f"{uuid4().hex}.{extension}"
    relative_folder = os.path.join("uploads", "medicines")
    upload_folder = os.path.join(UPLOAD_FOLDER, "medicines")
    os.makedirs(upload_folder, exist_ok=True)

    image_file.save(os.path.join(upload_folder, stored_filename))

    return f"/static/{relative_folder.replace(os.sep, '/')}/{stored_filename}"


def static_url_to_disk_path(static_url):
    if not static_url or not static_url.startswith("/static/"):
        return None

    relative_path = static_url.replace("/static/", "", 1)
    return os.path.join(app.static_folder, relative_path)


def registration_values_from_payload(payload, existing=None):
    values = {}
    fields = [
        "group_id",
        "line_user_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "gender",
        "role",
        "height_cm",
        "weight_kg",
    ]

    for field in fields:
        if field in payload:
            values[field] = normalize_registration_input(payload.get(field))
        elif existing:
            values[field] = normalize_registration_input(existing.get(field))
        else:
            values[field] = ""

    return values


def normalize_registration_input(value):
    if value is None:
        return ""

    return str(value).strip()


def truthy(value):
    if isinstance(value, bool):
        return value

    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def registration_data_from_values(values):
    return {
        "group_id": values["group_id"],
        "line_user_id": values["line_user_id"] or None,
        "first_name": values["first_name"],
        "last_name": values["last_name"],
        "email": values["email"],
        "phone": values["phone"],
        "gender": values["gender"],
        "role": values["role"],
        "height_cm": to_float_or_none(values["height_cm"]),
        "weight_kg": to_float_or_none(values["weight_kg"]),
    }


def validate_registration(values):
    errors = {}
    required_fields = [
        "group_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "gender",
        "role",
    ]

    for field in required_fields:
        if not values[field]:
            errors[field] = "จำเป็นต้องกรอกข้อมูลนี้"

    if values["email"] and "@" not in values["email"]:
        errors["email"] = "รูปแบบ email ไม่ถูกต้อง"

    if values["role"] not in {"patient", "caregiver"}:
        errors["role"] = "กรุณาเลือก role"

    if values["role"] == "patient":
        if not values["height_cm"]:
            errors["height_cm"] = "กรุณากรอกส่วนสูง"
        elif to_float_or_none(values["height_cm"]) is None:
            errors["height_cm"] = "ส่วนสูงต้องเป็นตัวเลข"

        if not values["weight_kg"]:
            errors["weight_kg"] = "กรุณากรอกน้ำหนัก"
        elif to_float_or_none(values["weight_kg"]) is None:
            errors["weight_kg"] = "น้ำหนักต้องเป็นตัวเลข"

    return errors


def to_float_or_none(value):
    if value in (None, ""):
        return None

    try:
        return float(value)
    except ValueError:
        return None


def build_register_url(group_id, line_user_id=None):
    base_url = PUBLIC_BASE_URL or request.url_root.strip("/")
    params = {"group_id": group_id}
    if line_user_id:
        params["line_user_id"] = line_user_id

    return f"{base_url}/register?{urlencode(params)}"


def build_medicine_url(group_id):
    base_url = PUBLIC_BASE_URL or request.url_root.strip("/")

    return f"{base_url}/medicines?{urlencode({'group_id': group_id})}"


def build_carebot_url(group_id=None, line_user_id=None):
    base_url = PUBLIC_BASE_URL or request.url_root.strip("/")
    params = {}
    if group_id:
        params["group_id"] = group_id
    if line_user_id:
        params["line_user_id"] = line_user_id

    query = f"?{urlencode(params)}" if params else ""
    return f"{base_url}/carebot{query}"


def build_symptom_chat_url(group_id=None, line_user_id=None):
    base_url = PUBLIC_BASE_URL or request.url_root.strip("/")
    params = {}
    if group_id:
        params["group_id"] = group_id
    if line_user_id:
        params["line_user_id"] = line_user_id

    query = f"?{urlencode(params)}" if params else ""
    return f"{base_url}/symptom-chat{query}"


def get_source_group_id(source):
    return getattr(source, "group_id", None) or getattr(source, "room_id", None)


def is_register_postback(postback_data):
    try:
        payload = json.loads(postback_data)
    except (TypeError, json.JSONDecodeError):
        return postback_data in {"register", "feature=register"}

    return payload.get("data") == "register" or payload.get("feature") == "register"


def get_postback_feature(postback_data):
    try:
        payload = json.loads(postback_data)
    except (TypeError, json.JSONDecodeError):
        if isinstance(postback_data, str) and postback_data.startswith("feature="):
            return postback_data.split("=", 1)[1]
        return None

    return payload.get("feature")


def get_postback_json(postback_data):
    try:
        payload = json.loads(postback_data)
    except (TypeError, json.JSONDecodeError):
        return {}

    return payload if isinstance(payload, dict) else {}


def get_source_type(source):
    return getattr(source, "type", None) or ""


def get_source_id(source):
    return (
        getattr(source, "group_id", None)
        or getattr(source, "room_id", None)
        or getattr(source, "user_id", None)
        or ""
    )


def build_feature_reply(postback_data):
    feature = get_postback_feature(postback_data)
    replies = {
        "health_ocr": "ส่งรูปฉลากยา หน้าจอวัดความดัน หน้าจอวัดน้ำตาล อาหาร หรือใบนัดหมอมาในแชทนี้ได้เลยครับ เดี๋ยวผมจะส่งรูปไปวิเคราะห์ผ่าน MedGuard AI",
        "medicine_management": "เมนูจัดการยาจะใช้สำหรับดู เพิ่ม และลบรายการยาที่คนไข้ใช้ปัจจุบันครับ",
        "membership_required": "รบกวนจัดการสมาชิกในกลุ่มก่อนนะค้าบบบ",
    }

    return replies.get(feature)


def group_has_registered_members(group_id):
    return bool(group_id and list_registrations(group_id))

###########################
# TODO USER MESSAGE HANDLER

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


###########################
# TODO JOIN EVENT
@handler.add(JoinEvent)
def join_event(event):
    group_id = event.source.group_id
    print(group_id)
    # reply_token = event.reply_token
    register_url = build_register_url(group_id) if group_id else None
    medicine_url = build_medicine_url(group_id) if group_id else None
    carebot_url = build_carebot_url(group_id) if group_id else None
    symptom_chat_url = build_symptom_chat_url(group_id) if group_id else None
    has_registered_members = group_has_registered_members(group_id)
    flex_message = FlexSendMessage(
        alt_text="น้องพิล features",
        contents=features_carousel_flex(
            register_url,
            medicine_url,
            carebot_url,
            symptom_chat_url,
            medguard_locked=not has_registered_members,
            carebot_locked=not has_registered_members,
            symptom_chat_locked=not has_registered_members,
        ),
    )
    print(flex_message)
    msg = TextSendMessage("หวัดดีค้าบบ! 👋 ผมเป็น AI ผมเป็นผู้ช่วยเล็กๆ ที่จะมาคอยส่งข้อความเตือนเรื่องยาให้เป็นระยะ ต้องการให้ผมช่วยอะไร เรียกผมได้เลยครับ ผมช่วยคุณเองไม่ต้องห่วงงง 💊😆")
    line_bot_api.push_message(to=group_id, messages=msg)
    line_bot_api.push_message(to=group_id, messages=flex_message)
    

###########################
# TODO Message Handler
@handler.add(MessageEvent, message=[TextMessage,ImageMessage])
def handle_message(event):
    if isinstance(event.message, TextMessage):
        message_text = event.message.text.strip()
        normalized_text = message_text.lower()

        if message_text == "น้องพิล":
            line_bot_api.reply_message(
                event.reply_token,
                messages=TextSendMessage(
                    text=(
                        "น้องพิลมาแล้วค้าบ เรียกใช้งานด้วย keyword เหล่านี้ได้เลย\n\n"
                        "• จัดการสมาชิก - เพิ่ม/แก้ไขข้อมูลสมาชิกในกลุ่ม\n"
                        "• MedGuard AI - วิเคราะห์รูปสุขภาพและจัดการยา\n"
                        "• CareBot - ทำแบบประเมินสุขภาพจิต\n"
                        "• เช็กอาการ - เช็กอินอาการผิดปกติ"
                    )
                ),
            )
            return

        if normalized_text in {"medguard ai", "madguard ai", "medguard", "madguard"}:
            group_id = get_source_group_id(event.source)
            medicine_url = build_medicine_url(group_id) if group_id else None
            is_locked = not group_has_registered_members(group_id)
            flex_message = FlexSendMessage(
                alt_text="MedGuard AI",
                contents=medguard_ai_bubble(medicine_url, locked=is_locked),
            )
            intro_text = "MedGuard AI พร้อมช่วยดูรูปสุขภาพและรายการยาแล้วค้าบ"
            if is_locked:
                intro_text = "ก่อนใช้ MedGuard AI ขอจัดการสมาชิกในกลุ่มให้เรียบร้อยก่อนนะค้าบ"
            line_bot_api.reply_message(
                event.reply_token,
                messages=[
                    TextSendMessage(text=intro_text),
                    flex_message,
                ],
            )
            return

        if message_text == "จัดการสมาชิก":
            group_id = get_source_group_id(event.source)
            line_user_id = getattr(event.source, "user_id", None)
            register_url = build_register_url(group_id, line_user_id) if group_id else None
            flex_message = FlexSendMessage(
                alt_text="จัดการสมาชิก",
                contents=member_management_bubble(register_url),
            )
            line_bot_api.reply_message(
                event.reply_token,
                messages=[
                    TextSendMessage(text="ได้เลยค้าบ มาอัปเดตข้อมูลสมาชิกในกลุ่มกัน"),
                    flex_message,
                ],
            )
            return

        if normalized_text in {"chat-symtom", "chat-symptom", "symtom", "symptom", "เช็กอาการ", "เช็คอาการ"}:
            group_id = get_source_group_id(event.source)
            line_user_id = getattr(event.source, "user_id", None)
            symptom_chat_url = build_symptom_chat_url(group_id, line_user_id)
            is_locked = not group_has_registered_members(group_id)
            flex_message = FlexSendMessage(
                alt_text="Symptom Check-in",
                contents=symptom_chat_bubble(symptom_chat_url, locked=is_locked),
            )
            intro_text = "ได้เลยค้าบ มาเช็กอินอาการผิดปกติกัน"
            if is_locked:
                intro_text = "ก่อนเริ่มเช็กอาการ ขอจัดการสมาชิกในกลุ่มให้เรียบร้อยก่อนนะค้าบ"
            line_bot_api.reply_message(
                event.reply_token,
                messages=[
                    TextSendMessage(text=intro_text),
                    flex_message,
                ],
            )
            return

        if normalized_text in {"carebot", "cerebot", "แคร์บอท", "แคร์บอต"}:
            group_id = get_source_group_id(event.source)
            line_user_id = getattr(event.source, "user_id", None)
            carebot_url = build_carebot_url(group_id, line_user_id)
            is_locked = not group_has_registered_members(group_id)
            flex_message = FlexSendMessage(
                alt_text="CareBot Health",
                contents=carebot_bubble(carebot_url, locked=is_locked),
            )
            intro_text = "CareBot มาแล้วค้าบ ค่อย ๆ เช็กใจไปด้วยกันนะ"
            if is_locked:
                intro_text = "ก่อนเริ่ม CareBot ขอจัดการสมาชิกในกลุ่มให้เรียบร้อยก่อนนะค้าบ"
            line_bot_api.reply_message(
                event.reply_token,
                messages=[
                    TextSendMessage(text=intro_text),
                    flex_message,
                ],
            )
            return

    line_user_id = event.source.user_id
    profile = None
    while not profile:
        try:
            profile = line_bot_api.get_profile(line_user_id)
        except ConnectionError:
            time.sleep(1)
    print('uid: ',line_user_id)
    
@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    timestamp = event.timestamp
    event_type = event.type
    postback_data = event.postback.data
    postback_payload = get_postback_json(postback_data)
    if postback_payload.get("feature") == "medicine_alert" and postback_payload.get("action") == "taken":
        action_log_id = record_medicine_alert_action(
            {
                "alert_log_id": postback_payload.get("alert_log_id"),
                "group_id": get_source_group_id(event.source),
                "medicine_id": postback_payload.get("medicine_id"),
                "action": "taken",
                "line_user_id": user_id,
                "source_type": get_source_type(event.source),
                "source_id": get_source_id(event.source),
                "raw_payload": {
                    "postback": postback_payload,
                    "timestamp": timestamp,
                    "event_type": event_type,
                },
            }
        )
        line_bot_api.reply_message(
            event.reply_token,
            messages=TextSendMessage(text=f"บันทึกแล้วครับ กินยาแล้ว log #{action_log_id}"),
        )
        return

    if is_register_postback(postback_data):
        group_id = get_source_group_id(event.source)
        if not group_id:
            line_bot_api.reply_message(
                event.reply_token,
                messages=TextSendMessage(text="กรุณากดลงทะเบียนจากใน LINE group นะครับ"),
            )
            return

        register_url = build_register_url(group_id, user_id)
        line_bot_api.reply_message(
            event.reply_token,
            messages=TextSendMessage(text=f"กดลิงก์นี้เพื่อจัดการสมาชิกได้เลยค้าบ\n{register_url}"),
        )
        return

    if get_postback_feature(postback_data) == "membership_required":
        group_id = get_source_group_id(event.source)
        if group_has_registered_members(group_id):
            medicine_url = build_medicine_url(group_id)
            flex_message = FlexSendMessage(
                alt_text="MedGuard AI",
                contents=medguard_ai_bubble(medicine_url),
            )
            line_bot_api.reply_message(
                event.reply_token,
                messages=[
                    TextSendMessage(text="เจอสมาชิกในกลุ่มแล้วค้าบ เปิด MedGuard AI ให้เลยนะ"),
                    flex_message,
                ],
            )
            return

        line_bot_api.reply_message(
            event.reply_token,
            messages=TextSendMessage(text="รบกวนจัดการสมาชิกในกลุ่มก่อนนะค้าบบบ"),
        )
        return

    if get_postback_feature(postback_data) == "carebot_membership_required":
        group_id = get_source_group_id(event.source)
        if group_has_registered_members(group_id):
            carebot_url = build_carebot_url(group_id, user_id)
            flex_message = FlexSendMessage(
                alt_text="CareBot Health",
                contents=carebot_bubble(carebot_url),
            )
            line_bot_api.reply_message(
                event.reply_token,
                messages=[
                    TextSendMessage(text="เจอสมาชิกในกลุ่มแล้วค้าบ เปิด CareBot ให้เลยนะ"),
                    flex_message,
                ],
            )
            return

        line_bot_api.reply_message(
            event.reply_token,
            messages=TextSendMessage(text="รบกวนจัดการสมาชิกในกลุ่มก่อนนะค้าบบบ"),
        )
        return

    if get_postback_feature(postback_data) == "symptom_chat_membership_required":
        group_id = get_source_group_id(event.source)
        if group_has_registered_members(group_id):
            symptom_chat_url = build_symptom_chat_url(group_id, user_id)
            flex_message = FlexSendMessage(
                alt_text="Symptom Check-in",
                contents=symptom_chat_bubble(symptom_chat_url),
            )
            line_bot_api.reply_message(
                event.reply_token,
                messages=[
                    TextSendMessage(text="เจอสมาชิกในกลุ่มแล้วค้าบ เปิด Symptom Check-in ให้เลยนะ"),
                    flex_message,
                ],
            )
            return

        line_bot_api.reply_message(
            event.reply_token,
            messages=TextSendMessage(text="รบกวนจัดการสมาชิกในกลุ่มก่อนนะค้าบบบ"),
        )
        return

    feature_reply = build_feature_reply(postback_data)
    if feature_reply:
        line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=feature_reply))
        return

    print(user_id)
    print(postback_data)
