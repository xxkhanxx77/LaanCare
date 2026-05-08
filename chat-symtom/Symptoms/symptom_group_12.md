---
document_type: ems_symptom_group
group_id: EMS12
group_name_th: "ปวดศีรษะ/ภาวะผิดปกติของตา/หู/คอ/จมูก"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.44-p.45, Module 12, heading ปวดศีรษะ/ภาวะผิดปกติของตา/หู/คอ/จมูก"
needs_human_review: true
---

# EMS12: ปวดศีรษะ/ภาวะผิดปกติของตา/หู/คอ/จมูก

## 1. Retrieval Keywords
- คำหลัก: ปวดศีรษะ, ปวดหัว, เวียนศีรษะ, มองเห็นยาก, เห็นภาพซ้อน, ปวดตา, ปวดหู, เจ็บคอ
- คำใกล้เคียง: ปวดศีรษะรุนแรงฉับพลัน, พูดเสียงพร่า, เห็นภาพมัว, อ่อนแรง, อาเจียน
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ปวดศีรษะ, ปวดหัว, เวียนศีรษะ, มองเห็นยาก, เห็นภาพซ้อน, ปวดตา, ปวดหู, เจ็บคอ
- คำที่ควรแยกออกจากกลุ่มนี้: แขนขาอ่อนแรง/พูดลำบากเด่นให้ดู EMS18, บาดเจ็บศีรษะเด่นให้ดู EMS21/EMS24

## 2. What This Group Is For
ใช้คัดกรองอาการปวดศีรษะหรืออาการผิดปกติของตา หู คอ จมูกตามเกณฑ์ PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS12_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.44-45, Module 12, code 12แดง1 | true |
| EMS12_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.44-45, Module 12, code 12แดง2 | true |
| EMS12_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.44-45, Module 12, code 12แดง3 | true |
| EMS12_RED_04 | ระดับความรู้สึกตัวลดลงหรือไม่ร่วมมือ/ตอบไม่ถูกต้อง | ตอบคำถามง่าย ๆ ได้ปกติไหม? | yes_no | PDF p.44-45, Module 12, code 12แดง4 | true |
| EMS12_RED_05 | ปวดศีรษะรุนแรงฉับพลันร่วมกับพูดเสียงพร่า เห็นภาพมัว/ซ้อน อ่อนแรง เหงื่อท่วม หรืออาเจียน | ปวดหัวรุนแรงทันทีร่วมกับตามัว พูดพร่า อ่อนแรง หรืออาเจียนไหม? | yes_no | PDF p.44-45, Module 12, code 12แดง5 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS12_YELLOW_01 | ตอบไม่ถูกต้องแต่ยังพูดและเดินได้ | มีสับสนแต่ยังพูดและเดินได้ไหม? | yes_no | PDF p.44-45, Module 12, code 12เหลือง1 | true |
| EMS12_YELLOW_02 | หายใจขัด | หายใจขัดไหม? | yes_no | PDF p.44-45, Module 12, code 12เหลือง2 | true |
| EMS12_YELLOW_03 | มองเห็นยากลำบาก | มองเห็นลำบากไหม? | yes_no | PDF p.44-45, Module 12, code 12เหลือง4 | true |
| EMS12_YELLOW_04 | เวียนศีรษะ | เวียนศีรษะไหม? | yes_no | PDF p.44-45, Module 12, code 12เหลือง5 | true |
| EMS12_YELLOW_05 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.44-45, Module 12, code 12เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS12_GREEN_01 | ปวดศีรษะหลังบาดเจ็บศีรษะที่ไม่เข้าเกณฑ์แดง | ปวดหัวหลังบาดเจ็บศีรษะ แต่ไม่เข้าเกณฑ์แดงใช่ไหม? | yes_no | PDF p.44-45, Module 12, code 12เขียว1 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS12_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS12_* | 1 |
| EMS12_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS12_RED_01 | 2 |
| EMS12_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS12_RED_02 | 3 |
| EMS12_Q04 | มีสับสนแต่ยังพูดและเดินได้ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS12_YELLOW_01 | 4 |
| EMS12_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS12_* | 5 |

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
  "group_id": "EMS12",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
