import json


def member_management_bubble(register_url=None):
    action = {
        "type": "postback",
        "label": "จัดการสมาชิก",
        "data": "{\"data\": \"register\"}",
    }

    if register_url:
        action = {
            "type": "uri",
            "label": "จัดการสมาชิก",
            "uri": register_url,
        }

    return {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://lh3.googleusercontent.com/d/1K8nP9rEhErEhCF48pHkqo0N_E9tFhIg-",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": action,
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "จัดการสมาชิกกลุ่ม",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#14301f",
                },
                {
                    "type": "text",
                    "text": "ดูแลข้อมูล Patient และ Caregiver ของกลุ่มนี้",
                    "size": "sm",
                    "wrap": True,
                    "color": "#5b725f",
                },
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "color": "#55b82e",
                    "action": action,
                },
            ],
        },
    }


def register_flex(register_url=None):
    return member_management_bubble(register_url)


def features_bubbles(
    register_url=None,
    medicine_url=None,
    carebot_url=None,
    symptom_chat_url=None,
    medguard_locked=False,
    carebot_locked=False,
    symptom_chat_locked=False,
):
    return [
        member_management_bubble(register_url),
        medguard_ai_bubble(medicine_url, locked=medguard_locked),
        carebot_bubble(carebot_url, locked=carebot_locked),
        symptom_chat_bubble(symptom_chat_url, locked=symptom_chat_locked),
    ]


def features_carousel_flex(
    register_url=None,
    medicine_url=None,
    carebot_url=None,
    symptom_chat_url=None,
    medguard_locked=False,
    carebot_locked=False,
    symptom_chat_locked=False,
):
    return {
        "type": "carousel",
        "contents": features_bubbles(
            register_url,
            medicine_url,
            carebot_url,
            symptom_chat_url,
            medguard_locked,
            carebot_locked,
            symptom_chat_locked,
        ),
    }


def medguard_ai_bubble(medicine_url=None, locked=False):
    medicine_action = {
        "type": "postback",
        "label": "ใช้งาน Madguard AI",
        "data": "feature=medicine_management",
    }
    button_color = "#55b82e"
    hero_color = "#0f8f8c"
    description = "ส่งรูปสุขภาพให้ AI วิเคราะห์อัตโนมัติ และจัดการรายการยาที่ใช้ประจำ"

    if locked:
        medicine_action = {
            "type": "postback",
            "label": "จัดการสมาชิกก่อน",
            "data": "feature=membership_required",
        }
        button_color = "#9aa8a0"
        hero_color = "#7d8b83"
        description = "กรุณาจัดการข้อมูลสมาชิกในกลุ่มก่อน แล้วค่อยใช้งาน MedGuard AI"
    elif medicine_url:
        medicine_action = {
            "type": "uri",
            "label": "ใช้งาน Madguard AI",
            "uri": medicine_url,
        }

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "paddingAll": "20px",
            "backgroundColor": "#f7fdf1",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "height": "72px",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "backgroundColor": hero_color,
                    "cornerRadius": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "Madguard AI 🛡️",
                            "size": "xxl",
                            "align": "center",
                            "color": "#ffffff"
                        }
                    ],
                },
                {
                    "type": "text",
                    "text": "MedGuard AI",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#14301f",
                    "wrap": True,
                },
                {
                    "type": "text",
                    "text": description,
                    "size": "sm",
                    "color": "#5b725f",
                    "wrap": True,
                },
                {
                    "type": "separator",
                    "color": "#d8ead3",
                },
                feature_row(
                    "Universal Health OCR",
                    "ฉลากยา, ความดัน, น้ำตาล, อาหาร, ใบนัดหมอ",
                    "#0f8f8c",
                ),
                feature_row(
                    "Medicine Management",
                    "ดู เพิ่ม และลบรายการยาปัจจุบัน",
                    "#55b82e",
                ),
                feature_row(
                    "Thai Interpretation",
                    "สรุปผลและรายงานความเสี่ยงภาษาไทย",
                    "#3267b7",
                ),
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "color": button_color,
                    "action": medicine_action,
                },
            ],
        },
    }


def medguard_features_bubble(medicine_url=None, locked=False):
    return medguard_ai_bubble(medicine_url, locked)


