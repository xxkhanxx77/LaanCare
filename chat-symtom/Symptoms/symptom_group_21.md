---
document_type: ems_symptom_group
group_id: EMS21
group_name_th: "ถูกทำร้าย/บาดเจ็บ"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.80-p.81, Module 21, heading ถูกทำร้าย/บาดเจ็บ"
needs_human_review: true
---

# EMS21: ถูกทำร้าย/บาดเจ็บ

## 1. Retrieval Keywords
- คำหลัก: ถูกทำร้าย, บาดเจ็บ, ถูกยิง, ถูกแทง, เลือดออกจากบาดแผล, บาดเจ็บศีรษะ
- คำใกล้เคียง: อาวุธ, บาดแผลเจาะทะลุ, ห้ามเลือดไม่หยุด, กระดูกหักหลายแห่ง, ถูกประทุษร้ายทางเพศ
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ถูกทำร้าย, บาดเจ็บ, ถูกยิง, ถูกแทง, เลือดออกจากบาดแผล, บาดเจ็บศีรษะ, อาวุธ, บาดแผลเจาะทะลุ
- คำที่ควรแยกออกจากกลุ่มนี้: อุบัติเหตุยานยนต์ให้ดู EMS25, พลัดตกหกล้มให้ดู EMS24

## 2. What This Group Is For
ใช้คัดกรองเหตุถูกทำร้ายหรือบาดเจ็บตาม PDF โดยเน้นความปลอดภัย เลือดออก หายใจ และกลไกบาดเจ็บ

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS21_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.80-81, Module 21, code 21แดง1 | true |
| EMS21_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.80-81, Module 21, code 21แดง2 | true |
| EMS21_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.80-81, Module 21, code 21แดง3 | true |
| EMS21_RED_04 | หลังบาดเจ็บมีสติลดลง ตอบไม่ถูกต้อง ชัก หรือขัดขืนอย่างไร้เหตุผล | หลังบาดเจ็บมีสับสน ชัก หรือขัดขืนมากไหม? | yes_no | PDF p.80-81, Module 21, code 21แดง4 | true |
| EMS21_RED_05 | เลือดออกห้ามไม่หยุด ถูกยิง/แทง/บด/บาดแผลเจาะทะลุเหนือมือหรือเท้า หรืออุบัติภัยหมู่ | ถูกยิง ถูกแทง แผลทะลุ หรือเลือดห้ามไม่หยุดไหม? | yes_no | PDF p.80-81, Module 21, code 21แดง5-21แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS21_YELLOW_01 | ถูกยิง/แทง/บด/บาดแผลเจาะทะลุที่มือหรือเท้า | มีแผลยิง แทง บด หรือทะลุที่มือหรือเท้าไหม? | yes_no | PDF p.80-81, Module 21, code 21เหลือง1 | true |
| EMS21_YELLOW_02 | หายใจขัด | หายใจขัดไหม? | yes_no | PDF p.80-81, Module 21, code 21เหลือง2 | true |
| EMS21_YELLOW_03 | บาดเจ็บจากอาวุธไม่รุนแรง กระดูกหักหลายแห่ง หรือหมดสติชั่ววูบหลังบาดเจ็บ | มีกระดูกหักหลายแห่งหรือเคยหมดสติหลังบาดเจ็บไหม? | yes_no | PDF p.80-81, Module 21, code 21เหลือง3-21เหลือง5 | true |
| EMS21_YELLOW_04 | บาดเจ็บไม่ทราบสาเหตุ | บาดเจ็บแต่ไม่ทราบสาเหตุใช่ไหม? | yes_no | PDF p.80-81, Module 21, code 21เหลือง8 | true |
| EMS21_YELLOW_05 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.80-81, Module 21, code 21เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS21_GREEN_01 | แผลฉีกขาดที่ห้ามเลือดได้ | แผลเลือดหยุดแล้วและไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.80-81, Module 21, code 21เขียว1 |
| EMS21_GREEN_02 | บาดเจ็บศีรษะ/ลำคอเล็กน้อย | บาดเจ็บศีรษะหรือลำคอเล็กน้อยไหม? | yes_no | PDF p.80-81, Module 21, code 21เขียว2 |
| EMS21_GREEN_03 | กระดูกหัก/เคลื่อนแห่งเดียว: แขนขา | สงสัยกระดูกแขนหรือขาแห่งเดียวหัก/เคลื่อนไหม? | yes_no | PDF p.80-81, Module 21, code 21เขียว4 |
| EMS21_GREEN_04 | ถูกประทุษร้ายทางเพศ | เหตุเข้ากับถูกประทุษร้ายทางเพศตาม PDF ไหม? | yes_no | PDF p.80-81, Module 21, code 21เขียว5 |
| EMS21_GREEN_05 | ตำรวจร้องขอสนับสนุน/ตรวจสอบ หรือถูกสารป้องกันตัว | ตำรวจร้องขอสนับสนุน หรือถูกสเปรย์พริกไทยไหม? | yes_no | PDF p.80-81, Module 21, code 21เขียว7-21เขียว8 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS21_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS21_* | 1 |
| EMS21_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS21_RED_01 | 2 |
| EMS21_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS21_RED_02 | 3 |
| EMS21_Q04 | มีแผลยิง แทง บด หรือทะลุที่มือหรือเท้าไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS21_YELLOW_01 | 4 |
| EMS21_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS21_* | 5 |

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
  "group_id": "EMS21",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
