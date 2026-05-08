---
document_type: ems_symptom_group
group_id: EMS08
group_name_th: "สำลักอุดทางหายใจ"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.31, Module 8, heading สำลักอุดทางหายใจ"
needs_human_review: true
---

# EMS08: สำลักอุดทางหายใจ

## 1. Retrieval Keywords
- คำหลัก: สำลัก, อุดทางหายใจ, ติดคอ, พูดไม่ออก, ร้องไม่ออก, เขียวคล้ำ
- คำใกล้เคียง: ทรวงอกขยับ, กินอยู่, มีสิ่งในปาก, ช่วยให้ทางหายใจโล่งแล้ว
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: สำลัก, อุดทางหายใจ, ติดคอ, พูดไม่ออก, ร้องไม่ออก, เขียวคล้ำ, ทรวงอกขยับ, กินอยู่
- คำที่ควรแยกออกจากกลุ่มนี้: หายใจยากที่ไม่ได้เกิดจากสำลักให้ดู EMS05

## 2. What This Group Is For
ใช้คัดกรองกรณีสำลักหรือสงสัยมีสิ่งอุดทางหายใจตาม PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS08_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.31, Module 8, code 8แดง1 | true |
| EMS08_RED_02 | พูดหรือร้องไม่ออก/ออกเสียงไม่ได้ | ตอนนี้พูดหรือร้องออกเสียงไม่ได้ใช่ไหม? | yes_no | PDF p.31, Module 8, code 8แดง2 | true |
| EMS08_RED_03 | มีอาการเขียวคล้ำ | มีริมฝีปากหรือตัวเขียวคล้ำไหม? | yes_no | PDF p.31, Module 8, code 8แดง3 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS08_YELLOW_01 | หายใจได้โดยไม่ยากลำบาก | ยังหายใจได้และไม่ยากลำบากใช่ไหม? | yes_no | PDF p.31, Module 8, code 8เหลือง1 | true |
| EMS08_YELLOW_02 | ยังพูดหรือร้องออกเสียงได้ | ยังพูดหรือร้องออกเสียงได้ใช่ไหม? | yes_no | PDF p.31, Module 8, code 8เหลือง2 | true |
| EMS08_YELLOW_03 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.31, Module 8, code 8เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS08_GREEN_01 | ช่วยทำให้ทางหายใจโล่งแล้ว แต่ยังยืนยันขอให้ช่วย | ทางหายใจโล่งแล้วแต่ยังต้องการให้ช่วยใช่ไหม? | yes_no | PDF p.31, Module 8, code 8เขียว1 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS08_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS08_* | 1 |
| EMS08_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS08_RED_01 | 2 |
| EMS08_Q03 | ตอนนี้พูดหรือร้องออกเสียงไม่ได้ใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS08_RED_02 | 3 |
| EMS08_Q04 | ยังหายใจได้และไม่ยากลำบากใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS08_YELLOW_01 | 4 |
| EMS08_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS08_* | 5 |

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
  "group_id": "EMS08",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