def carebot_bubble(carebot_url=None, locked=False):
    action = {
        "type": "postback",
        "label": "เริ่มประเมินใจ",
        "data": "feature=carebot",
    }
    button_color = "#55b82e"
    hero_color = "#0f8f8c"
    description = "แบบประเมินสุขภาพจิต PHQ-9 พร้อมสรุปผลและพื้นที่คุยต่ออย่างอ่อนโยน"

    if locked:
        action = {
            "type": "postback",
            "label": "จัดการสมาชิกก่อน",
            "data": "feature=carebot_membership_required",
        }
        button_color = "#9aa8a0"
        hero_color = "#7d8b83"
        description = "กรุณาจัดการข้อมูลสมาชิกในกลุ่มก่อน แล้วค่อยใช้งาน CareBot"
    elif carebot_url:
        action = {
            "type": "uri",
            "label": "เริ่มประเมินใจ",
            "uri": carebot_url,
        }

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "paddingAll": "20px",
            "backgroundColor": "#f7fdf1",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "height": "72px",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "backgroundColor": hero_color,
                    "cornerRadius": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "แบบประเมินใจ ❤️",
                            "size": "xxl",
                            "weight": "bold",
                            "color": "#ffffff",
                            "align": "center",
                        }
                    ],
                },
                {
                    "type": "text",
                    "text": "CareBot Health",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#14301f",
                    "wrap": True,
                },
                {
                    "type": "text",
                    "text": description,
                    "size": "sm",
                    "color": "#5b725f",
                    "wrap": True,
                },
                {
                    "type": "separator",
                    "color": "#d8ead3",
                },
                feature_row(
                    "PHQ-2 / PHQ-9",
                    "เริ่มคัดกรองทีละข้อ ใช้เวลาไม่นาน",
                    "#0f8f8c",
                ),
                feature_row(
                    "Assessment Result",
                    "สรุปคะแนนและระดับอาการให้อ่านง่าย",
                    "#55b82e",
                ),
                feature_row(
                    "CareBot Chat",
                    "คุยต่อเพื่อรับคำแนะนำเบื้องต้นหลังประเมิน",
                    "#3267b7",
                ),
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "color": button_color,
                    "action": action,
                },
            ],
        },
    }


def cerebot_bubble(carebot_url=None, locked=False):
    return carebot_bubble(carebot_url, locked)


def symptom_chat_bubble(symptom_chat_url=None, locked=False):
    action = {
        "type": "postback",
        "label": "เริ่มเช็กอาการ",
        "data": "feature=symptom_chat",
    }
    button_color = "#55b82e"
    hero_color = "#0f8f8c"
    description = "เช็กอินอาการผิดปกติ คัดกรองความเสี่ยงเบื้องต้น และจำลอง alert ให้ผู้ดูแล"

    if locked:
        action = {
            "type": "postback",
            "label": "จัดการสมาชิกก่อน",
            "data": "feature=symptom_chat_membership_required",
        }
        button_color = "#9aa8a0"
        hero_color = "#7d8b83"
        description = "กรุณาจัดการข้อมูลสมาชิกในกลุ่มก่อน แล้วค่อยใช้งาน Symptom Check-in"
    elif symptom_chat_url:
        action = {
            "type": "uri",
            "label": "เริ่มเช็กอาการ",
            "uri": symptom_chat_url,
        }

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "paddingAll": "20px",
            "backgroundColor": "#f7fdf1",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "height": "72px",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "backgroundColor": hero_color,
                    "cornerRadius": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "เช็กอาการ",
                            "size": "xxl",
                            "weight": "bold",
                            "color": "#ffffff",
                            "align": "center",
                        }
                    ],
                },
                {
                    "type": "text",
                    "text": "Symptom Check-in",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#14301f",
                    "wrap": True,
                },
                {
                    "type": "text",
                    "text": description,
                    "size": "sm",
                    "color": "#5b725f",
                    "wrap": True,
                },
                {
                    "type": "separator",
                    "color": "#d8ead3",
                },
                feature_row(
                    "EMS Screening",
                    "เลือกกลุ่มอาการจากชุดความรู้ EMS",
                    "#0f8f8c",
                ),
                feature_row(
                    "Risk Level",
                    "สรุป green, yellow, red จากคำตอบ",
                    "#55b82e",
                ),
                feature_row(
                    "Caregiver Alert",
                    "จำลองการแจ้งเตือนผู้ดูแลเมื่อพบความเสี่ยง",
                    "#3267b7",
                ),
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "color": button_color,
                    "action": action,
                },
            ],
        },
    }


def chat_symtom_bubble(symptom_chat_url=None, locked=False):
    return symptom_chat_bubble(symptom_chat_url, locked)


