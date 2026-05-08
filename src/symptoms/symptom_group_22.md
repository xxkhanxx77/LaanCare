---
document_type: ems_symptom_group
group_id: EMS22
group_name_th: "ไหม้/ลวก - ความร้อน/กระแสไฟฟ้า/สารเคมี"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.84-p.85, Module 22, heading ไหม้/ลวก - ความร้อน/กระแสไฟฟ้า/สารเคมี"
needs_human_review: true
---

# EMS22: ไหม้/ลวก - ความร้อน/กระแสไฟฟ้า/สารเคมี

## 1. Retrieval Keywords
- คำหลัก: ไหม้, ลวก, ไฟไหม้, น้ำร้อนลวก, ไฟฟ้าช็อต, สารเคมีไหม้, แผลไหม้
- คำใกล้เคียง: หายใจผิดปกติ, ไหม้ทางหายใจ, เสียงแหบ, กลืนลำบาก, ไฟฟ้าช็อต, มือ เท้า อวัยวะเพศ
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: ไหม้, ลวก, ไฟไหม้, น้ำร้อนลวก, ไฟฟ้าช็อต, สารเคมีไหม้, แผลไหม้, หายใจผิดปกติ
- คำที่ควรแยกออกจากกลุ่มนี้: สารเคมีสัมผัสแต่ไม่มีแผลไหม้ชัดเจนให้ดู EMS10, กินสารพิษให้ดู EMS14

## 2. What This Group Is For
ใช้คัดกรองแผลไหม้/ลวกจากความร้อน ไฟฟ้า หรือสารเคมีตาม PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS22_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.84-85, Module 22, code 22แดง1 | true |
| EMS22_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.84-85, Module 22, code 22แดง2 | true |
| EMS22_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.84-85, Module 22, code 22แดง3 | true |
| EMS22_RED_04 | หลังบาดเจ็บมีสติลดลง ชัก ตอบไม่ถูกต้อง ขัดขืน หรือเลือดออกห้ามไม่หยุด | หลังเหตุมีสับสน ชัก หรือเลือดห้ามไม่หยุดไหม? | yes_no | PDF p.84-85, Module 22, code 22แดง4-22แดง5 | true |
| EMS22_RED_05 | ไหม้ทางหายใจ ไหม้ผิวกาย >20% ผู้ใหญ่/>10% เด็ก ไฟฟ้าช็อตจากสายไฟ/กล่องไฟ หรืออุบัติภัยหมู่ | มีไหม้ที่หน้า/คอ หายใจลำบาก กลืนลำบาก หรือไฟฟ้าช็อตรุนแรงไหม? | yes_no | PDF p.84-85, Module 22, code 22แดง6-22แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS22_YELLOW_01 | ของเหลวร้อนหกราด หายใจขัด หรือไฟฟ้าช็อตเครื่องใช้ในบ้านไม่เข้าแดง | น้ำร้อนลวก หายใจขัด หรือไฟฟ้าช็อตในบ้านไหม? | yes_no | PDF p.84-85, Module 22, code 22เหลือง1-22เหลือง3 | true |
| EMS22_YELLOW_02 | สารเคมีไหม้ตา | สารเคมีเข้าตาหรือไหม้ตาไหม? | yes_no | PDF p.84-85, Module 22, code 22เหลือง5 | true |
| EMS22_YELLOW_03 | ไหม้ผิวกายผู้ใหญ่ 10-20% หรือเด็ก 5-10% | แผลไหม้กว้างตามเกณฑ์ PDF ไหม? | yes_no | PDF p.84-85, Module 22, code 22เหลือง6 | true |
| EMS22_YELLOW_04 | แบตเตอรี่ระเบิด หรือไหม้ที่มือ เท้า อวัยวะเพศ | ไหม้ที่มือ เท้า หรืออวัยวะเพศไหม? | yes_no | PDF p.84-85, Module 22, code 22เหลือง7-22เหลือง8 | true |
| EMS22_YELLOW_05 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.84-85, Module 22, code 22เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS22_GREEN_01 | ไฟฟ้าช็อตเครื่องใช้ในบ้าน ไม่มีอาการ | ไฟฟ้าช็อตจากเครื่องใช้ในบ้านแต่ไม่มีอาการไหม? | yes_no | PDF p.84-85, Module 22, code 22เขียว3 |
| EMS22_GREEN_02 | ไหม้/ลวกผิวกายผู้ใหญ่ <10% หรือเด็ก <5% | แผลไหม้เล็กกว่าเกณฑ์เหลืองและไม่เข้าแดงไหม? | yes_no | PDF p.84-85, Module 22, code 22เขียว6 |
| EMS22_GREEN_03 | ถูกสารป้องกันตัว เช่น แก๊สน้ำตาหรือสเปรย์พริกไทย | ถูกแก๊สน้ำตาหรือสเปรย์พริกไทยและไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.84-85, Module 22, code 22เขียว8 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS22_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS22_* | 1 |
| EMS22_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS22_RED_01 | 2 |
| EMS22_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS22_RED_02 | 3 |
| EMS22_Q04 | น้ำร้อนลวก หายใจขัด หรือไฟฟ้าช็อตในบ้านไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS22_YELLOW_01 | 4 |
| EMS22_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS22_* | 5 |

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
  "group_id": "EMS22",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
