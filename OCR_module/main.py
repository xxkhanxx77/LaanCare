import os
import sqlite3
import json
import traceback
import io
import httpx
import difflib
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()
BASE_DIR = os.path.dirname(__file__)

# Configure Gemini API with the NEW SDK
API_KEY = os.getenv("GEMINI_API_KEY")
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)

# Security Configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "medguard-secret-key")

# Placeholder for External Notification API
EXTERNAL_NOTIFY_URL = os.getenv("NOTIFY_API_URL", "https://api.example.com/notify")

# --- Pydantic Models ---

class OCRResponse(BaseModel):
    success: bool
    detected_type: str = Field(..., description="Type of health data detected: medicine, blood_pressure, blood_glucose, or unknown")
    data: dict = Field(..., description="The extracted structured data")
    interpretation: Optional[str] = Field(None, description="Thai interpretation of the results (e.g., for BP/Glucose)")
    interaction_report: Optional[str] = Field(None, description="Interaction report (only for medicines)")

class MedicineCreate(BaseModel):
    name: str
    quantity: Optional[str] = None
    frequency: Optional[str] = None
    time_of_taking: Optional[str] = None
    expiry: Optional[str] = None
    instructions: Optional[str] = None

class MedicineResponse(MedicineCreate):
    id: int
    added_at: str

