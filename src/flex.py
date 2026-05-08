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


def features_bubbles(register_url=None, medicine_url=None, medguard_locked=False):
    return [
        member_management_bubble(register_url),
        medguard_ai_bubble(medicine_url, locked=medguard_locked),
    ]


def features_carousel_flex(register_url=None, medicine_url=None, medguard_locked=False):
    return {
        "type": "carousel",
        "contents": features_bubbles(register_url, medicine_url, medguard_locked),
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
                            "text": "🛡️",
                            "size": "xxl",
                            "align": "center",
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
