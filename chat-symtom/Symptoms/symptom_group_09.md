---
document_type: ems_symptom_group
group_id: EMS09
group_name_th: "เบาหวาน"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.35, Module 9, heading เบาหวาน"
needs_human_review: true
---

# EMS09: เบาหวาน

## 1. Retrieval Keywords
- คำหลัก: เบาหวาน, น้ำตาล, อินซูลิน, ฉีดอินซูลิน, อ่อนเพลียจากเบาหวาน
- คำใกล้เคียง: เจ็บแน่นทรวงอก, ชัก, ระดับความรู้สึกตัวลดลง, พฤติกรรมเปลี่ยน, ไม่สบายไม่จำเพาะ
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: เบาหวาน, น้ำตาล, อินซูลิน, ฉีดอินซูลิน, อ่อนเพลียจากเบาหวาน, เจ็บแน่นทรวงอก, ชัก, ระดับความรู้สึกตัวลดลง
- คำที่ควรแยกออกจากกลุ่มนี้: ชักเด่นให้ดู EMS16, หมดสติเด่นให้ดู EMS19

## 2. What This Group Is For
ใช้คัดกรองผู้ที่ระบุเบาหวานหรือเกี่ยวกับอินซูลิน/น้ำตาล โดยใช้เฉพาะระดับความเสี่ยงจาก PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS09_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.35, Module 9, code 9แดง1 | true |
| EMS09_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.35, Module 9, code 9แดง2 | true |
| EMS09_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.35, Module 9, code 9แดง3 | true |
| EMS09_RED_04 | ระดับความรู้สึกตัวลดลงหรือไม่ร่วมมือ | ตอบคำถามง่าย ๆ ได้ปกติไหม? | yes_no | PDF p.35, Module 9, code 9แดง4 | true |
| EMS09_RED_05 | เจ็บแน่นทรวงอกหรือชัก | มีเจ็บแน่นทรวงอกหรือชักไหม? | yes_no | PDF p.35, Module 9, code 9แดง5-9แดง6 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS09_YELLOW_01 | ตอบเวลา/สถานที่/บุคคลไม่ถูกต้องหรือพฤติกรรมเปลี่ยน | มีพฤติกรรมต่างจากเดิมหรือตอบไม่ตรงไหม? | yes_no | PDF p.35, Module 9, code 9เหลือง1 | true |
| EMS09_YELLOW_02 | รู้สึกไม่สบาย อาการไม่จำเพาะ | รู้สึกไม่สบายแบบบอกอาการชัดไม่ได้ไหม? | yes_no | PDF p.35, Module 9, code 9เหลือง3 | true |
| EMS09_YELLOW_03 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.35, Module 9, code 9เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|


## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS09_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS09_* | 1 |
| EMS09_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS09_RED_01 | 2 |
| EMS09_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS09_RED_02 | 3 |
| EMS09_Q04 | มีพฤติกรรมต่างจากเดิมหรือตอบไม่ตรงไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS09_YELLOW_01 | 4 |
| EMS09_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS09_* | 5 |

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
  "group_id": "EMS09",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
