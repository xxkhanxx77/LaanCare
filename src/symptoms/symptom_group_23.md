---
document_type: ems_symptom_group
group_id: EMS23
group_name_th: "จมน้ำ/หน้าคว่ำจมน้ำ/บาดเจ็บเหตุดำน้ำ/บาดเจ็บทางน้ำ"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.88-p.89, Module 23, heading จมน้ำ/หน้าคว่ำจมน้ำ/บาดเจ็บเหตุดำน้ำ/บาดเจ็บทางน้ำ"
needs_human_review: true
---

# EMS23: จมน้ำ/หน้าคว่ำจมน้ำ/บาดเจ็บเหตุดำน้ำ/บาดเจ็บทางน้ำ

## 1. Retrieval Keywords
- คำหลัก: จมน้ำ, หน้าคว่ำจมน้ำ, ดำน้ำ, บาดเจ็บทางน้ำ, สำลักน้ำ, จมใต้น้ำ
- คำใกล้เคียง: เครื่องประดาน้ำ, จม >1 นาที, สำลักน้ำ, บาดเจ็บศีรษะ/คอ/หลัง/ลำตัว, อยู่บนบกหรือในเรือ
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: จมน้ำ, หน้าคว่ำจมน้ำ, ดำน้ำ, บาดเจ็บทางน้ำ, สำลักน้ำ, จมใต้น้ำ, เครื่องประดาน้ำ, จม >1 นาที
- คำที่ควรแยกออกจากกลุ่มนี้: สำลักอาหาร/สิ่งอุดทางหายใจให้ดู EMS08

## 2. What This Group Is For
ใช้คัดกรองเหตุจมน้ำ ดำน้ำ หรือบาดเจ็บทางน้ำตาม PDF

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS23_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.88-89, Module 23, code 23แดง1 | true |
| EMS23_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.88-89, Module 23, code 23แดง2 | true |
| EMS23_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.88-89, Module 23, code 23แดง3 | true |
| EMS23_RED_04 | หลังบาดเจ็บมีสติลดลง ชัก ตอบไม่ถูกต้อง ขัดขืน หรือเลือดออกห้ามไม่หยุด | หลังเหตุมีสับสน ชัก หรือเลือดห้ามไม่หยุดไหม? | yes_no | PDF p.88-89, Module 23, code 23แดง4-23แดง5 | true |
| EMS23_RED_05 | อุบัติเหตุดำน้ำด้วยเครื่องประดาน้ำ หรืออุบัติภัยหมู่ | เกิดเหตุดำน้ำด้วยเครื่องประดาน้ำหรืออุบัติภัยหมู่ไหม? | yes_no | PDF p.88-89, Module 23, code 23แดง7-23แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS23_YELLOW_01 | จมน้ำ/หน้าคว่ำจมน้ำ ผู้ป่วยรู้สึกตัว | จมน้ำแต่ตอนนี้รู้สึกตัวใช่ไหม? | yes_no | PDF p.88-89, Module 23, code 23เหลือง1 | true |
| EMS23_YELLOW_02 | หายใจขัดหรือสำลักน้ำ/ไอ | มีหายใจขัด สำลักน้ำ หรือไอไหม? | yes_no | PDF p.88-89, Module 23, code 23เหลือง2-23เหลือง3 | true |
| EMS23_YELLOW_03 | กระดูกหัก/บาดเจ็บศีรษะคอหลังลำตัว หรือยืนยันว่าจมน้ำ >1 นาทีไม่เข้าแดง | จมน้ำนานเกิน 1 นาทีหรือมีบาดเจ็บศีรษะ คอ หลัง หรือลำตัวไหม? | yes_no | PDF p.88-89, Module 23, code 23เหลือง4-23เหลือง6 | true |
| EMS23_YELLOW_04 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.88-89, Module 23, code 23เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS23_GREEN_01 | บาดเจ็บทางน้ำเล็กน้อย ไม่จมน้ำ: แผลห้ามเลือดได้ | บาดเจ็บทางน้ำเล็กน้อยและไม่ได้จมน้ำใช่ไหม? | yes_no | PDF p.88-89, Module 23, code 23เขียว1 |
| EMS23_GREEN_02 | บาดเจ็บทางน้ำเล็กน้อย ไม่จมน้ำ: กระดูกแขน/ขาหักหรือเคลื่อนตำแหน่งเดียว | สงสัยกระดูกแขนหรือขาหัก/เคลื่อนแห่งเดียวจากน้ำไหม? | yes_no | PDF p.88-89, Module 23, code 23เขียว4 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS23_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS23_* | 1 |
| EMS23_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS23_RED_01 | 2 |
| EMS23_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS23_RED_02 | 3 |
| EMS23_Q04 | จมน้ำแต่ตอนนี้รู้สึกตัวใช่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS23_YELLOW_01 | 4 |
| EMS23_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS23_* | 5 |

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
  "group_id": "EMS23",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
