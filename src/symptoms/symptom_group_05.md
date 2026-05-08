---
document_type: ems_symptom_group
group_id: EMS05
group_name_th: "หายใจยากลำบาก"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.19-p.20, Module 5, heading หายใจยากลำบาก"
needs_human_review: true
---

# EMS05: หายใจยากลำบาก

## 1. Retrieval Keywords
- คำหลัก: หายใจยาก, หายใจลำบาก, หายใจไม่อิ่ม, หายใจขัด, แน่นหายใจ, ไอคล้ายเห่า
- คำใกล้เคียง: ต้องลุกนั่ง, โน้มตัวหายใจ, พูดประโยคสั้น, เจ็บทรวงอกร่วมกับหายใจยาก, สเปรย์พริกไทย
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: หายใจยาก, หายใจลำบาก, หายใจไม่อิ่ม, หายใจขัด, แน่นหายใจ, ไอคล้ายเห่า, ต้องลุกนั่ง, โน้มตัวหายใจ
- คำที่ควรแยกออกจากกลุ่มนี้: สำลักอุดทางหายใจให้ดู EMS08, ปฏิกิริยาภูมิแพ้ให้ดู EMS02

## 2. What This Group Is For
ใช้คัดกรองข้อความที่อาการหลักเป็นหายใจยากลำบากหรือหายใจขัดตาม PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS05_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.19-20, Module 5, code 5แดง1 | true |
| EMS05_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | ต้องนั่งพิงหรือพูดได้แค่ประโยคสั้น ๆ เพื่อหายใจไหม? | yes_no | PDF p.19-20, Module 5, code 5แดง2 | true |
| EMS05_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.19-20, Module 5, code 5แดง3 | true |
| EMS05_RED_04 | ระดับความรู้สึกตัวลดลง/ตอบไม่ถูกต้อง | ตอบคำถามง่าย ๆ ได้ปกติไหม? | yes_no | PDF p.19-20, Module 5, code 5แดง4 | true |
| EMS05_RED_05 | หายใจยากร่วมกับเจ็บทรวงอกในอายุ >25 | อายุเกิน 25 ปีและหายใจยากร่วมกับเจ็บแน่นทรวงอกไหม? | yes_no | PDF p.19-20, Module 5, code 5แดง6 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS05_YELLOW_01 | รู้สึกซ่าหรือชาที่แขนขาหรือรอบปาก | มีชา หรือซ่ารอบปากหรือแขนขาไหม? | yes_no | PDF p.19-20, Module 5, code 5เหลือง1 | true |
| EMS05_YELLOW_02 | หายใจขัด | หายใจขัดไหม? | yes_no | PDF p.19-20, Module 5, code 5เหลือง2 | true |
| EMS05_YELLOW_03 | หายใจขัดร่วมกับไอคล้ายเห่า อายุ <= 6 | เด็กอายุไม่เกิน 6 ปีมีไอคล้ายเห่าและหายใจขัดไหม? | yes_no | PDF p.19-20, Module 5, code 5เหลือง4 | true |
| EMS05_YELLOW_04 | เจ็บขณะหายใจ | เจ็บตอนหายใจไหม? | yes_no | PDF p.19-20, Module 5, code 5เหลือง5 | true |
| EMS05_YELLOW_05 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.19-20, Module 5, code 5เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS05_GREEN_01 | ออกซิเจนหมดถัง | ใช้ออกซิเจนที่บ้านแล้วถังหมดใช่ไหม? | yes_no | PDF p.19-20, Module 5, code 5เขียว1 |
| EMS05_GREEN_02 | ภาวะระบายลมหายใจเกิน/ตื่นตระหนกในผู้ที่เคยมีอาการเช่นนี้มาก่อน | เคยมีอาการตื่นตระหนกแบบนี้มาก่อนและตอนนี้ไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.19-20, Module 5, code 5เขียว4 |
| EMS05_GREEN_03 | ผู้ป่วย/ผู้แจ้งขอให้ช่วยโดยไม่เข้าเกณฑ์แดงหรือเหลือง | ยังต้องการให้ช่วย แต่ไม่มีอาการเข้าเกณฑ์แดงหรือเหลืองใช่ไหม? | yes_no | PDF p.19-20, Module 5, code 5เขียว6 |
| EMS05_GREEN_04 | ถูกสารป้องกันตัว เช่น สเปรย์พริกไทย | ถูกสเปรย์พริกไทยหรือสารป้องกันตัวและไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.19-20, Module 5, code 5เขียว8 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS05_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS05_* | 1 |
| EMS05_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS05_RED_01 | 2 |
| EMS05_Q03 | ต้องนั่งพิงหรือพูดได้แค่ประโยคสั้น ๆ เพื่อหายใจไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS05_RED_02 | 3 |
| EMS05_Q04 | มีชา หรือซ่ารอบปากหรือแขนขาไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS05_YELLOW_01 | 4 |
| EMS05_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS05_* | 5 |

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
  "group_id": "EMS05",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
