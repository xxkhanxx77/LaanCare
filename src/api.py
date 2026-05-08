try:
    from .config import *
    from .flex import *
    from .storage import (
        delete_registration,
        get_registration,
        get_registration_by_line_user_id,
        list_medicines,
        list_registrations,
        save_medicine_items,
        save_registration,
        update_registration,
    )
except ImportError:
    from config import *
    from flex import *
    from storage import (
        delete_registration,
        get_registration,
        get_registration_by_line_user_id,
        list_medicines,
        list_registrations,
        save_medicine_items,
        save_registration,
        update_registration,
    )


import json
import os
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
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
line_bot_api = LineBotApi(channel_access_token=LINE_ACCESS_TOKEN, timeout=3)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route('/')
def home():
    return abort(404)


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

    saved_items = []
    files = request.files.getlist("medicine_image[]")
    for index, item in enumerate(items):
        image_file = files[index] if index < len(files) else None
        image_path = save_uploaded_medicine_image(image_file)
        item["image_path"] = image_path
        saved_items.append(item)

    medicine_ids = save_medicine_items(group_id, saved_items)

    return redirect(url_for("medicines_success", count=len(medicine_ids), group_id=group_id))


@app.get("/medicines/success")
def medicines_success():
    count = int(request.args.get("count", "0"))
    group_id = request.args.get("group_id", "").strip()
    return render_template("medicine_success.html", count=count, group_id=group_id)


@app.get("/api/medicines")
def medicines_api():
    group_id = request.args.get("group_id", "").strip() or None
    return jsonify({"medicines": list_medicines(group_id)})


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


def build_feature_reply(postback_data):
    feature = get_postback_feature(postback_data)
    replies = {
        "health_ocr": "ส่งรูปฉลากยา หน้าจอวัดความดัน หน้าจอวัดน้ำตาล อาหาร หรือใบนัดหมอมาในแชทนี้ได้เลยครับ เดี๋ยวผมจะส่งรูปไปวิเคราะห์ผ่าน MedGuard AI",
        "medicine_management": "เมนูจัดการยาจะใช้สำหรับดู เพิ่ม และลบรายการยาที่คนไข้ใช้ปัจจุบันครับ",
    }

    return replies.get(feature)

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
    flex_message = register_flex()
    flex_message = FlexSendMessage(alt_text="Group ID Information", contents=flex_message)
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

        if message_text == "น้องพิล":
            group_id = get_source_group_id(event.source)
            line_user_id = getattr(event.source, "user_id", None)
            register_url = build_register_url(group_id, line_user_id) if group_id else None
            medicine_url = build_medicine_url(group_id) if group_id else None
            flex_message = FlexSendMessage(
                alt_text="น้องพิล features",
                contents=features_carousel_flex(register_url, medicine_url),
            )
            line_bot_api.reply_message(event.reply_token, messages=flex_message)
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
    if is_register_postback(postback_data):
        group_id = get_source_group_id(event.source)
        if not group_id:
            line_bot_api.reply_message(
                event.reply_token,
                messages=TextSendMessage(text="กรุณากดลงทะเบียนจากใน LINE group นะครับ"),
            )
            return

        register_url = build_register_url(group_id, user_id)
        flex_message = FlexSendMessage(
            alt_text="Register",
            contents=register_flex(register_url),
        )
        line_bot_api.reply_message(event.reply_token, messages=flex_message)
        return

    feature_reply = build_feature_reply(postback_data)
    if feature_reply:
        line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=feature_reply))
        return

    print(user_id)
    print(postback_data)
