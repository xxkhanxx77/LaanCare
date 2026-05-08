---
document_type: ems_symptom_group
group_id: EMS15
group_name_th: "มีครรภ์/คลอด/นรีเวช"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.56-p.57, Module 15, heading มีครรภ์/คลอด/นรีเวช"
needs_human_review: true
---

# EMS15: มีครรภ์/คลอด/นรีเวช

## 1. Retrieval Keywords
- คำหลัก: ตั้งครรภ์, มีครรภ์, คลอด, เจ็บท้องคลอด, เลือดออกช่องคลอด, น้ำเดิน, นรีเวช
- คำใกล้เคียง: อายุครรภ์ >20 สัปดาห์, ชุ่มผ้าอนามัย 3 แผ่นต่อชั่วโมง, มดลูกหดบีบตัว, ทารกกำลังคลอด, ถุงน้ำคร่ำแตก
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ตั้งครรภ์, มีครรภ์, คลอด, เจ็บท้องคลอด, เลือดออกช่องคลอด, น้ำเดิน, นรีเวช, อายุครรภ์ >20 สัปดาห์
- คำที่ควรแยกออกจากกลุ่มนี้: ปวดท้องทั่วไปไม่เกี่ยวกับครรภ์ให้ดู EMS01, เลือดออกทั่วไปให้ดู EMS04

## 2. What This Group Is For
ใช้คัดกรองข้อความเกี่ยวกับตั้งครรภ์ คลอด หรือเลือดออกทางนรีเวชตาม PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS15_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.56-57, Module 15, code 15แดง1 | true |
| EMS15_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.56-57, Module 15, code 15แดง2 | true |
| EMS15_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.56-57, Module 15, code 15แดง3 | true |
| EMS15_RED_04 | เลือดออกทางช่องคลอดร่วมกับอายุครรภ์ >20 สัปดาห์ หรือเลือดมากร่วมกับช็อก | ตั้งครรภ์เกิน 20 สัปดาห์และมีเลือดออกไหม? | yes_no | PDF p.56-57, Module 15, code 15แดง5 | true |
| EMS15_RED_05 | ชักในครรภ์ >20 สัปดาห์ ทารกกำลังคลอด หดตัวถี่ ภาวะแทรกซ้อน หรือบาดเจ็บช่องท้องร่วมกับหดตัว | มีชัก ทารกกำลังคลอด หรือมดลูกหดตัวถี่มากไหม? | yes_no | PDF p.56-57, Module 15, code 15แดง6-15แดง10 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS15_YELLOW_01 | เลือดออกทางช่องคลอด | มีเลือดออกทางช่องคลอดไหม? | yes_no | PDF p.56-57, Module 15, code 15เหลือง1 | true |
| EMS15_YELLOW_02 | บาดเจ็บช่องท้อง ไม่มีมดลูกหดตัว อายุครรภ์ >20 สัปดาห์ | ตั้งครรภ์เกิน 20 สัปดาห์และบาดเจ็บช่องท้องไหม? | yes_no | PDF p.56-57, Module 15, code 15เหลือง4 | true |
| EMS15_YELLOW_03 | ถุงน้ำคร่ำแตก ร่วมกับมดลูกหดบีบตัว | น้ำเดินและมีมดลูกหดตัวไหม? | yes_no | PDF p.56-57, Module 15, code 15เหลือง5 | true |
| EMS15_YELLOW_04 | ระยะหดตัวตามครรภ์แรกหรือครรภ์ถัดไปที่ PDF ระบุ | กำลังเจ็บท้องคลอดและหดตัวเป็นระยะไหม? | yes_no | PDF p.56-57, Module 15, code 15เหลือง6-15เหลือง7 | true |
| EMS15_YELLOW_05 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.56-57, Module 15, code 15เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|


## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS15_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS15_* | 1 |
| EMS15_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS15_RED_01 | 2 |
| EMS15_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS15_RED_02 | 3 |
| EMS15_Q04 | มีเลือดออกทางช่องคลอดไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS15_YELLOW_01 | 4 |
| EMS15_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS15_* | 5 |

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
  "group_id": "EMS15",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
