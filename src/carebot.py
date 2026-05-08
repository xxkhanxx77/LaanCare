import os


ANSWER_OPTIONS = [
    {"label": "ไม่มีเลย", "value": 0},
    {"label": "มีบางวัน", "value": 1},
    {"label": "มีบ่อย (>7 วัน)", "value": 2},
    {"label": "มีทุกวัน", "value": 3},
]

PHQ2_QUESTIONS = [
    {
        "id": "q1",
        "text": "เบื่อ ทำอะไรก็ไม่เพลิดเพลิน",
        "options": ANSWER_OPTIONS,
    },
    {
        "id": "q2",
        "text": "ไม่สบายใจ ซึมเศร้า หรือท้อแท้",
        "options": ANSWER_OPTIONS,
    },
]

PHQ9_QUESTIONS = [
    *PHQ2_QUESTIONS,
    {
        "id": "q3",
        "text": "หลับยาก หรือหลับๆ ตื่นๆ หรือหลับมากไป",
        "options": ANSWER_OPTIONS,
    },
    {
        "id": "q4",
        "text": "เหนื่อยง่าย หรือไม่ค่อยมีแรง",
        "options": ANSWER_OPTIONS,
    },
    {
        "id": "q5",
        "text": "เบื่ออาหาร หรือกินมากเกินไป",
        "options": ANSWER_OPTIONS,
    },
    {
        "id": "q6",
        "text": "รู้สึกไม่ดีกับตัวเอง คิดว่าตัวเองล้มเหลว หรือทำให้ตนเองหรือครอบครัวผิดหวัง",
        "options": ANSWER_OPTIONS,
    },
    {
        "id": "q7",
        "text": "สมาธิไม่ดีเวลาทำอะไร เช่น ดูโทรทัศน์ หรือทำงานที่ต้องใช้ความตั้งใจ",
        "options": ANSWER_OPTIONS,
    },
    {
        "id": "q8",
        "text": "พูดหรือทำอะไรช้าจนคนอื่นสังเกตเห็นได้ หรือกระสับกระส่ายจนอยู่ไม่นิ่งเหมือนเคย",
        "options": ANSWER_OPTIONS,
    },
    {
        "id": "q9",
        "text": "คิดทำร้ายตนเอง หรือคิดว่าถ้าตายไปคงจะดี",
        "options": ANSWER_OPTIONS,
    },
]


class CareBotError(Exception):
    pass


def get_phq9_result(score):
    if score <= 4:
        return {
            "severity": "ไม่มีอาการของโรคซึมเศร้าหรือมีอาการในระดับน้อยมาก",
            "action": "ไม่ต้องทำอะไร",
        }
    if score <= 9:
        return {
            "severity": "มีอาการของโรคซึมเศร้าในระดับน้อย",
            "action": "ควรติดตามสังเกตอาการ และทำแบบทดสอบซ้ำในอีก 2-4 สัปดาห์",
        }
    if score <= 14:
        return {
            "severity": "มีอาการของโรคซึมเศร้าในระดับปานกลาง",
            "action": "ควรปรึกษาแพทย์หรือผู้เชี่ยวชาญเพื่อวางแผนการรักษา",
        }
    if score <= 19:
        return {
            "severity": "มีอาการของโรคซึมเศร้าในระดับค่อนข้างรุนแรง",
            "action": "ควรปรึกษาแพทย์เพื่อรับการรักษาด้วยยาและ/หรือจิตบำบัด",
        }

    return {
        "severity": "มีอาการของโรคซึมเศร้าในระดับรุนแรง",
        "action": "ควรปรึกษาแพทย์โดยด่วนเพื่อรับการรักษา",
    }


def get_carebot_payload():
    return {
        "phq2_questions": PHQ2_QUESTIONS,
        "phq9_questions": PHQ9_QUESTIONS,
    }


def generate_carebot_reply(message, history, context):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise CareBotError("OPENAI_API_KEY is not configured on server")

    try:
        from openai import OpenAI
    except ImportError as error:
        raise CareBotError("openai is not installed") from error

    severity = context.get("severity", "Normal")
    score = context.get("score", "0")
    action = context.get("action", "None")
    system_prompt = (
        "คุณคือ CareBot ผู้ช่วยดูแลสุขภาพจิตใจสำหรับผู้สูงอายุ "
        f"ผลการประเมินของผู้ใช้คือ: {severity}, คะแนน: {score}. "
        f"คำแนะนำ: {action}. "
        "จงพูดคุยด้วยความสุภาพ อ่อนโยน ใช้ภาษาที่เข้าใจง่ายสำหรับผู้สูงอายุ "
        "และหลีกเลี่ยงการวินิจฉัยแทนแพทย์"
    )
    history_text = "\n".join(
        f"{'CareBot' if item.get('role') == 'ai' else 'User'}: {item.get('text', '')}"
        for item in history
    )
    user_prompt = f"ประวัติการสนทนา:\n{history_text}\n\nUser: {message}"

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as error:
        raise CareBotError(str(error)) from error

    return response.choices[0].message.content or ""
