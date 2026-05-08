---
document_type: ems_symptom_group
group_id: EMS18
group_name_th: "แขนขาอ่อนแรง/พูดลำบาก/ปากเบี้ยว (หลอดเลือดสมองอุดตัน/แตก)"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.68-p.69, Module 18, heading แขนขาอ่อนแรง/พูดลำบาก/ปากเบี้ยว"
needs_human_review: true
---

# EMS18: แขนขาอ่อนแรง/พูดลำบาก/ปากเบี้ยว (หลอดเลือดสมองอุดตัน/แตก)

## 1. Retrieval Keywords
- คำหลัก: แขนขาอ่อนแรง, พูดลำบาก, ปากเบี้ยว, หน้าเบี้ยว, พูดไม่ชัด, เดินไม่ได้
- คำใกล้เคียง: อ่อนแรงซีกเดียว, ยกแขนไม่เท่ากัน, แรงบีบมือไม่เท่ากัน, ภายใน 2 ชั่วโมง, ตั้งแต่ 3 ชั่วโมง
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: แขนขาอ่อนแรง, พูดลำบาก, ปากเบี้ยว, หน้าเบี้ยว, พูดไม่ชัด, เดินไม่ได้, อ่อนแรงซีกเดียว, ยกแขนไม่เท่ากัน
- คำที่ควรแยกออกจากกลุ่มนี้: ปวดหัวเด่นไม่มีอ่อนแรงให้ดู EMS12, เบาหวานเด่นให้ดู EMS09

## 2. What This Group Is For
ใช้คัดกรองอาการแขนขาอ่อนแรง พูดลำบาก หรือปาก/หน้าเบี้ยวตามเกณฑ์ PDF โดยไม่สรุปโรค

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS18_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.68-69, Module 18, code 18แดง1 | true |
| EMS18_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.68-69, Module 18, code 18แดง2 | true |
| EMS18_RED_03 | ระดับความรู้สึกตัวลดลงร่วมกับหายใจผิดปกติ | มีสับสนหรือตอบไม่ตรงร่วมกับหายใจผิดปกติไหม? | yes_no | PDF p.68-69, Module 18, code 18แดง4 | true |
| EMS18_RED_04 | ปวดศีรษะรุนแรงกะทันหันร่วมกับอาการตาม PDF | ปวดหัวรุนแรงทันทีร่วมกับตามัว พูดไม่ชัด อ่อนแรง หรืออาเจียนไหม? | yes_no | PDF p.68-69, Module 18, code 18แดง5 | true |
| EMS18_RED_05 | อ่อนแรง/อัมพาตซีกเดียว <2 ชั่วโมงร่วมกับอาการอย่างน้อย 1 ข้อ | อ่อนแรงซีกเดียวหรือหน้าเบี้ยวเริ่มไม่ถึง 2 ชั่วโมงไหม? | yes_no | PDF p.68-69, Module 18, code 18แดง6 | true |
| EMS18_RED_06 | อายุ >45 ร่วมกับสับสน/พูดลำบาก <3 ชั่วโมง หรือเบาหวาน | อายุเกิน 45 ปีและพูดลำบากหรือสับสนเริ่มไม่ถึง 3 ชั่วโมงไหม? | yes_no | PDF p.68-69, Module 18, code 18แดง7-18แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS18_YELLOW_01 | กล้ามเนื้ออ่อนแรง/ชา/ยืนหรือเดินไม่ได้ | มีแขนขาอ่อนแรง ชา หรือเดินไม่ได้ไหม? | yes_no | PDF p.68-69, Module 18, code 18เหลือง1 | true |
| EMS18_YELLOW_02 | หายใจขัด | หายใจขัดไหม? | yes_no | PDF p.68-69, Module 18, code 18เหลือง2 | true |
| EMS18_YELLOW_03 | อ่อนแรงซีกเดียว >=3 ชั่วโมงร่วมกับอาการที่ PDF ระบุ | อ่อนแรงซีกเดียวหรือหน้าเบี้ยวมานานตั้งแต่ 3 ชั่วโมงไหม? | yes_no | PDF p.68-69, Module 18, code 18เหลือง6 | true |
| EMS18_YELLOW_04 | ตอบไม่ถูกต้อง/พูดไม่ปะติดปะต่อ/พูดลำบาก >=3 ชั่วโมง | พูดลำบากหรือสับสนมานานตั้งแต่ 3 ชั่วโมงไหม? | yes_no | PDF p.68-69, Module 18, code 18เหลือง7 | true |
| EMS18_YELLOW_05 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.68-69, Module 18, code 18เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|


## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS18_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS18_* | 1 |
| EMS18_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS18_RED_01 | 2 |
| EMS18_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS18_RED_02 | 3 |
| EMS18_Q04 | มีแขนขาอ่อนแรง ชา หรือเดินไม่ได้ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS18_YELLOW_01 | 4 |
| EMS18_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS18_* | 5 |

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
  "group_id": "EMS18",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
