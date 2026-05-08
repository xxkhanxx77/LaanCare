---
document_type: ems_symptom_group
group_id: EMS11
group_name_th: "เว้นว่างใน PDF"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.41, Module 11, user-confirmed blank module"
needs_human_review: true
---

# EMS11: เว้นว่างใน PDF

> หมายเหตุ: กลุ่มนี้เว้นว่างตาม PDF และคำยืนยันของผู้ใช้ จึงไม่มี risk rule สำหรับ runtime LLM

## 1. Retrieval Keywords
- คำหลัก: ไม่พบใน PDF
- คำใกล้เคียง: ไม่พบใน PDF
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ไม่พบใน PDF
- คำที่ควรแยกออกจากกลุ่มนี้: ไม่มีเกณฑ์ใน PDF สำหรับกลุ่มนี้

## 2. What This Group Is For
กลุ่มนี้เว้นว่างตาม PDF และไม่ควรใช้จัดระดับความเสี่ยงอัตโนมัติ

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|


### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|


### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|


## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS11_Q01 | กลุ่มนี้ไม่มีเกณฑ์ใน PDF ต้องส่งตรวจทานโดยมนุษย์ | statement | [] | if_group_detected |  |  | 1 |

## 5. Skip Rules

- ถ้า `session_mode = self_checkin` และ `user_can_chat = true`:
  - ข้ามคำถามเรื่องผู้ป่วยไม่ตอบสนอง
  - ข้ามคำถามเรื่องผู้ป่วยกำลังชักอยู่
  - ข้ามคำถามที่สมมติว่าผู้ป่วยไม่สามารถตอบเองได้
- ถ้า `session_mode = caregiver_report`:
  - อนุญาตให้ถามคำถามเรื่องการตอบสนองได้ เฉพาะถ้ามีอยู่ใน PDF

## 6. Minimum Information Needed

| info_key | reason | required_for |
|---|---|---|
| main_symptom | เพื่อเลือกกลุ่มอาการ | group_detection |
| onset | เพื่อช่วยแบ่งระดับความเสี่ยงตามเกณฑ์ PDF | risk_screening |
| red_flag_answer | เพื่อหยุดถามและ alert ทันทีถ้าเข้าเกณฑ์ | red |

## 7. Output Contract For Runtime LLM

Runtime LLM ต้องตอบเป็น JSON เท่านั้น:
```json
{
  "group_id": "EMS11",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
