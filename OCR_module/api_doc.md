# 🛡️ MedGuard AI - API Documentation (V1.0)

เอกสารระบุรายละเอียดการเชื่อมต่อ API สำหรับระบบจัดการยาสามัญประจำบ้านและวิเคราะห์ข้อมูลสุขภาพอัตโนมัติ

## 🌐 Base URL
- **Tunnel URL:** `https://sandwich-diagnostic-surgeon-subscribers.trycloudflare.com`
- **Interactive Docs (Swagger):** `/docs`

## 🔑 Authentication
ระบบใช้ API Key ในการรักษาความปลอดภัย โดยต้องส่งผ่าน HTTP Header:
- **Header:** `X-API-Key`
- **Default Value:** `medguard-secret-key`

---

## 📡 Endpoints รายละเอียด

### 1. Universal Health OCR
ระบบแยกแยะประเภทข้อมูลสุขภาพอัตโนมัติจากภาพถ่าย (ไม่ต้องระบุประเภทล่วงหน้า)

- **Endpoint:** `/api/ocr`
- **Method:** `POST`
- **Payload:** `multipart/form-data`
    - `file`: (File) รูปภาพฉลากยา, หน้าจอวัดความดัน, หน้าจอวัดน้ำตาล, อาหาร, หรือใบนัด

**การตอบกลับ (Response):**
```json
{
  "success": true,
  "detected_type": "medicine | blood_pressure | blood_glucose | food | appointment",
  "data": { ...สถิติที่ตรวจพบ... },
  "interpretation": "สรุปผลภาษาไทย (เช่น ความดันปกติ, น้ำตาลเริ่มสูง)",
  "interaction_report": "รายงานความเสี่ยงกรณีเป็นยา (Thai)"
}
```

---

### 2. Medicine Management
จัดการรายการยาที่คนไข้ใช้ปัจจุบัน

- **List All:** `GET /api/medicines`
- **Register:** `POST /api/medicines`
    - Body: `MedicineCreate` (JSON)
- **Delete:** `DELETE /api/medicines/{med_id}`

---

### 3. Vitals & Food (Schema Detail)

#### 💊 Medicine (ยา)
- `medication name`: ชื่อยา (ภาษาไทย)
- `frequency`: `["เช้า", "กลางวัน", "เย็น", "ก่อนนอน"]`
- `time of taking`: `["ก่อนอาหาร", "หลังอาหาร"]`

#### 💓 Blood Pressure (ความดัน)
- `systolic`: ค่าบน
- `diastolic`: ค่าล่าง
- `pulse`: ชีพจร

#### 🩸 Blood Glucose (น้ำตาล)
- `value`: ค่าน้ำตาล
- `unit`: `mg/dL`
- `context`: `ก่อนอาหาร / หลังอาหาร`

#### 🍱 Food (อาหารและแคลอรี่)
- `dish_name`: ชื่ออาหาร
- `calories`: แคลอรี่โดยประมาณ
- `rating`: 1-5 (คะแนนสุขภาพ)
- `advice`: คำแนะนำเชิงโภชนาการ

#### 📅 Appointment (ใบนัดหมอ)
- `hospital`: ชื่อสถานพยาบาล
- `date`: วันที่นัด
- `preparation`: การเตรียมตัว (เช่น งดน้ำ/อาหาร)

---

## 📋 Response Examples (ตามประเภทข้อมูล)

### 1. 💊 Medicine (ยา)
```json
{
  "success": true,
  "detected_type": "medicine",
  "data": {
    "medication name": "Amlodipine 5mg",
    "number": 1,
    "frequency": ["เช้า"],
    "time of taking": ["หลังอาหาร"]
  },
  "interpretation": "ยาลดความดันโลหิต ควรทานให้ตรงเวลา",
  "interaction_report": "✅ ไม่พบข้อมูลความเสี่ยงที่ขัดกันในฐานข้อมูล"
}
```

### 2. 💓 Blood Pressure (ความดัน)
```json
{
  "success": true,
  "detected_type": "blood_pressure",
  "data": {
    "systolic": 128,
    "diastolic": 84,
    "pulse": 72
  },
  "interpretation": "ความดันโลหิตของคุณอยู่ในเกณฑ์เริ่มสูงเล็กน้อย (Pre-hypertension) ควรพักผ่อนให้เพียงพอ",
  "interaction_report": null
}
```

### 3. 🩸 Blood Glucose (น้ำตาล)
```json
{
  "success": true,
  "detected_type": "blood_glucose",
  "data": {
    "value": 115,
    "unit": "mg/dL",
    "context": "หลังอาหาร"
  },
  "interpretation": "ระดับน้ำตาลหลังอาหารอยู่ในเกณฑ์ปกติ",
  "interaction_report": null
}
```

### 4. 🍱 Food (อาหาร)
```json
{
  "success": true,
  "detected_type": "food",
  "data": {
    "dish_name": "ข้าวมันไก่ผสมไก่ทอด",
    "calories": 650,
    "protein": "25g",
    "fat": "30g",
    "carbs": "70g",
    "rating": 2,
    "advice": "มีไขมันและคาร์โบไฮเดรตสูง ควรเพิ่มผักและลดการทานหนังไก่"
  },
  "interpretation": "อาหารมื้อนี้ให้พลังงานสูง ควรระมัดระวังปริมาณไขมัน",
  "interaction_report": null
}
```

### 5. 📅 Appointment (ใบนัดหมอ)
```json
{
  "success": true,
  "detected_type": "appointment",
  "data": {
    "hospital": "โรงพยาบาลกรุงเทพ",
    "department": "ศูนย์หัวใจ",
    "doctor": "นพ.สมชาย ใจดี",
    "date": "20 มิ.ย. 2567",
    "time": "09:00",
    "preparation": "งดน้ำและอาหารอย่างน้อย 8 ชั่วโมงก่อนตรวจ",
    "reason": "ตรวจติดตามอาการโรคความดันโลหิตสูง"
  },
  "interpretation": "คุณมีนัดตรวจหัวใจ ต้องงดน้ำและอาหารก่อนไปโรงพยาบาล",
  "interaction_report": null
}
```

---

## 💻 Code Example (Python)
```python
import requests

url = "https://sandwich-diagnostic-surgeon-subscribers.trycloudflare.com/api/ocr"
headers = {"X-API-Key": "medguard-secret-key"}
files = {"file": open("my_photo.jpg", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```
