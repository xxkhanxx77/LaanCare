import httpx
import json
import sys

# Ensure UTF-8 for Thai characters in terminal
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8100"
HEADERS = {"X-API-Key": "medguard-secret-key"}

def run_test():
    print("--- 🏁 เริ่มการทดสอบระบบ Local Interaction Check ---")
    
    # 1. ล้างข้อมูลเก่า (ถ้ามี) เพื่อความสะอาดในการทดสอบ
    print("\n1. ดึงรายการยาปัจจุบัน...")
    r = httpx.get(f"{BASE_URL}/api/medicines", headers=HEADERS)
    meds = r.json()
    for m in meds:
        httpx.delete(f"{BASE_URL}/api/medicines/{m['id']}", headers=HEADERS)
    print("   ✅ ล้างข้อมูลเรียบร้อย")

    # 2. เพิ่มยา Warfarin (ยาที่มีความเสี่ยงสูง)
    print("\n2. เพิ่มยา 'Warfarin' เข้าสู่ระบบ...")
    httpx.post(f"{BASE_URL}/api/medicines", headers=HEADERS, json={
        "name": "Warfarin", 
        "quantity": "1 pill", 
        "frequency": "once a day"
    })
    print("   ✅ เพิ่ม Warfarin สำเร็จ")

    # 3. ทดสอบเช็คยา Aspirin (พบคู่ Interaction: Warfarin)
    print("\n3. ทดสอบเช็คปฏิกิริยาของ 'Aspirin' (ขณะที่มี Warfarin ในระบบ)...")
    r = httpx.get(f"{BASE_URL}/api/check_interaction", headers=HEADERS, params={"name": "Aspirin"})
    print("   📊 ผลลัพธ์:")
    print(r.json()["report"])

    # 4. ทดสอบยาที่ไม่มีในฐานข้อมูล (เช่น 'Amoxicillin')
    print("\n4. ทดสอบเช็คยาที่ไม่มีข้อมูลความเสี่ยงในระบบ (เช่น 'Amoxicillin')...")
    r = httpx.get(f"{BASE_URL}/api/check_interaction", headers=HEADERS, params={"name": "Amoxicillin"})
    print("   📊 ผลลัพธ์:")
    print(r.json()["report"])

    print("\n--- ✅ จบการทดสอบ ---")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
