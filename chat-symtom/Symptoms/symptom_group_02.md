---
document_type: ems_symptom_group
group_id: EMS02
group_name_th: "แอนาฟิแล็กซิส(ช็อกภูมิแพ้)/ปฏิกิริยาภูมิแพ้"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.7, Module 2, heading แอนาฟิแล็กซิส/ปฏิกิริยาภูมิแพ้"
needs_human_review: true
---

# EMS02: แอนาฟิแล็กซิส(ช็อกภูมิแพ้)/ปฏิกิริยาภูมิแพ้

## 1. Retrieval Keywords
- คำหลัก: ช็อกภูมิแพ้, ภูมิแพ้รุนแรง, แพ้ยา, ปฏิกิริยาภูมิแพ้, คอหอยบวม, ลิ้นบวม
- คำใกล้เคียง: กลืนลำบาก, พูดขัด, หายใจขัด, หลังได้รับสิ่งที่แพ้ 30 นาที, ปฏิกิริยาต่อยา
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ช็อกภูมิแพ้, ภูมิแพ้รุนแรง, แพ้ยา, ปฏิกิริยาภูมิแพ้, คอหอยบวม, ลิ้นบวม, กลืนลำบาก, พูดขัด
- คำที่ควรแยกออกจากกลุ่มนี้: แมลงหรือสัตว์กัดเด่นให้ดู EMS03, หายใจลำบากเด่นโดยไม่เกี่ยวกับแพ้ให้ดู EMS05

## 2. What This Group Is For
ใช้คัดกรองข้อความที่สงสัยปฏิกิริยาภูมิแพ้หรือช็อกภูมิแพ้ตามเกณฑ์ PDF โดยไม่สรุปโรค

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS02_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.7, Module 2, code 2แดง1 | true |
| EMS02_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.7, Module 2, code 2แดง2 | true |
| EMS02_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.7, Module 2, code 2แดง3 | true |
| EMS02_RED_04 | ระดับความรู้สึกตัวลดลง/ตอบไม่ถูกต้อง | ตอบคำถามง่าย ๆ ได้ปกติไหม? | yes_no | PDF p.7, Module 2, code 2แดง4 | true |
| EMS02_RED_05 | คอหอย/ลิ้นบวม/กลืนลำบากร่วมกับพูดหรือหายใจขัด | คอหอยหรือลิ้นบวม และพูดหรือหายใจขัดไหม? | yes_no | PDF p.7, Module 2, code 2แดง6 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS02_YELLOW_01 | เคยมีประวัติช็อกภูมิแพ้ภายใน 30 นาทีหลังได้รับสิ่งที่แพ้ | เคยมีปฏิกิริยาภูมิแพ้รุนแรงหลังได้รับสิ่งที่แพ้ภายใน 30 นาทีไหม? | yes_no | PDF p.7, Module 2, code 2เหลือง1 | true |
| EMS02_YELLOW_02 | หายใจขัดหรือปฏิกิริยาต่อยา | หายใจขัดหรือมีปฏิกิริยาต่อยาไหม? | yes_no | PDF p.7, Module 2, code 2เหลือง2 | true |
| EMS02_YELLOW_03 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.7, Module 2, code 2เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS02_GREEN_01 | พบรหัสเขียวแต่ข้อความรายละเอียดไม่ชัดจาก extraction | มีอาการแพ้เล็กน้อยแต่ไม่เข้าเกณฑ์แดงหรือเหลืองไหม? | yes_no | PDF p.7, Module 2, code 2เขียว1 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS02_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS02_* | 1 |
| EMS02_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS02_RED_01 | 2 |
| EMS02_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS02_RED_02 | 3 |
| EMS02_Q04 | เคยมีปฏิกิริยาภูมิแพ้รุนแรงหลังได้รับสิ่งที่แพ้ภายใน 30 นาทีไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS02_YELLOW_01 | 4 |
| EMS02_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS02_* | 5 |

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
  "group_id": "EMS02",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
