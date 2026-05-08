from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import sqlite3
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env from root or current directory
load_dotenv() # Load from current dir
load_dotenv("../.env") # Load from root if running from backend folder

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
DB_FILE = "assessments.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            score INTEGER,
            responses TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Gemini Setup - Try both names to be safe
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("VITE_GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

# Models
class AssessmentResult(BaseModel):
    type: str
    score: int
    responses: Dict[str, int]

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]
    context: Dict[str, str]

@app.post("/save-assessment")
async def save_assessment(result: AssessmentResult):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO results (type, score, responses, timestamp) VALUES (?, ?, ?, ?)",
            (result.type, result.score, json.dumps(result.responses), datetime.now())
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Assessment saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results")
async def get_results():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM results ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "type": row["type"],
                "score": row["score"],
                "responses": json.loads(row["responses"]),
                "timestamp": row["timestamp"]
            })
        
        conn.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_gemini(request: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured on server")
    
    try:
        system_prompt = f"คุณคือ CareBot ผู้ช่วยดูแลสุขภาพจิตใจสำหรับผู้สูงอายุ ผลการประเมินของผู้ใช้คือ: {request.context.get('severity', 'Normal')}, คะแนน: {request.context.get('score', 0)}. คำแนะนำ: {request.context.get('action', 'None')}. จงพูดคุยด้วยความสุภาพ อ่อนโยน ใช้ภาษาที่เข้าใจง่ายสำหรับผู้สูงอายุ"
        
        # Format history for Gemini
        history_str = "\n".join([f"{'CareBot' if m['role'] == 'ai' else 'User'}: {m['text']}" for m in request.history])
        full_prompt = f"{system_prompt}\n\nประวัติการสนทนา:\n{history_str}\nUser: {request.message}\nCareBot:"
        
        response = model.generate_content(full_prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
