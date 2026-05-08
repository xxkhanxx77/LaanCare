---
document_type: ems_symptom_group
group_id: EMS24
group_name_th: "พลัดตกหกล้ม/อุบัติเหตุ/เจ็บปวด"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.92-p.93, Module 24, heading พลัดตกหกล้ม/อุบัติเหตุ/เจ็บปวด"
needs_human_review: true
---

# EMS24: พลัดตกหกล้ม/อุบัติเหตุ/เจ็บปวด

## 1. Retrieval Keywords
- คำหลัก: หกล้ม, ตกจากที่สูง, อุบัติเหตุ, เจ็บปวด, แขนขาถูกตัดขาด, กระดูกหัก
- คำใกล้เคียง: เลือดออกห้ามไม่หยุด, อัมพาต, ตกจากที่สูง, นิ้วถูกตัดขาด, กระดูกต้นขาหัก, สะโพกหัก
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: หกล้ม, ตกจากที่สูง, อุบัติเหตุ, เจ็บปวด, แขนขาถูกตัดขาด, กระดูกหัก, เลือดออกห้ามไม่หยุด, อัมพาต
- คำที่ควรแยกออกจากกลุ่มนี้: ยานยนต์ให้ดู EMS25, ถูกทำร้ายให้ดู EMS21

## 2. What This Group Is For
ใช้คัดกรองการพลัดตก หกล้ม อุบัติเหตุทั่วไป หรือเจ็บปวดจากบาดเจ็บตาม PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS24_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.92-93, Module 24, code 24แดง1 | true |
| EMS24_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.92-93, Module 24, code 24แดง2 | true |
| EMS24_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.92-93, Module 24, code 24แดง3 | true |
| EMS24_RED_04 | หลังบาดเจ็บมีสติลดลง ชัก ตอบไม่ถูกต้อง ขัดขืน หรือเลือดออกห้ามไม่หยุด | หลังเหตุมีสับสน ชัก หรือเลือดห้ามไม่หยุดไหม? | yes_no | PDF p.92-93, Module 24, code 24แดง4-24แดง5 | true |
| EMS24_RED_05 | ถูกตัดขาด/บดคาเหนือระดับนิ้ว อัมพาต หรืออุบัติภัยหมู่ | มีอวัยวะถูกตัด/บดคา อัมพาต หรืออุบัติภัยหมู่ไหม? | yes_no | PDF p.92-93, Module 24, code 24แดง7-24แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS24_YELLOW_01 | หมดสติชั่ววูบครั้งเดียว หายใจขัด หรือนิ้วมือ/เท้าถูกตัดขาด/บดติด | หมดสติชั่ววูบ หายใจขัด หรือมีนิ้วถูกตัด/บดไหม? | yes_no | PDF p.92-93, Module 24, code 24เหลือง1-24เหลือง3 | true |
| EMS24_YELLOW_02 | กระดูกหักหลายตำแหน่ง/ต้นขา/สะโพก บาดเจ็บศีรษะคอไหล่เล็กน้อย หรือติดคาไม่มีบาดเจ็บชัดเจน | มีกระดูกหักหลายตำแหน่งหรือบาดเจ็บศีรษะ/คอ/ไหล่ไหม? | yes_no | PDF p.92-93, Module 24, code 24เหลือง4-24เหลือง6 | true |
| EMS24_YELLOW_03 | หกล้มเกี่ยวเนื่องกับเจ็บแน่นทรวงอก เวียนศีรษะ ปวดศีรษะ หรือเบาหวาน | ก่อนล้มมีเจ็บแน่นอก เวียนหัว ปวดหัว หรือเกี่ยวกับเบาหวานไหม? | yes_no | PDF p.92-93, Module 24, code 24เหลือง7 | true |
| EMS24_YELLOW_04 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.92-93, Module 24, code 24เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS24_GREEN_01 | แผลฉีกขาดน่ากลัวแต่ห้ามเลือดได้แล้ว | แผลดูน่ากลัวแต่เลือดหยุดแล้วใช่ไหม? | yes_no | PDF p.92-93, Module 24, code 24เขียว1 |
| EMS24_GREEN_02 | เจ็บปวดสะโพก | เจ็บสะโพกแต่ไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.92-93, Module 24, code 24เขียว2 |
| EMS24_GREEN_03 | พลัดตกจากที่สูงกว่า 5 เมตร | ตกจากที่สูงกว่า 5 เมตรแต่ไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.92-93, Module 24, code 24เขียว3 |
| EMS24_GREEN_04 | แขนขาหัก/เคลื่อนตำแหน่งเดียว | สงสัยแขนหรือขาหัก/เคลื่อนแห่งเดียวไหม? | yes_no | PDF p.92-93, Module 24, code 24เขียว4 |
| EMS24_GREEN_05 | ผู้ป่วย/ผู้แจ้งยืนยันขอให้ช่วย | ยังขอให้ช่วยแต่ไม่เข้าเกณฑ์แดง/เหลืองใช่ไหม? | yes_no | PDF p.92-93, Module 24, code 24เขียว6 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS24_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS24_* | 1 |
| EMS24_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS24_RED_01 | 2 |
| EMS24_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS24_RED_02 | 3 |
| EMS24_Q04 | หมดสติชั่ววูบ หายใจขัด หรือมีนิ้วถูกตัด/บดไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS24_YELLOW_01 | 4 |
| EMS24_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS24_* | 5 |

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
  "group_id": "EMS24",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
