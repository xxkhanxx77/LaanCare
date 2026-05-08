---
document_type: ems_symptom_group
group_id: EMS17
group_name_th: "ป่วย/อ่อนเพลีย (ไม่จำเพาะ/ไม่ทราบสาเหตุ)/อื่นๆ"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.64-p.65, Module 17, heading ป่วย/อ่อนเพลีย (ไม่จำเพาะ/ไม่ทราบสาเหตุ)/อื่นๆ"
needs_human_review: true
---

# EMS17: ป่วย/อ่อนเพลีย (ไม่จำเพาะ/ไม่ทราบสาเหตุ)/อื่นๆ

## 1. Retrieval Keywords
- คำหลัก: ป่วย, อ่อนเพลีย, ไม่สบาย, เวียนศีรษะ, อ่อนแรงทั่วร่างกาย, อาการไม่จำเพาะ
- คำใกล้เคียง: อาการไม่ทราบสาเหตุ, หน่วยเฝ้าระวังสุขภาพ, วางสาย, เจ็บปวดทั่วร่างกาย
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ป่วย, อ่อนเพลีย, ไม่สบาย, เวียนศีรษะ, อ่อนแรงทั่วร่างกาย, อาการไม่จำเพาะ, อาการไม่ทราบสาเหตุ, หน่วยเฝ้าระวังสุขภาพ
- คำที่ควรแยกออกจากกลุ่มนี้: อาการเข้ากลุ่มเฉพาะอื่นให้เลือกกลุ่มนั้นก่อน

## 2. What This Group Is For
ใช้คัดกรองอาการทั่วไปหรือไม่จำเพาะ เฉพาะเมื่อไม่เข้าอาการนำกลุ่มอื่น และใช้ตาม PDF เท่านั้น

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS17_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.64-65, Module 17, code 17แดง1 | true |
| EMS17_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.64-65, Module 17, code 17แดง2 | true |
| EMS17_RED_03 | อาการแสดงช็อกอย่างน้อย 1 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.64-65, Module 17, code 17แดง3 | true |
| EMS17_RED_04 | ระดับความรู้สึกตัวลดลงหรือไม่ร่วมมือ/ตอบไม่ถูกต้อง | ตอบคำถามง่าย ๆ ได้ปกติไหม? | yes_no | PDF p.64-65, Module 17, code 17แดง4 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS17_YELLOW_01 | เวียนศีรษะ/การทรงตัวผิดปกติ | เวียนศีรษะหรือทรงตัวผิดปกติไหม? | yes_no | PDF p.64-65, Module 17, code 17เหลือง4 | true |
| EMS17_YELLOW_02 | อ่อนแรงทั่วร่างกาย/เจ็บปวดทั่วร่างกาย | อ่อนแรงหรือเจ็บปวดทั่วร่างกายไหม? | yes_no | PDF p.64-65, Module 17, code 17เหลือง5 | true |
| EMS17_YELLOW_03 | องค์กร/ผู้เฝ้าระวังสุขภาพยืนยันภาวะฉุกเฉินการแพทย์ | มีหน่วยงานยืนยันภาวะฉุกเฉินการแพทย์ไหม? | yes_no | PDF p.64-65, Module 17, code 17เหลือง7 | true |
| EMS17_YELLOW_04 | อื่น ๆ ที่พิจารณาว่าอาจวิกฤต | มีอาการอื่นที่ดูอาจวิกฤตตาม PDF ไหม? | yes_no | PDF p.64-65, Module 17, code 17เหลือง8 | true |
| EMS17_YELLOW_05 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.64-65, Module 17, code 17เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS17_GREEN_01 | วางหูโทรศัพท์/เงียบหายไป - พิจารณาแจ้งตำรวจ | สายเงียบหรือวางสายระหว่างแจ้งเหตุใช่ไหม? | yes_no | PDF p.64-65, Module 17, code 17เขียว5 |
| EMS17_GREEN_02 | ผู้ป่วย/ผู้แจ้งยืนยันขอให้ช่วย | ยังขอให้ช่วยแต่ไม่เข้าเกณฑ์แดง/เหลืองใช่ไหม? | yes_no | PDF p.64-65, Module 17, code 17เขียว6 |
| EMS17_GREEN_03 | องค์กร/ผู้เฝ้าระวังสุขภาพยืนยันภาวะไม่วิกฤตหรือไม่มีรายละเอียด | หน่วยงานแจ้งว่าไม่วิกฤตหรือไม่มีรายละเอียดใช่ไหม? | yes_no | PDF p.64-65, Module 17, code 17เขียว7 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS17_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS17_* | 1 |
| EMS17_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS17_RED_01 | 2 |
| EMS17_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS17_RED_02 | 3 |
| EMS17_Q04 | เวียนศีรษะหรือทรงตัวผิดปกติไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS17_YELLOW_01 | 4 |
| EMS17_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS17_* | 5 |

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
  "group_id": "EMS17",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
