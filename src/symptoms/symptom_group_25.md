---
document_type: ems_symptom_group
group_id: EMS25
group_name_th: "อุบัติเหตุยานยนต์"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.96, Module 25, heading อุบัติเหตุยานยนต์"
needs_human_review: true
---

# EMS25: อุบัติเหตุยานยนต์

## 1. Retrieval Keywords
- คำหลัก: รถชน, อุบัติเหตุรถ, รถล้ม, มอเตอร์ไซค์ชน, คนเดินถูกรถชน, รถพลิกคว่ำ
- คำใกล้เคียง: กระเด็นออกจากพาหนะ, ความเร็วสูง, ชนประสานงา, t-bone, ติดอยู่ในรถ, อุบัติภัยหมู่
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: รถชน, อุบัติเหตุรถ, รถล้ม, มอเตอร์ไซค์ชน, คนเดินถูกรถชน, รถพลิกคว่ำ, กระเด็นออกจากพาหนะ, ความเร็วสูง
- คำที่ควรแยกออกจากกลุ่มนี้: พลัดตกหกล้มไม่เกี่ยวกับยานยนต์ให้ดู EMS24

## 2. What This Group Is For
ใช้คัดกรองอุบัติเหตุยานยนต์ตาม PDF โดยเน้นการตอบสนอง หายใจ ช็อก เลือดออก และกลไกชน

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS25_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.96, Module 25, code 25แดง1 | true |
| EMS25_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.96, Module 25, code 25แดง2 | true |
| EMS25_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.96, Module 25, code 25แดง3 | true |
| EMS25_RED_04 | หลังบาดเจ็บมีสติลดลง ชัก ตอบไม่ถูกต้อง ขัดขืน หรือเลือดออกห้ามไม่หยุด | หลังเหตุมีสับสน ชัก หรือเลือดห้ามไม่หยุดไหม? | yes_no | PDF p.96, Module 25, code 25แดง4-25แดง5 | true |
| EMS25_RED_05 | กระเด็นออกจากพาหนะ ความเร็วสูงชนตามกลไก PDF หรืออุบัติภัยหมู่ | มีคนกระเด็นออกจากรถ รถชนแรง หรือเข้าเกณฑ์อุบัติภัยหมู่ไหม? | yes_no | PDF p.96, Module 25, code 25แดง7-25แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS25_YELLOW_01 | อุบัติเหตุบาดเจ็บ: พาหนะความเร็วต่ำ ผู้ประสบภัยเดินได้ หรือไม่ทราบบาดเจ็บที่ใด | เป็นอุบัติเหตุรถความเร็วต่ำ หรือผู้บาดเจ็บเดินได้ไหม? | yes_no | PDF p.96, Module 25, code 25เหลือง1 | true |
| EMS25_YELLOW_02 | รถพลิกคว่ำ | รถพลิกคว่ำไหม? | yes_no | PDF p.96, Module 25, code 25เหลือง2 | true |
| EMS25_YELLOW_03 | ผู้ประสบภัยยังติดอยู่ในรถ | ยังมีคนติดอยู่ในรถไหม? | yes_no | PDF p.96, Module 25, code 25เหลือง4 | true |
| EMS25_YELLOW_04 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.96, Module 25, code 25เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|


## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS25_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS25_* | 1 |
| EMS25_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS25_RED_01 | 2 |
| EMS25_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS25_RED_02 | 3 |
| EMS25_Q04 | เป็นอุบัติเหตุรถความเร็วต่ำ หรือผู้บาดเจ็บเดินได้ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS25_YELLOW_01 | 4 |
| EMS25_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS25_* | 5 |

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
  "group_id": "EMS25",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