app = FastAPI(
    title="MedGuard AI Public API",
    description="API for Medicine OCR extraction and Safety checking using Gemini AI",
    version="1.0.0"
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for public access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_api_key(api_key: str = Security(api_key_header)):
    # If INTERNAL_API_KEY is not set or empty, we allow public access
    if not INTERNAL_API_KEY or INTERNAL_API_KEY == "":
        return api_key
    if api_key == INTERNAL_API_KEY:
        return api_key
    # For now, we'll keep it open but log if key is missing/wrong
    # To enforce: raise HTTPException(status_code=403, detail="Could not validate API Key")
    return api_key

# --- Database Setup ---
DB_PATH = os.path.join(BASE_DIR, "medicines.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity TEXT,
            frequency TEXT,
            time_of_taking TEXT,
            expiry TEXT,
            instructions TEXT,
            last_notified TIMESTAMP,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Static Files ---
static_dir = os.path.join(BASE_DIR, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Frontend files not found.</h1>"

# --- API Endpoints ---

@app.post("/api/ocr", response_model=OCRResponse, tags=["AI Services"])
async def perform_ocr(
    file: UploadFile = File(...), 
    api_key: str = Depends(get_api_key)
):
    """
    Upload an image of a medicine label to extract structured data and check for interactions.
    """
    if not client:
        raise HTTPException(status_code=500, detail="Gemini API Client not initialized.")
    
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))
        
        prompt = """
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
        
        # Robust Model Rotation (Based on verified available models in your environment)
        models_to_try = [
            # 'gemini-2.0-flash',
            # 'gemini-flash-latest',
            # 'gemini-3.1-flash-lite-preview',
            # 'gemini-2.0-flash-lite',
            'gemini-flash-lite-latest'
        ]
        
        # Diagnostic (Keep it for one more run if you want to verify, or remove it)
        try:
            print("--- Available Models for your API Key ---")
            for m in client.models.list():
                print(f"- {m.name}")
            print("-----------------------------------------")
        except:
            pass

        response = None
        last_error = None
        
        for model_name in models_to_try:
            try:
                print(f"Attempting OCR with model: {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt, img]
                )
                if response:
                    print(f"✅ Success with model: {model_name}")
                    break
            except Exception as e:
                last_error = e
                print(f"❌ Model {model_name} failed: {str(e)}")
                continue
        
        if not response:
            raise HTTPException(status_code=503, detail=f"All AI models are currently busy. Please try again in a moment. (Last error: {str(last_error)})")
        
        # Parse JSON
        try:
            clean_json = response.text.strip().replace("```json", "").replace("```", "")
            extracted_data = json.loads(clean_json)
            
            detected_type = extracted_data.get("type", "unknown")
            data = extracted_data.get("data", {})
            
            # Debug: See what AI actually extracted
            print(f"🔍 AI Detected Type: {detected_type}")
            print(f"📦 AI Extracted Data: {json.dumps(data, ensure_ascii=False)}")
            
        except Exception as e:
            print(f"❌ JSON Parse Error: {str(e)}")
            print(f"Raw Response: {response.text}")
            raise HTTPException(status_code=500, detail="AI returned invalid data format.")
        interpretation = extracted_data.get("interpretation")
        interaction_report = None

        if detected_type == "medicine":
            med_name = data.get('medication name', data.get('name', 'Unknown'))
            interaction_report = await check_interactions(med_name)
        
        return { 
            "success": True, 
            "detected_type": detected_type,
            "data": data,
            "interpretation": interpretation,
            "interaction_report": interaction_report 
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Load Local Drug Knowledge
DRUG_KNOWLEDGE_PATH = os.path.join(BASE_DIR, "drug_knowledge.json")
drug_kb = {"drugs": []}
if os.path.exists(DRUG_KNOWLEDGE_PATH):
    try:
        with open(DRUG_KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
            drug_kb = json.load(f)
    except Exception as e:
        print(f"Error loading drug knowledge: {e}")

def get_closest_drug(name: str):
    """Find the closest drug name from the knowledge base using fuzzy matching."""
    if not drug_kb.get("drugs"):
        return None
    names = [d["name"] for d in drug_kb["drugs"]]
    matches = difflib.get_close_matches(name, names, n=1, cutoff=0.6)
    if matches:
        # Return the actual drug object
        return next((d for d in drug_kb["drugs"] if d["name"] == matches[0]), None)
    return None

async def check_interactions(new_med_name: str):
    """
    Check for potential drug interactions locally using fuzzy matching.
    Does NOT call Gemini.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM medicines")
    existing_med_names = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    new_drug = get_closest_drug(new_med_name)
    reports = []

    # 1. Check against knowledge base for the new drug
    if new_drug:
        reports.append(f"🔍 ตรวจพบข้อมูลยา: **{new_drug['name']}**")
        
        # Check against each existing drug
        for existing_name in existing_med_names:
            existing_drug = get_closest_drug(existing_name)
            if existing_drug:
                # Check if new_drug has interaction with existing_drug
                for interaction in new_drug.get("interactions", []):
                    if interaction["target"].lower() == existing_drug["name"].lower():
                        reports.append(f"⚠️ **คำเตือน (Interaction):** พบความเสี่ยงระหว่าง {new_drug['name']} และ {existing_drug['name']}")
                        reports.append(f"   - รายละเอียด: {interaction['risk']}")
                        reports.append(f"   - ความรุนแรง: {interaction['severity']}")

    if not reports:
        if not existing_med_names:
            return "✅ ยังไม่มีการลงทะเบียนยาอื่นๆ ไม่พบความเสี่ยงที่ขัดกันในขณะนี้"
        return f"✅ ไม่พบข้อมูลความเสี่ยงที่ขัดกัน (Interaction) ของ {new_med_name} ในฐานข้อมูลตัวอย่างของเรา"

    return "\n".join(reports)

@app.post("/api/check_interactions", tags=["AI Services"])
async def api_check_bulk_interactions(drug_list: List[str], api_key: str = Depends(get_api_key)):
    """
    Check for interactions among a provided list of drug names.
    This performs a cross-check between all pairs in the list.
    """
    if not drug_list or len(drug_list) < 2:
        return {"report": "✅ ต้องการชื่อยาอย่างน้อย 2 ชนิดเพื่อตรวจสอบความเสี่ยงระหว่างกัน", "has_warning": False}
    
    all_reports = []
    # Cross-check logic
    for i in range(len(drug_list)):
        for j in range(i + 1, len(drug_list)):
            # Check interaction between drug_list[i] and drug_list[j]
            report = await check_interactions(drug_list[i], [drug_list[j]])
            if "⚠️" in report:
                all_reports.append(report)
    
    final_report = "\n".join(list(set(all_reports))) if all_reports else "✅ ไม่พบความเสี่ยงที่ขัดกันรุนแรงในรายการยานี้"
    return {
        "report": final_report,
        "has_warning": len(all_reports) > 0
    }

@app.post("/api/medicines", tags=["Medicine Management"])
async def register_medicine(data: MedicineCreate, api_key: str = Depends(get_api_key)):
    """Register a new medicine into the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medicines (name, quantity, frequency, time_of_taking, expiry, instructions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.name, 
            data.quantity, 
            data.frequency, 
            data.time_of_taking, 
            data.expiry,
            data.instructions
        ))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/medicines", response_model=List[MedicineResponse], tags=["Medicine Management"])
async def list_medicines(api_key: str = Depends(get_api_key)):
    """List all registered medicines."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines ORDER BY added_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0], 
            "name": r[1], 
            "quantity": r[2], 
            "frequency": r[3], 
            "time_of_taking": r[4], 
            "expiry": r[5], 
            "instructions": r[6],
            "added_at": str(r[8])
        } for r in rows
    ]

@app.delete("/api/medicines/{med_id}", tags=["Medicine Management"])
async def delete_medicine(med_id: int, api_key: str = Depends(get_api_key)):
    """Delete a medicine by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.post("/api/notify/{med_id}", tags=["Notifications"])
async def trigger_notification(med_id: int, api_key: str = Depends(get_api_key)):
    """Trigger a notification for a specific medicine."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity, frequency, time_of_taking FROM medicines WHERE id = ?", (med_id,))
    res = cursor.fetchone()
    conn.close()
    
    if not res:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    name, quantity, frequency, time_of_taking = res
    message = f"🔔 Reminder: It's time to take {name} ({quantity}). Frequency: {frequency}, Timing: {time_of_taking}"
    
    try:
        async with httpx.AsyncClient() as client_http:
            await client_http.post(EXTERNAL_NOTIFY_URL, json={"message": message, "medicine": name})
    except Exception as e:
        print(f"External notification failed: {str(e)}")

    return {"success": True, "message": message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
