---
document_type: ems_symptom_group
group_id: EMS20
group_name_th: "เด็ก (กุมารเวชกรรม)"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.76-p.77, Module 20, heading เด็ก (กุมารเวชกรรม)"
needs_human_review: true
---

# EMS20: เด็ก (กุมารเวชกรรม)

## 1. Retrieval Keywords
- คำหลัก: เด็ก, กุมาร, เด็กไม่ตอบสนอง, เด็กหายใจลำบาก, เด็กชัก, เด็กมีไข้
- คำใกล้เคียง: เงื่องหงอย, เซื่องซึม, ตัวอ่อนปวกเปียก, ไข้ 4-7 วัน, สารกัดกร่อน, ไฮโดรคาร์บอน
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: เด็ก, กุมาร, เด็กไม่ตอบสนอง, เด็กหายใจลำบาก, เด็กชัก, เด็กมีไข้, เงื่องหงอย, เซื่องซึม
- คำที่ควรแยกออกจากกลุ่มนี้: ผู้ใหญ่ให้เลือกกลุ่มอาการหลักอื่น

## 2. What This Group Is For
ใช้คัดกรองผู้ป่วยเด็กตามเกณฑ์ PDF โดยเน้นการตอบสนอง หายใจ สีผิว ชัก ไข้ และสารที่กินเข้าไป

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS20_RED_01 | ไม่รู้สติ/ไม่ตอบสนอง เงื่องหงอย เซื่องซึม ตัวอ่อนปวกเปียก | เด็กไม่ตอบสนองหรือซึมมากไหม? | yes_no | PDF p.76-77, Module 20, code 20แดง1 | true |
| EMS20_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | เด็กหายใจลำบากมากหรือมีเสียงหายใจผิดปกติไหม? | yes_no | PDF p.76-77, Module 20, code 20แดง2 | true |
| EMS20_RED_03 | ปลุกตื่นได้ร่วมกับอาการผิดปกติอย่างน้อย 2 ข้อ | เด็กปลุกตื่นยากและมีสีผิวผิดปกติหรือซีดเย็นไหม? | yes_no | PDF p.76-77, Module 20, code 20แดง3 | true |
| EMS20_RED_04 | ป่วย/ติดเชื้อเริ่มเร็ว <10 ชั่วโมง หรือไข้ 4-7 วันร่วมกับเลือดออกผิดปกติ | เด็กป่วยเร็วมากหรือมีไข้หลายวันร่วมกับเลือดออกผิดปกติไหม? | yes_no | PDF p.76-77, Module 20, code 20แดง4-20แดง5 | true |
| EMS20_RED_05 | ชักหลายครั้ง/นาน >5 นาที สารกัดกร่อนร่วมกลืนลำบาก ไฮโดรคาร์บอน/ยาเกินขนาด <30 นาที หรือภาวะแต่กำเนิดอันตราย | เด็กชักนาน/หลายครั้ง หรือกินสารแล้วกลืนลำบากไหม? | yes_no | PDF p.76-77, Module 20, code 20แดง6-20แดง9 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS20_YELLOW_01 | หายใจขัด | เด็กหายใจขัดไหม? | yes_no | PDF p.76-77, Module 20, code 20เหลือง2 | true |
| EMS20_YELLOW_02 | ภาวะผิดปกติแต่กำเนิดร่วมกับอาการไม่สบาย/ไม่จำเพาะ/ขอประเมิน | เด็กมีภาวะแต่กำเนิดและดูไม่ค่อยสบายไหม? | yes_no | PDF p.76-77, Module 20, code 20เหลือง5 | true |
| EMS20_YELLOW_03 | ชักที่ไม่เข้าแดง: ครั้งแรก เคยชักมาก่อน หรือมีไข้ | เด็กชักแต่ไม่เข้าเกณฑ์แดงใช่ไหม? | yes_no | PDF p.76-77, Module 20, code 20เหลือง6 | true |
| EMS20_YELLOW_04 | กินสารกัดกร่อนหรือไฮโดรคาร์บอน/ยาเกินขนาดที่ไม่เข้าแดง | เด็กกินสารหรือยาแต่ไม่เข้าเกณฑ์แดงใช่ไหม? | yes_no | PDF p.76-77, Module 20, code 20เหลือง7-20เหลือง8 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS20_GREEN_01 | มีไข้ <4 หรือ >7 วันร่วมกับอาการอย่างน้อย 1 ข้อใน PDF | เด็กมีไข้ร่วมกับร้องไม่หยุด อายุน้อยกว่า 3 เดือน ขาดน้ำ หรืออาเจียน/ถ่ายเหลวมากไหม? | yes_no | PDF p.76-77, Module 20, code 20เขียว1 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS20_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS20_* | 1 |
| EMS20_Q02 | เด็กไม่ตอบสนองหรือซึมมากไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS20_RED_01 | 2 |
| EMS20_Q03 | เด็กหายใจลำบากมากหรือมีเสียงหายใจผิดปกติไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS20_RED_02 | 3 |
| EMS20_Q04 | เด็กหายใจขัดไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS20_YELLOW_01 | 4 |
| EMS20_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS20_* | 5 |

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
  "group_id": "EMS20",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
