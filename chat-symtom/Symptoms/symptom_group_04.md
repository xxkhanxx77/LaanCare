---
document_type: ems_symptom_group
group_id: EMS04
group_name_th: "เลือดออก (ไม่มีสาเหตุจากการบาดเจ็บ)"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.15-p.16, Module 4, heading เลือดออก (ไม่มีสาเหตุจากการบาดเจ็บ)"
needs_human_review: true
---

# EMS04: เลือดออก (ไม่มีสาเหตุจากการบาดเจ็บ)

## 1. Retrieval Keywords
- คำหลัก: เลือดออก, ไอเป็นเลือด, อาเจียนเป็นเลือด, ถ่ายดำ, เลือดกำเดา, เลือดออกช่องคลอด
- คำใกล้เคียง: ชุ่มผ้าอนามัย 3 ผืนต่อชั่วโมง, เลือดสด, อ่อนแรงมาก, หมดสติชั่ววูบ, ห้ามไม่หยุด
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: เลือดออก, ไอเป็นเลือด, อาเจียนเป็นเลือด, ถ่ายดำ, เลือดกำเดา, เลือดออกช่องคลอด, ชุ่มผ้าอนามัย 3 ผืนต่อชั่วโมง, เลือดสด
- คำที่ควรแยกออกจากกลุ่มนี้: เลือดจากอุบัติเหตุให้ดู EMS21/EMS24, สัตว์กัดให้ดู EMS03

## 2. What This Group Is For
ใช้คัดกรองภาวะเลือดออกที่ไม่ได้เกิดจากการบาดเจ็บ โดยแยกตามแหล่งเลือดและสัญญาณแจ้งเตือนใน PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS04_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.15-16, Module 4, code 4แดง1 | true |
| EMS04_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.15-16, Module 4, code 4แดง2 | true |
| EMS04_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.15-16, Module 4, code 4แดง3 | true |
| EMS04_RED_04 | อาเจียนเลือดสด/ถ่ายดำ/เลือดออกช่องคลอดมากร่วมกับอาการช็อก | มีเลือดออกมากร่วมกับอ่อนแรงมากหรือเกือบหมดสติไหม? | yes_no | PDF p.15-16, Module 4, code 4แดง5-4แดง7 | true |
| EMS04_RED_05 | ไอเป็นเลือดร่วมกับหายใจยากหรืออาการช็อก 2 ข้อ | ไอเป็นเลือดและหายใจยากไหม? | yes_no | PDF p.15-16, Module 4, code 4แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS04_YELLOW_01 | เลือดออกที่ไม่เข้าเกณฑ์แดง | มีเลือดออกจากร่างกายส่วนใดอยู่ไหม? | yes_no | PDF p.15-16, Module 4, code 4เหลือง1 | true |
| EMS04_YELLOW_02 | หายใจขัด | หายใจขัดไหม? | yes_no | PDF p.15-16, Module 4, code 4เหลือง2 | true |
| EMS04_YELLOW_03 | อ่อนแรง/เพลียมาก | อ่อนแรงหรือเพลียมากไหม? | yes_no | PDF p.15-16, Module 4, code 4เหลือง3 | true |
| EMS04_YELLOW_04 | หมดสติชั่ววูบหลายครั้งในวันนั้น | วันนี้หมดสติหรือเกือบหมดสติหลายครั้งไหม? | yes_no | PDF p.15-16, Module 4, code 4เหลือง4 | true |
| EMS04_YELLOW_05 | เลือดกำเดาห้ามแล้วไม่หยุด | เลือดกำเดาห้ามแล้วไม่หยุดไหม? | yes_no | PDF p.15-16, Module 4, code 4เหลือง6 | true |
| EMS04_YELLOW_06 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.15-16, Module 4, code 4เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|


## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS04_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS04_* | 1 |
| EMS04_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS04_RED_01 | 2 |
| EMS04_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS04_RED_02 | 3 |
| EMS04_Q04 | มีเลือดออกจากร่างกายส่วนใดอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS04_YELLOW_01 | 4 |
| EMS04_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS04_* | 5 |

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
  "group_id": "EMS04",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
