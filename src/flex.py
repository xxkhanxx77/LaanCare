def register_flex(register_url=None):
    action = {
        "type": "postback",
        "label": "Register",
        "data": "{\"data\": \"register\"}",
    }

    if register_url:
        action = {
            "type": "uri",
            "label": "Register",
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
                    "text": "ลงทะเบียนสมาชิกกลุ่ม",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#14301f",
                },
                {
                    "type": "text",
                    "text": "เลือก Role เป็น Patient หรือ Caregiver เพื่อเริ่มใช้งาน",
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


def features_carousel_flex(register_url=None, medicine_url=None):
    return {
        "type": "carousel",
        "contents": [
            register_flex(register_url),
            medguard_features_bubble(medicine_url),
        ],
    }


def medguard_features_bubble(medicine_url=None):
    medicine_action = {
        "type": "postback",
        "label": "จัดการยา",
        "data": "feature=medicine_management",
    }

    if medicine_url:
        medicine_action = {
            "type": "uri",
            "label": "จัดการยา",
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
                    "backgroundColor": "#0f8f8c",
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
                    "text": "ส่งรูปสุขภาพให้ AI วิเคราะห์อัตโนมัติ และจัดการรายการยาที่ใช้ประจำ",
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
                    "color": "#0f8f8c",
                    "action": {
                        "type": "postback",
                        "label": "วิธีใช้ OCR",
                        "data": "feature=health_ocr",
                    },
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": medicine_action,
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
