import io
import json
import os

try:
    from .storage import list_medicines
    from .drug_interaction import SEARCH_ENGINE, INTERACTIONS, find_interactions
except ImportError:
    from storage import list_medicines
    from drug_interaction import SEARCH_ENGINE, INTERACTIONS, find_interactions


BASE_DIR = os.path.dirname(__file__)
OCR_MODEL_NAMES = ["gemini-flash-lite-latest"]

OCR_PROMPT = """
วิเคราะห์ภาพที่เกี่ยวกับสุขภาพนี้และระบุประเภท (medicine, blood_pressure, blood_glucose, food, หรือ appointment)
สกัดข้อมูลออกมาเป็น JSON ภาษาไทยตามโครงสร้างด้านล่างนี้เท่านั้น

Output JSON Schema:
{
    "type": "medicine" | "blood_pressure" | "blood_glucose" | "food" | "appointment" | "unknown",
    "data": { ... ข้อมูลตามประเภท ... },
    "interpretation": "สรุปผลสั้นๆ เป็นภาษาไทย"
}

รายละเอียดฟิลด์ใน data (ให้เป็นภาษาไทย):
- ถ้าเป็น 'medicine': {
    "medication name": "ชื่อยาภาษาไทย",
    "number": 1,
    "frequency": ["เช้า", "กลางวัน", "เย็น", "ก่อนนอน"],
    "time of taking": ["ก่อนอาหาร", "หลังอาหาร"]
  }
- ถ้าเป็น 'blood_pressure': {"systolic": int, "diastolic": int, "pulse": int}
- ถ้าเป็น 'blood_glucose': {"value": float, "unit": "mg/dL", "context": "ก่อนอาหาร" | "หลังอาหาร"}
- ถ้าเป็น 'food': {
    "dish_name": "ชื่ออาหาร",
    "calories": int,
    "protein": "g",
    "fat": "g",
    "carbs": "g",
    "rating": 1-5,
    "advice": "คำแนะนำสั้นๆ"
  }
- ถ้าเป็น 'appointment': {
    "hospital": "ชื่อโรงพยาบาล",
    "department": "แผนก/คลินิก",
    "doctor": "ชื่อแพทย์ (ถ้ามี)",
    "date": "วันที่นัดหมาย (พ.ศ.)",
    "time": "เวลานัดหมาย",
    "preparation": "การเตรียมตัว (เช่น งดน้ำ/งดอาหาร)",
    "reason": "เหตุผลที่นัด/อาการ"
  }

กฎการแปลผล (Thai):
- ความดัน: เทียบกับ 120/80
- น้ำตาล: เทียบกับ 100 mg/dL
- อาหาร: ประเมินจากปริมาณสารอาหาร
- ใบนัด: สรุปสิ่งที่คนไข้ต้องทำหรือเตรียมตัว
"""


class LocalOCRError(Exception):
    pass


def perform_ocr(image_bytes, group_id=None):
    client = build_gemini_client()
    image = load_image(image_bytes)
    response = generate_content(client, image)
    extracted_data = parse_model_json(response.text)
    detected_type = extracted_data.get("type", "unknown")
    data = extracted_data.get("data", {})
    interaction_report = None

    if detected_type == "medicine":
        medicine_name = data.get("medication name", data.get("name", "Unknown"))
        interaction_report = check_interactions(medicine_name, group_id)

    return {
        "success": True,
        "detected_type": detected_type,
        "data": data,
        "interpretation": extracted_data.get("interpretation"),
        "interaction_report": interaction_report,
    }


def build_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LocalOCRError("GEMINI_API_KEY is not configured")

    try:
        from google import genai
    except ImportError as error:
        raise LocalOCRError("google-genai is not installed") from error

    return genai.Client(api_key=api_key)


def load_image(image_bytes):
    try:
        from PIL import Image
    except ImportError as error:
        raise LocalOCRError("pillow is not installed") from error

    try:
        return Image.open(io.BytesIO(image_bytes))
    except Exception as error:
        raise LocalOCRError("Uploaded file is not a readable image") from error


def generate_content(client, image):
    last_error = None

    for model_name in OCR_MODEL_NAMES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[OCR_PROMPT, image],
            )
            if response:
                return response
        except Exception as error:
            last_error = error

    raise LocalOCRError(f"All OCR models failed: {last_error}")


def parse_model_json(text):
    try:
        clean_json = text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_json)
    except Exception as error:
        raise LocalOCRError("AI returned invalid data format") from error


def check_interactions(new_medicine_name, group_id=None):
    existing_medicine_names = [
        medicine["medicine_name"]
        for medicine in list_medicines(group_id)
        if medicine.get("medicine_name")
    ]

    new_match = SEARCH_ENGINE.match(new_medicine_name)
    if not new_match.get("matched"):
        if not existing_medicine_names:
            return "ยังไม่มีการลงทะเบียนยาอื่นๆ ไม่พบความเสี่ยงที่ขัดกันในขณะนี้"
        return f"ไม่พบข้อมูลความเสี่ยงที่ขัดกันของ {new_medicine_name} ในฐานข้อมูลตัวอย่างของเรา"

    existing_matches = [SEARCH_ENGINE.match(name) for name in existing_medicine_names]
    detected = find_interactions([new_match] + existing_matches, INTERACTIONS)

    matched_name = new_match["selected"]["generic_name"]
    if not detected:
        if not existing_medicine_names:
            return "ยังไม่มีการลงทะเบียนยาอื่นๆ ไม่พบความเสี่ยงที่ขัดกันในขณะนี้"
        return f"ไม่พบข้อมูลความเสี่ยงที่ขัดกันของ {matched_name} ในฐานข้อมูลตัวอย่างของเรา"

    reports = [f"ตรวจพบข้อมูลยา: {matched_name}"]
    for ix in detected:
        reports.append(f"คำเตือน: พบความเสี่ยงระหว่าง {ix['group_1']} และ {ix['group_2']}")
        reports.append(f"- รายละเอียด: {ix['interaction_risk']}")
        reports.append(f"- ความรุนแรง: {ix['interaction_severity']}")
        if ix.get("possible_symptoms"):
            reports.append(f"- อาการที่อาจเกิดขึ้น: {ix['possible_symptoms']}")
    return "\n".join(reports)
