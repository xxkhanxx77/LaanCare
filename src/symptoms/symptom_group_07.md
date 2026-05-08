---
document_type: ems_symptom_group
group_id: EMS07
group_name_th: "เจ็บแน่นทรวงอก/หัวใจ"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.27-p.28, Module 7, heading เจ็บแน่นทรวงอก/หัวใจ"
needs_human_review: true
---

# EMS07: เจ็บแน่นทรวงอก/หัวใจ

## 1. Retrieval Keywords
- คำหลัก: เจ็บแน่นทรวงอก, เจ็บหน้าอก, เจ็บอก, หัวใจ, ใจสั่น, จุกลิ้นปี่
- คำใกล้เคียง: อายุชาย >=40, อายุหญิง >=45, เครื่องกระตุกหัวใจอัตโนมัติช็อก, หายใจไม่พอ, หัวใจเต้นเร็ว
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: เจ็บแน่นทรวงอก, เจ็บหน้าอก, เจ็บอก, หัวใจ, ใจสั่น, จุกลิ้นปี่, อายุชาย >=40, อายุหญิง >=45
- คำที่ควรแยกออกจากกลุ่มนี้: ปวดท้องบนเด่นให้ดู EMS01, หายใจยากเด่นให้ดู EMS05

## 2. What This Group Is For
ใช้คัดกรองข้อความที่อาการหลักเป็นเจ็บแน่นทรวงอก อาการหัวใจเต้นเร็ว หรือจุกยอดอกตาม PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS07_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.27-28, Module 7, code 7แดง1 | true |
| EMS07_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.27-28, Module 7, code 7แดง2 | true |
| EMS07_RED_03 | อาการแสดงช็อกอย่างน้อย 1 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.27-28, Module 7, code 7แดง3 | true |
| EMS07_RED_04 | หัวใจเต้นเร็ว/ใจสั่นร่วมกับเจ็บแน่น หายใจติดขัด เหงื่อท่วม หรือเกือบหมดสติ | ใจสั่นร่วมกับเจ็บแน่นอกหรือหายใจติดขัดไหม? | yes_no | PDF p.27-28, Module 7, code 7แดง5 | true |
| EMS07_RED_05 | เจ็บแน่นทรวงอกในชายอายุ >=40 หรือหญิงอายุ >=45 | อายุเข้าเกณฑ์ PDF และเจ็บแน่นทรวงอกไหม? | yes_no | PDF p.27-28, Module 7, code 7แดง6-7แดง7 | true |
| EMS07_RED_06 | เครื่องกระตุกหัวใจอัตโนมัติช็อก หรืออายุ >25 ร่วมกับหายใจไม่พอ | มีเครื่องกระตุกหัวใจช็อกหรือหายใจไม่พอร่วมด้วยไหม? | yes_no | PDF p.27-28, Module 7, code 7แดง8-7แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS07_YELLOW_01 | หัวใจเต้นเร็ว/ใจสั่นที่ไม่เข้าเกณฑ์แดง | ใจสั่นแต่ไม่เข้าเกณฑ์แดงใช่ไหม? | yes_no | PDF p.27-28, Module 7, code 7เหลือง1 | true |
| EMS07_YELLOW_02 | เจ็บแน่นทรวงอกในชาย <40 หรือหญิง <45 | อายุต่ำกว่าเกณฑ์แดงแต่มีเจ็บแน่นทรวงอกไหม? | yes_no | PDF p.27-28, Module 7, code 7เหลือง4-7เหลือง5 | true |
| EMS07_YELLOW_03 | จุกเสียดลิ้นปี่ในชาย >=40 หรือหญิง >=45 | จุกเสียดลิ้นปี่และอายุเข้าเกณฑ์ PDF ไหม? | yes_no | PDF p.27-28, Module 7, code 7เหลือง6 | true |
| EMS07_YELLOW_04 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.27-28, Module 7, code 7เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS07_GREEN_01 | เจ็บกล้ามเนื้อหน้าอก/ซี่โครง | เจ็บเหมือนกล้ามเนื้อหน้าอกหรือซี่โครง และไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.27-28, Module 7, code 7เขียว1 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS07_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS07_* | 1 |
| EMS07_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS07_RED_01 | 2 |
| EMS07_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS07_RED_02 | 3 |
| EMS07_Q04 | ใจสั่นแต่ไม่เข้าเกณฑ์แดงใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS07_YELLOW_01 | 4 |
| EMS07_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS07_* | 5 |

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
  "group_id": "EMS07",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
