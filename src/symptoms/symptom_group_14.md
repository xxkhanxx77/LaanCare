---
document_type: ems_symptom_group
group_id: EMS14
group_name_th: "ยาเกินขนาด/ได้รับพิษ"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.52-p.53, Module 14, heading ยาเกินขนาด/ได้รับพิษ"
needs_human_review: true
---

# EMS14: ยาเกินขนาด/ได้รับพิษ

## 1. Retrieval Keywords
- คำหลัก: ยาเกินขนาด, ได้รับพิษ, กินยา, กินสาร, เมาสุรา, สารกัดกร่อน, สารเคมี
- คำใกล้เคียง: กินมา <2 ชั่วโมง, ถอนยา, ชัก, ไม่ตอบสนองต่อสิ่งเร้า, กลืนลำบาก, ยาเพื่อความเพลิดเพลิน
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ยาเกินขนาด, ได้รับพิษ, กินยา, กินสาร, เมาสุรา, สารกัดกร่อน, สารเคมี, กินมา <2 ชั่วโมง
- คำที่ควรแยกออกจากกลุ่มนี้: สารเคมีภายนอก/สภาพแวดล้อมให้ดู EMS10, แผลไหม้สารเคมีให้ดู EMS22

## 2. What This Group Is For
ใช้คัดกรองการกินยา/สาร สารพิษ แอลกอฮอล์ หรือสารกัดกร่อนตาม PDF โดยไม่ให้คำแนะนำการรักษา

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS14_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.52-53, Module 14, code 14แดง1 | true |
| EMS14_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.52-53, Module 14, code 14แดง2 | true |
| EMS14_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.52-53, Module 14, code 14แดง3 | true |
| EMS14_RED_04 | กินยาที่ใช้บำบัดรักษาภายใน <2 ชั่วโมง | กินยาที่ใช้รักษาภายใน 2 ชั่วโมงที่ผ่านมาไหม? | yes_no | PDF p.52-53, Module 14, code 14แดง5 | true |
| EMS14_RED_05 | ชักจากแอลกอฮอล์/ยา เพ้อคลุ้มคลั่ง เมาสุราไม่ตอบสนอง หรือกินสารกัดกร่อนร่วมกับกลืนลำบาก | มีชัก ไม่ตอบสนอง หรือกลืนลำบากหลังได้รับยา/สารไหม? | yes_no | PDF p.52-53, Module 14, code 14แดง6-14แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS14_YELLOW_01 | กินยา/สารหรือสารเคมีที่ไม่เข้าแดงตามเงื่อนไขเวลาและชนิดสาร | กินยา/สารเข้าไปแต่ยังไม่เข้าเกณฑ์แดงใช่ไหม? | yes_no | PDF p.52-53, Module 14, code 14เหลือง1-14เหลือง5 | true |
| EMS14_YELLOW_02 | หายใจขัด | หายใจขัดไหม? | yes_no | PDF p.52-53, Module 14, code 14เหลือง2 | true |
| EMS14_YELLOW_03 | อาการผิดปกติจากยาไม่ทราบชนิด | มีอาการผิดปกติจากยาแต่ไม่รู้ว่าเป็นยาอะไรไหม? | yes_no | PDF p.52-53, Module 14, code 14เหลือง6 | true |
| EMS14_YELLOW_04 | แอลกอฮอล์ร่วมกับยา หรือเมาสุราระดับรู้สึกตัวลดลงที่ไม่เข้าแดง | ดื่มแอลกอฮอล์ร่วมกับยา หรือมีสับสนจากสุราไหม? | yes_no | PDF p.52-53, Module 14, code 14เหลือง7-14เหลือง8 | true |
| EMS14_YELLOW_05 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.52-53, Module 14, code 14เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS14_GREEN_01 | เมาสุราโดยไม่มียาอื่นร่วมและยังตอบสนองได้ | เมาสุราแต่ยังตอบสนองได้และไม่มียาอื่นร่วมใช่ไหม? | yes_no | PDF p.52-53, Module 14, code 14เขียว1 |
| EMS14_GREEN_02 | ผลข้างเคียงจากยาแต่ไม่เข้าแดง/เหลือง | มีอาการจากยาแต่ไม่เข้าเกณฑ์แดงหรือเหลืองใช่ไหม? | yes_no | PDF p.52-53, Module 14, code 14เขียว2 |
| EMS14_GREEN_03 | ยา/สารเพื่อความเพลิดเพลิน มีอาการแต่ไม่เข้าแดง/เหลือง | ได้รับยา/สารเพื่อความเพลิดเพลินแต่ไม่เข้าเกณฑ์แดงหรือเหลืองใช่ไหม? | yes_no | PDF p.52-53, Module 14, code 14เขียว3 |
| EMS14_GREEN_04 | สารป้องกันตัว เช่น สเปรย์พริกไทย | ถูกสารป้องกันตัวและไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.52-53, Module 14, code 14เขียว8 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS14_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS14_* | 1 |
| EMS14_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS14_RED_01 | 2 |
| EMS14_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS14_RED_02 | 3 |
| EMS14_Q04 | กินยา/สารเข้าไปแต่ยังไม่เข้าเกณฑ์แดงใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS14_YELLOW_01 | 4 |
| EMS14_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS14_* | 5 |

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
  "group_id": "EMS14",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
