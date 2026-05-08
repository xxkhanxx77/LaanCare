---
document_type: ems_symptom_group
group_id: EMS01
group_name_th: "ปวดท้อง/หลัง/เชิงกรานและขาหนีบ"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.3, Module 1, heading ปวดท้อง/หลัง/เชิงกรานและขาหนีบ"
needs_human_review: true
---

# EMS01: ปวดท้อง/หลัง/เชิงกรานและขาหนีบ

## 1. Retrieval Keywords
- คำหลัก: ปวดท้อง, ปวดหลัง, ปวดเชิงกราน, ปวดขาหนีบ, จุกยอดอก, ปวดบั้นเอว
- คำใกล้เคียง: อาเจียน, ถ่ายดำ, เลือดออกทางช่องคลอด, ปวดท้องส่วนล่าง, อายุเกิน 50, อายุเกิน 65
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ปวดท้อง, ปวดหลัง, ปวดเชิงกราน, ปวดขาหนีบ, จุกยอดอก, ปวดบั้นเอว, อาเจียน, ถ่ายดำ
- คำที่ควรแยกออกจากกลุ่มนี้: เจ็บแน่นทรวงอกเด่นให้ดู EMS07, เลือดออกเด่นโดยไม่ปวดให้ดู EMS04

## 2. What This Group Is For
ใช้คัดกรองข้อความที่อาการหลักเป็นปวดท้อง ปวดหลัง ปวดเชิงกราน หรือขาหนีบ โดยดูสัญญาณแจ้งเตือนจาก PDF เท่านั้น

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS01_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.3, Module 1, code 1แดง1 | true |
| EMS01_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่ประโยคสั้น ๆ ไหม? | yes_no | PDF p.3, Module 1, code 1แดง2 | true |
| EMS01_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.3, Module 1, code 1แดง3 | true |
| EMS01_RED_04 | อาเจียนเลือดสด/ถ่ายดำ/เลือดออกช่องคลอดมากร่วมกับอาการช็อก | มีเลือดออกหรืออาเจียน/ถ่ายเป็นเลือดร่วมกับอ่อนแรงมากไหม? | yes_no | PDF p.3, Module 1, code 1แดง5-1แดง7 | true |
| EMS01_RED_05 | ปวดท้องล่าง/หลังในอายุ >65 หรือจุกยอดอก/ท้องบนในอายุ >50 ร่วมกับอาการช็อก | อายุเกิน 50 ปีและมีจุกแน่นยอดอกหรือท้องบนร่วมกับอ่อนแรงมากไหม? | yes_no | PDF p.3, Module 1, code 1แดง8-1แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS01_YELLOW_01 | ปวดร่วมกับอาเจียน | ปวดร่วมกับอาเจียนไหม? | yes_no | PDF p.3, Module 1, code 1เหลือง1 | true |
| EMS01_YELLOW_02 | หายใจขัด | หายใจขัดไหม? | yes_no | PDF p.3, Module 1, code 1เหลือง2 | true |
| EMS01_YELLOW_03 | อาการแสดงช็อกอย่างน้อย 1 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติแม้เพียงข้อเดียวไหม? | yes_no | PDF p.3, Module 1, code 1เหลือง3 | true |
| EMS01_YELLOW_04 | ปวดท้อง/หลังตามอายุหรือบริเวณที่ PDF ระบุ | อายุ 50 ปีขึ้นไปและปวดท้องหรือปวดหลังไหม? | yes_no | PDF p.3, Module 1, code 1เหลือง4-1เหลือง6 | true |
| EMS01_YELLOW_05 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.3, Module 1, code 1เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|


## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS01_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS01_* | 1 |
| EMS01_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS01_RED_01 | 2 |
| EMS01_Q03 | หายใจลำบากมากหรือพูดได้แค่ประโยคสั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS01_RED_02 | 3 |
| EMS01_Q04 | ปวดร่วมกับอาเจียนไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS01_YELLOW_01 | 4 |
| EMS01_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS01_* | 5 |

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
  "group_id": "EMS01",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
