---
document_type: ems_symptom_group
group_id: EMS16
group_name_th: "ชัก"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.60-p.61, Module 16, heading ชัก"
needs_human_review: true
---

# EMS16: ชัก

## 1. Retrieval Keywords
- คำหลัก: ชัก, กำลังชัก, ชักหลายครั้ง, ชักครั้งแรก, หลังชักไม่หายใจ
- คำใกล้เคียง: นานกว่า 5 นาที, มากกว่า 3 ครั้งต่อชั่วโมง, หลังบาดเจ็บศีรษะ 24 ชั่วโมง, หญิงมีครรภ์ >20 สัปดาห์, เบาหวาน
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ชัก, กำลังชัก, ชักหลายครั้ง, ชักครั้งแรก, หลังชักไม่หายใจ, นานกว่า 5 นาที, มากกว่า 3 ครั้งต่อชั่วโมง, หลังบาดเจ็บศีรษะ 24 ชั่วโมง
- คำที่ควรแยกออกจากกลุ่มนี้: เด็กเป็นหลักให้ดู EMS20, ตั้งครรภ์เป็นหลักให้ดู EMS15

## 2. What This Group Is For
ใช้คัดกรองเหตุชักตามเกณฑ์ PDF โดยถามเฉพาะเพื่อจัดระดับ check-in/alert

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS16_RED_01 | ไม่หายใจหลังหยุดชัก | หลังหยุดชักแล้วยังไม่หายใจไหม? | yes_no | PDF p.60-61, Module 16, code 16แดง1 | true |
| EMS16_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หลังชักมีหายใจลำบากมากไหม? | yes_no | PDF p.60-61, Module 16, code 16แดง2 | true |
| EMS16_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.60-61, Module 16, code 16แดง3 | true |
| EMS16_RED_04 | กำลังชักนาน >5 นาที หรือชักหลายครั้ง >3 ครั้งต่อชั่วโมง | กำลังชักนานเกิน 5 นาที หรือชักเกิน 3 ครั้งใน 1 ชั่วโมงไหม? | yes_no | PDF p.60-61, Module 16, code 16แดง4-16แดง5 | true |
| EMS16_RED_05 | ชักหลังบาดเจ็บศีรษะ ปวดศีรษะรุนแรงก่อนชัก จากแอลกอฮอล์/ยา หญิงครรภ์ >20 สัปดาห์ หรือเบาหวาน | ชักร่วมกับบาดเจ็บศีรษะ ตั้งครรภ์เกิน 20 สัปดาห์ หรือเบาหวานไหม? | yes_no | PDF p.60-61, Module 16, code 16แดง6-16แดง10 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS16_YELLOW_01 | ชักครั้งแรกในชีวิต | เป็นการชักครั้งแรกในชีวิตไหม? | yes_no | PDF p.60-61, Module 16, code 16เหลือง1 | true |
| EMS16_YELLOW_02 | ชักในผู้ที่เคยชักมาก่อน | เคยชักมาก่อนและครั้งนี้ชักอีกใช่ไหม? | yes_no | PDF p.60-61, Module 16, code 16เหลือง4 | true |
| EMS16_YELLOW_03 | ไม่ทราบประวัติว่าเคยชักมาก่อนหรือไม่ | ไม่ทราบว่าเคยชักมาก่อนหรือไม่ใช่ไหม? | yes_no | PDF p.60-61, Module 16, code 16เหลือง5 | true |
| EMS16_YELLOW_04 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.60-61, Module 16, code 16เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|


## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS16_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS16_* | 1 |
| EMS16_Q02 | หลังหยุดชักแล้วยังไม่หายใจไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS16_RED_01 | 2 |
| EMS16_Q03 | หลังชักมีหายใจลำบากมากไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched | session_mode = self_checkin && user_can_chat = true | EMS16_RED_02 | 3 |
| EMS16_Q04 | เป็นการชักครั้งแรกในชีวิตไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched | session_mode = self_checkin && user_can_chat = true | EMS16_YELLOW_01 | 4 |
| EMS16_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS16_* | 5 |

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
  "group_id": "EMS16",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
