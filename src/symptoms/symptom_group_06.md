---
document_type: ems_symptom_group
group_id: EMS06
group_name_th: "หัวใจหยุดเต้น"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.23, Module 6, heading หัวใจหยุดเต้น"
needs_human_review: true
---

# EMS06: หัวใจหยุดเต้น

## 1. Retrieval Keywords
- คำหลัก: หัวใจหยุดเต้น, หยุดหายใจ, ไม่หายใจ, ไม่รู้สึกตัว, เสียชีวิตแล้วก่อนถึง
- คำใกล้เคียง: ไม่ตอบสนอง, ทรวงอกไม่ขยับ, หายใจพะงาบ, Obvious DOA, หนังสือแสดงเจตนา
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: หัวใจหยุดเต้น, หยุดหายใจ, ไม่หายใจ, ไม่รู้สึกตัว, เสียชีวิตแล้วก่อนถึง, ไม่ตอบสนอง, ทรวงอกไม่ขยับ, หายใจพะงาบ
- คำที่ควรแยกออกจากกลุ่มนี้: หมดสติแต่ยังหายใจให้ดู EMS19

## 2. What This Group Is For
ใช้คัดกรองเหตุไม่รู้สึกตัว ไม่หายใจ หรือสงสัยหยุดหายใจตามเกณฑ์ PDF โดยไม่ให้คำแนะนำการกู้ชีพในเอกสารนี้

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS06_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ผู้ป่วยไม่ตอบสนองหรือไม่หายใจใช่ไหม? | yes_no | PDF p.23, Module 6, code 6แดง1 | true |
| EMS06_RED_02 | เสียชีวิตแล้วก่อนถึงในทารกอายุน้อยกว่า 1 ปีร่วมกับตัวเย็น/แข็ง | อายุน้อยกว่า 1 ปีและตัวเย็นหรือแข็งใช่ไหม? | yes_no | PDF p.23, Module 6, code 6แดง6 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS06_YELLOW_01 | เสียชีวิตแล้วก่อนถึง อายุ >=1 ปี หรือสภาพตาม PDF | ยืนยันว่าเสียชีวิตแล้วก่อนถึงตามเกณฑ์ PDF ใช่ไหม? | yes_no | PDF p.23, Module 6, code 6เหลือง1 | true |
| EMS06_YELLOW_02 | มีหนังสือแสดงเจตนาไม่ประสงค์รับบริการเพื่อยืดการตาย | มีเอกสารแสดงเจตนาไม่ประสงค์รับบริการตาม PDF ไหม? | yes_no | PDF p.23, Module 6, code 6เหลือง4 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|


## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS06_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS06_* | 1 |
| EMS06_Q02 | ผู้ป่วยไม่ตอบสนองหรือไม่หายใจใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS06_RED_01 | 2 |
| EMS06_Q03 | อายุน้อยกว่า 1 ปีและตัวเย็นหรือแข็งใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched | session_mode = self_checkin && user_can_chat = true | EMS06_RED_02 | 3 |
| EMS06_Q04 | ยืนยันว่าเสียชีวิตแล้วก่อนถึงตามเกณฑ์ PDF ใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched | session_mode = self_checkin && user_can_chat = true | EMS06_YELLOW_01 | 4 |
| EMS06_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS06_* | 5 |

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
  "group_id": "EMS06",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