def medicine_alert_bubble(alert, alert_log_id=None):
    patient_names = names_or_fallback(alert.get("patients"), "ยังไม่มีข้อมูล Patient")
    caregiver_names = names_or_fallback(alert.get("caregivers"), "ยังไม่มีข้อมูล Caregiver")
    dosage = alert.get("dosage") or "-"
    scheduled_time = alert.get("scheduled_time") or alert.get("time") or "-"
    slot_label = alert.get("slot_label") or "ถึงเวลากินยา"
    mode_label = "TEST MODE" if alert.get("test_mode") else "MEDICINE ALERT"
    action_payload = {
        "feature": "medicine_alert",
        "action": "taken",
        "alert_log_id": alert_log_id,
        "medicine_id": alert.get("medicine_id"),
    }

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "paddingAll": "20px",
            "backgroundColor": "#f7fdf1",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "height": "66px",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "backgroundColor": "#0f8f8c",
                    "cornerRadius": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "แจ้งเตือนกินยา",
                            "size": "xl",
                            "weight": "bold",
                            "align": "center",
                            "color": "#ffffff",
                        },
                        {
                            "type": "text",
                            "text": mode_label,
                            "size": "xs",
                            "align": "center",
                            "color": "#d9fffb",
                        },
                    ],
                },
                {
                    "type": "text",
                    "text": alert.get("medicine_name") or "รายการยา",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#14301f",
                    "wrap": True,
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        medicine_alert_fact("เวลา", f"{slot_label} ({scheduled_time})", 2),
                        medicine_alert_fact("ขนาด", dosage, 1),
                    ],
                },
                {
                    "type": "separator",
                    "color": "#d8ead3",
                },
                medicine_alert_line("ผู้ป่วย", patient_names),
                medicine_alert_line("ผู้ดูแล", caregiver_names),
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "color": "#55b82e",
                    "action": {
                        "type": "postback",
                        "label": "กินแล้ว",
                        "data": json.dumps(action_payload, ensure_ascii=False, separators=(",", ":")),
                        "displayText": "กินยาแล้ว",
                    },
                },
            ],
        },
    }


def medicine_alert_fact(label, value, flex=1):
    return {
        "type": "box",
        "layout": "vertical",
        "flex": flex,
        "spacing": "xs",
        "paddingAll": "10px",
        "backgroundColor": "#e8faf8",
        "cornerRadius": "md",
        "contents": [
            {
                "type": "text",
                "text": label,
                "size": "xs",
                "weight": "bold",
                "color": "#0f8f8c",
            },
            {
                "type": "text",
                "text": value,
                "size": "sm",
                "weight": "bold",
                "color": "#14301f",
                "wrap": True,
            },
        ],
    }


def medicine_alert_line(label, value):
    return {
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "contents": [
            {
                "type": "text",
                "text": label,
                "size": "xs",
                "weight": "bold",
                "color": "#5b725f",
                "flex": 1,
            },
            {
                "type": "text",
                "text": value,
                "size": "xs",
                "color": "#14301f",
                "wrap": True,
                "flex": 3,
            },
        ],
    }


def names_or_fallback(members, fallback):
    names = [member["name"] for member in members or [] if member.get("name")]
    return ", ".join(names) if names else fallback


def appointment_alert_bubble(alert, alert_log_id=None):
    patient_names = names_or_fallback(alert.get("patients"), "ยังไม่มีข้อมูล Patient")
    scheduled_time = alert.get("appointment_display") or alert.get("scheduled_time") or "-"
    hospital = alert.get("hospital") or "โรงพยาบาล"
    department = alert.get("department") or "-"
    doctor = alert.get("doctor") or "-"
    preparation = alert.get("preparation") or "นำใบนัดและเอกสารที่เกี่ยวข้องไปด้วย"
    mode_label = "TEST MODE" if alert.get("test_mode") else "APPOINTMENT ALERT"
    action_payload = {
        "feature": "appointment_alert",
        "action": "acknowledged",
        "alert_log_id": alert_log_id,
        "appointment_id": alert.get("appointment_id"),
    }

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "paddingAll": "20px",
            "backgroundColor": "#f7fdf1",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "height": "66px",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "backgroundColor": "#3267b7",
                    "cornerRadius": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "แจ้งเตือนนัดหมาย",
                            "size": "xl",
                            "weight": "bold",
                            "align": "center",
                            "color": "#ffffff",
                        },
                        {
                            "type": "text",
                            "text": mode_label,
                            "size": "xs",
                            "align": "center",
                            "color": "#e7f0ff",
                        },
                    ],
                },
                {
                    "type": "text",
                    "text": hospital,
                    "weight": "bold",
                    "size": "xl",
                    "color": "#14301f",
                    "wrap": True,
                },
                medicine_alert_fact("วันเวลา", scheduled_time, 1),
                {
                    "type": "separator",
                    "color": "#d8ead3",
                },
                medicine_alert_line("ผู้ป่วย", patient_names),
                medicine_alert_line("แผนก", department),
                medicine_alert_line("แพทย์", doctor),
                medicine_alert_line("เตรียมตัว", preparation),
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "color": "#3267b7",
                    "action": {
                        "type": "postback",
                        "label": "รับทราบ",
                        "data": json.dumps(action_payload, ensure_ascii=False, separators=(",", ":")),
                        "displayText": "รับทราบนัดหมายแล้ว",
                    },
                },
            ],
        },
    }


def feature_row(title, description, color):
    return {
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "contents": [
            {
                "type": "text",
                "text": "●",
                "size": "sm",
                "color": color,
                "flex": 0,
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "size": "sm",
                        "color": "#14301f",
                        "wrap": True,
                    },
                    {
                        "type": "text",
                        "text": description,
                        "size": "xs",
                        "color": "#5b725f",
                        "wrap": True,
                    },
                ],
            },
        ],
    }
