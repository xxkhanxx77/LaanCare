---
document_type: ems_symptom_group
group_id: EMS19
group_name_th: "หมดสติ/ไม่ตอบสนอง/หมดสติชั่ววูบ"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.72-p.73, Module 19, heading หมดสติ/ไม่ตอบสนอง/หมดสติชั่ววูบ"
needs_human_review: true
---

# EMS19: หมดสติ/ไม่ตอบสนอง/หมดสติชั่ววูบ

## 1. Retrieval Keywords
- คำหลัก: หมดสติ, ไม่ตอบสนอง, เป็นลม, หมดสติชั่ววูบ, เกือบหมดสติ, ฟุบ
- คำใกล้เคียง: หายใจผิดปกติ, ชัก, เจ็บแน่นทรวงอก, ใจสั่น, เมาสุราไม่ตอบสนอง, เบาหวาน
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: หมดสติ, ไม่ตอบสนอง, เป็นลม, หมดสติชั่ววูบ, เกือบหมดสติ, ฟุบ, หายใจผิดปกติ, ชัก
- คำที่ควรแยกออกจากกลุ่มนี้: หัวใจหยุดเต้น/ไม่หายใจให้ดู EMS06, ชักเด่นให้ดู EMS16

## 2. What This Group Is For
ใช้คัดกรองหมดสติ ไม่ตอบสนอง หรือหมดสติชั่ววูบตาม PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS19_RED_01 | ยืนยันได้ว่าไม่รู้สติ | ยืนยันว่าไม่รู้สติใช่ไหม? | yes_no | PDF p.72-73, Module 19, code 19แดง1 | true |
| EMS19_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจผิดปกติหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.72-73, Module 19, code 19แดง2 | true |
| EMS19_RED_03 | หมดสติชั่ววูบร่วมกับอาการช็อกอย่างน้อย 1 ข้อ | หมดสติชั่ววูบและมีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.72-73, Module 19, code 19แดง3 | true |
| EMS19_RED_04 | ระดับความรู้สึกตัวลดลงหรือไม่ร่วมมือ/ตอบไม่ถูกต้อง | ตอนนี้ตอบคำถามง่าย ๆ ได้ปกติไหม? | yes_no | PDF p.72-73, Module 19, code 19แดง4 | true |
| EMS19_RED_05 | ชัก เจ็บแน่นทรวงอก/ใจสั่นในอายุ >40 เมาสุราไม่ตอบสนอง หรือเบาหวาน | หมดสติร่วมกับชัก เจ็บแน่นอก ใจสั่น หรือเบาหวานไหม? | yes_no | PDF p.72-73, Module 19, code 19แดง6-19แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS19_YELLOW_01 | ไม่ยืนยันการหมดสติ | ยังไม่ยืนยันว่าหมดสติใช่ไหม? | yes_no | PDF p.72-73, Module 19, code 19เหลือง1 | true |
| EMS19_YELLOW_02 | หายใจขัด | หายใจขัดไหม? | yes_no | PDF p.72-73, Module 19, code 19เหลือง2 | true |
| EMS19_YELLOW_03 | หมดสติชั่ววูบร่วมปวดศีรษะ หลายครั้งในวันเดียว หรือครั้งเดียว | วันนี้หมดสติชั่ววูบไหม? | yes_no | PDF p.72-73, Module 19, code 19เหลือง3-19เหลือง5 | true |
| EMS19_YELLOW_04 | ดื่มแอลกอฮอล์ร่วมกับใช้ยาแต่ตอบสนองได้ หรือเมาสุราไม่เข้าแดง | ดื่มแอลกอฮอล์ร่วมกับยาแต่ยังตอบสนองได้ไหม? | yes_no | PDF p.72-73, Module 19, code 19เหลือง7-19เหลือง8 | true |
| EMS19_YELLOW_05 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.72-73, Module 19, code 19เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS19_GREEN_01 | ฟุบอยู่กับพวงมาลัยยานพาหนะ - พิจารณาแจ้งตำรวจ | ฟุบอยู่กับพวงมาลัยยานพาหนะใช่ไหม? | yes_no | PDF p.72-73, Module 19, code 19เขียว1 |
| EMS19_GREEN_02 | เมาสุราโดยไม่มียาอื่นร่วมและตอบสนองได้ | เมาสุราแต่ยังตอบสนองได้และไม่มียาอื่นร่วมใช่ไหม? | yes_no | PDF p.72-73, Module 19, code 19เขียว2 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS19_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS19_* | 1 |
| EMS19_Q02 | ยืนยันว่าไม่รู้สติใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS19_RED_01 | 2 |
| EMS19_Q03 | หายใจผิดปกติหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched | session_mode = self_checkin && user_can_chat = true | EMS19_RED_02 | 3 |
| EMS19_Q04 | ยังไม่ยืนยันว่าหมดสติใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS19_YELLOW_01 | 4 |
| EMS19_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS19_* | 5 |

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
  "group_id": "EMS19",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
