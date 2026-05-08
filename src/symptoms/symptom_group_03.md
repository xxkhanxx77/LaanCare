---
document_type: ems_symptom_group
group_id: EMS03
group_name_th: "สัตว์กัด"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.11, Module 3, heading สัตว์กัด"
needs_human_review: true
---

# EMS03: สัตว์กัด

## 1. Retrieval Keywords
- คำหลัก: สัตว์กัด, สัตว์ต่อย, งูกัด, แมลงต่อย, ถูกกัด, ถูกเลีย
- คำใกล้เคียง: เลือดออก, กัดใบหน้า, กัดลำคอ, สัตว์พิษ, งูพิษ, ต่อแตนผึ้งหลายจุด
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: สัตว์กัด, สัตว์ต่อย, งูกัด, แมลงต่อย, ถูกกัด, ถูกเลีย, เลือดออก, กัดใบหน้า
- คำที่ควรแยกออกจากกลุ่มนี้: แผลจากทำร้ายหรืออุบัติเหตุให้ดู EMS21/EMS24

## 2. What This Group Is For
ใช้คัดกรองเหตุสัตว์กัดหรือต่อย โดยเน้นตำแหน่ง แผล เลือดออก หายใจ และสัตว์พิษตาม PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS03_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.11, Module 3, code 3แดง1 | true |
| EMS03_RED_02 | หายใจลำบากร่วมกับอาการผิดปกติ รวมถึงกัดลำคอ/ใบหน้า หรือคอหอย/ลิ้นบวม | ถูกกัดที่หน้า/คอ หรือมีลิ้นบวมร่วมกับหายใจลำบากไหม? | yes_no | PDF p.11, Module 3, code 3แดง2 | true |
| EMS03_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.11, Module 3, code 3แดง3 | true |
| EMS03_RED_04 | เลือดออกห้ามไม่หยุดหรือออกนอกบริเวณที่กัด | เลือดออกแล้วยังห้ามไม่หยุดไหม? | yes_no | PDF p.11, Module 3, code 3แดง5 | true |
| EMS03_RED_05 | ถูกสัตว์พิษร้ายแรงกัด/ต่อยตามตัวอย่างใน PDF | ถูกสัตว์พิษร้ายแรงหรือถูกต่อยหลายจุดไหม? | yes_no | PDF p.11, Module 3, code 3แดง6 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS03_YELLOW_01 | ถูกกัดที่ใบหน้า/ลำคอ แต่ห้ามเลือดได้ | ถูกกัดที่หน้า หรือคอ แต่เลือดหยุดแล้วใช่ไหม? | yes_no | PDF p.11, Module 3, code 3เหลือง1 | true |
| EMS03_YELLOW_02 | หายใจขัด | หายใจขัดไหม? | yes_no | PDF p.11, Module 3, code 3เหลือง2 | true |
| EMS03_YELLOW_03 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.11, Module 3, code 3เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|


## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS03_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS03_* | 1 |
| EMS03_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS03_RED_01 | 2 |
| EMS03_Q03 | ถูกกัดที่หน้า/คอ หรือมีลิ้นบวมร่วมกับหายใจลำบากไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS03_RED_02 | 3 |
| EMS03_Q04 | ถูกกัดที่หน้า หรือคอ แต่เลือดหยุดแล้วใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS03_YELLOW_01 | 4 |
| EMS03_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS03_* | 5 |

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
  "group_id": "EMS03",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
