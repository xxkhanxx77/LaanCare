---
document_type: ems_symptom_group
group_id: EMS10
group_name_th: "ภยันตรายจากสภาพแวดล้อม"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.39-p.40, Module 10, heading ภยันตรายจากสภาพแวดล้อม"
needs_human_review: true
---

# EMS10: ภยันตรายจากสภาพแวดล้อม

## 1. Retrieval Keywords
- คำหลัก: ความร้อน, ความเย็น, สารเคมี, ควัน, สภาพแวดล้อม, สเปรย์พริกไทย
- คำใกล้เคียง: ออกกำลังกายหนัก, ตัวร้อนจัด, ควัน, สารเคมีกิน/ราด/สาด, หนาวสั่นควบคุมไม่ได้
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ความร้อน, ความเย็น, สารเคมี, ควัน, สภาพแวดล้อม, สเปรย์พริกไทย, ออกกำลังกายหนัก, ตัวร้อนจัด
- คำที่ควรแยกออกจากกลุ่มนี้: แผลไหม้/ลวกชัดเจนให้ดู EMS22, ยา/สารเข้าร่างกายให้ดู EMS14

## 2. What This Group Is For
ใช้คัดกรองอันตรายจากความร้อน ความเย็น ควัน หรือสารเคมีตามเกณฑ์ PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS10_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.39-40, Module 10, code 10แดง1 | true |
| EMS10_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ รวมถึงตัว/ริมฝีปากเขียวคล้ำ | หายใจลำบากมากหรือริมฝีปากเขียวคล้ำไหม? | yes_no | PDF p.39-40, Module 10, code 10แดง2 | true |
| EMS10_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.39-40, Module 10, code 10แดง3 | true |
| EMS10_RED_04 | ออกกำลังกายหนัก/อยู่ในที่ร้อนจัดร่วมกับเลือดออกผิดปกติ ชัก หรืออาการอุณหพาตตาม PDF | อยู่ในที่ร้อนจัดแล้วมีชัก เลือดออกผิดปกติ หรืออาการหนักไหม? | yes_no | PDF p.39-40, Module 10, code 10แดง5-10แดง8 | true |
| EMS10_RED_05 | เจ็บแน่นหน้าอก/จุกเสียดลิ้นปี่ | มีเจ็บแน่นหน้าอกหรือจุกลิ้นปี่ไหม? | yes_no | PDF p.39-40, Module 10, code 10แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS10_YELLOW_01 | อยู่ในที่ร้อนจัดและตัวร้อนจัด | อยู่ในที่ร้อนจัดและตัวร้อนจัดไหม? | yes_no | PDF p.39-40, Module 10, code 10เหลือง1 | true |
| EMS10_YELLOW_02 | ถูกควัน/หายใจขัด | โดนควันและหายใจขัดไหม? | yes_no | PDF p.39-40, Module 10, code 10เหลือง2 | true |
| EMS10_YELLOW_03 | อยู่ในที่ร้อนจัดและมีอาการอุณหพาตอย่างน้อย 1 ข้อ | อยู่ในที่ร้อนจัดแล้วอาเจียน เป็นตะคริวรุนแรง แน่นหน้าอก หรือปวดท้องไหม? | yes_no | PDF p.39-40, Module 10, code 10เหลือง3 | true |
| EMS10_YELLOW_04 | สารเคมีหรือความเย็นจัดหรือภยันตรายอื่นที่ไม่เข้าแดง | สัมผัสสารเคมีหรือความเย็นจัดและยังมีอาการไหม? | yes_no | PDF p.39-40, Module 10, code 10เหลือง4-10เหลือง6 | true |
| EMS10_YELLOW_05 | ไม่ได้ข้อมูลยืนยันจากผู้แจ้ง | ยืนยันรายละเอียดเหตุไม่ได้ใช่ไหม? | yes_no | PDF p.39-40, Module 10, code 10เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS10_GREEN_01 | ภยันตรายอื่นแต่อาการไม่รุนแรง/ไม่จำเพาะ | ได้รับภยันตรายแต่ไม่มีอาการรุนแรงหรือชัดเจนไหม? | yes_no | PDF p.39-40, Module 10, code 10เขียว2 |
| EMS10_GREEN_02 | ถูกสารป้องกันตัว เช่น สเปรย์พริกไทย | ถูกสเปรย์พริกไทยหรือสารป้องกันตัวและไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.39-40, Module 10, code 10เขียว8 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS10_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS10_* | 1 |
| EMS10_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS10_RED_01 | 2 |
| EMS10_Q03 | หายใจลำบากมากหรือริมฝีปากเขียวคล้ำไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS10_RED_02 | 3 |
| EMS10_Q04 | อยู่ในที่ร้อนจัดและตัวร้อนจัดไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS10_YELLOW_01 | 4 |
| EMS10_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS10_* | 5 |

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
  "group_id": "EMS10",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
