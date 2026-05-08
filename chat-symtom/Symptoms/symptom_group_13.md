---
document_type: ems_symptom_group
group_id: EMS13
group_name_th: "คลุ้มคลั่ง/ภาวะทางจิตประสาท/อารมณ์"
scope: "check-in risk screening only"
not_for: ["diagnosis", "treatment", "general health Q&A"]
source_refs:
  - "PDF p.48-p.49, Module 13, heading คลุ้มคลั่ง/ภาวะทางจิตประสาท/อารมณ์"
needs_human_review: true
---

# EMS13: คลุ้มคลั่ง/ภาวะทางจิตประสาท/อารมณ์

## 1. Retrieval Keywords
- คำหลัก: คลุ้มคลั่ง, เพ้อ, พฤติกรรมเปลี่ยน, อารมณ์, ตื่นตระหนก, ทำร้ายตนเอง
- คำใกล้เคียง: อาวุธ, อันตรายต่อตนเอง, ตำรวจร้องขอ, เพ้อตื่นเต้น, บาดเจ็บจากทำร้ายตนเอง
- คำที่ผู้ใช้ทั่วไปอาจพิมพ์: คลุ้มคลั่ง, เพ้อ, พฤติกรรมเปลี่ยน, อารมณ์, ตื่นตระหนก, ทำร้ายตนเอง, อาวุธ, อันตรายต่อตนเอง
- คำที่ควรแยกออกจากกลุ่มนี้: ยาเกินขนาดเด่นให้ดู EMS14, ถูกทำร้าย/บาดเจ็บเด่นให้ดู EMS21

## 2. What This Group Is For
ใช้คัดกรองสถานการณ์พฤติกรรม คลุ้มคลั่ง ภาวะอารมณ์ หรือเสี่ยงทำร้ายตนเองตาม PDF โดยเน้นความปลอดภัยและ alert

## 3. Risk Rules

### RED
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS13_RED_01 | ไม่รู้สึกตัวหรือไม่หายใจ | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | PDF p.48-49, Module 13, code 13แดง1 | true |
| EMS13_RED_02 | หายใจผิดปกติอย่างน้อย 1 ข้อ | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | PDF p.48-49, Module 13, code 13แดง2 | true |
| EMS13_RED_03 | อาการแสดงช็อกอย่างน้อย 2 ข้อ | มีเหงื่อท่วม ตัวซีดเย็น หรือเกือบหมดสติไหม? | yes_no | PDF p.48-49, Module 13, code 13แดง3 | true |
| EMS13_RED_04 | หลังบาดเจ็บมีระดับความรู้สึกตัวลดลง ตอบไม่ถูกต้อง หรือขัดขืนอย่างไร้เหตุผล | หลังบาดเจ็บมีสับสน ไม่ร่วมมือ หรือขัดขืนมากไหม? | yes_no | PDF p.48-49, Module 13, code 13แดง4 | true |
| EMS13_RED_05 | เลือดออกห้ามไม่หยุด ชักหลังบาดเจ็บ เพ้อคลุ้มคลั่งที่หน่วยงานร้องขอ หรือพยายามทำร้ายตนเองด้วยวิธีรุนแรงตาม PDF | มีอาวุธ บาดแผลรุนแรง หรือเสี่ยงทำร้ายตนเองตอนนี้ไหม? | yes_no | PDF p.48-49, Module 13, code 13แดง5-13แดง8 | true |

### YELLOW
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref | stop_if_true |
|---|---|---|---|---|---|
| EMS13_YELLOW_01 | บาดเจ็บจากการทำร้ายตนเอง | มีบาดเจ็บจากการทำร้ายตนเองไหม? | yes_no | PDF p.48-49, Module 13, code 13เหลือง1 | true |
| EMS13_YELLOW_02 | ตื่นตระหนกและไม่ทราบว่าเคยเป็นมาก่อน | ตื่นตระหนกและไม่ทราบว่าเคยเป็นมาก่อนใช่ไหม? | yes_no | PDF p.48-49, Module 13, code 13เหลือง4 | true |
| EMS13_YELLOW_03 | พฤติกรรมต่างจากที่เคยเป็น | พฤติกรรมต่างจากปกติชัดเจนไหม? | yes_no | PDF p.48-49, Module 13, code 13เหลือง5 | true |
| EMS13_YELLOW_04 | ผู้แจ้งยืนยันรายละเอียดไม่ได้ | ยืนยันรายละเอียดอาการไม่ได้ใช่ไหม? | yes_no | PDF p.48-49, Module 13, code 13เหลือง9 | true |

### GREEN
| rule_id | condition_from_pdf | user_friendly_check | answer_type | source_ref |
|---|---|---|---|---|
| EMS13_GREEN_01 | ตื่นตระหนกในผู้ที่เคยมีอาการเช่นนี้มาก่อน | เคยมีอาการตื่นตระหนกแบบนี้มาก่อนและไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.48-49, Module 13, code 13เขียว4 |
| EMS13_GREEN_02 | ผู้ป่วย/ผู้แจ้งยืนยันขอให้ช่วย | ยังขอให้ช่วยแต่ไม่เข้าเกณฑ์แดง/เหลืองใช่ไหม? | yes_no | PDF p.48-49, Module 13, code 13เขียว6 |
| EMS13_GREEN_03 | ตำรวจร้องขอการเตรียมพร้อมกรณีมีภาวะคุกคาม | มีการร้องขอเตรียมพร้อมจากตำรวจตาม PDF ไหม? | yes_no | PDF p.48-49, Module 13, code 13เขียว7 |
| EMS13_GREEN_04 | ถูกสารป้องกันตัว เช่น แก๊สน้ำตาหรือสเปรย์พริกไทย | ถูกแก๊สน้ำตาหรือสเปรย์พริกไทยและไม่เข้าเกณฑ์แดง/เหลืองไหม? | yes_no | PDF p.48-49, Module 13, code 13เขียว8 |

## 4. Question Bank

คำถามต้องสั้น ไม่ซับซ้อน และเหมาะกับ LINE chat

| question_id | question_th | answer_type | choices | ask_when | skip_when | maps_to_rule_id | priority |
|---|---|---|---|---|---|---|---|
| EMS13_Q01 | ตอนนี้อาการหลักคืออะไร? | free_text | [] | first_question |  | EMS13_* | 1 |
| EMS13_Q02 | ตอนนี้ตอบสนองและหายใจอยู่ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_needed | session_mode = self_checkin && user_can_chat = true | EMS13_RED_01 | 2 |
| EMS13_Q03 | หายใจลำบากมากหรือพูดได้แค่สั้น ๆ ไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS13_RED_02 | 3 |
| EMS13_Q04 | มีบาดเจ็บจากการทำร้ายตนเองไหม? | yes_no | ["ใช่", "ไม่ใช่"] | if_no_red_matched |  | EMS13_YELLOW_01 | 4 |
| EMS13_Q05 | เริ่มเป็นเมื่อไหร่? | options | ["เมื่อกี้", "วันนี้", "หลายวันแล้ว", "ไม่แน่ใจ"] | if_needed |  | EMS13_* | 5 |

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
  "group_id": "EMS13",
  "risk_level": "red | yellow | green | insufficient",
  "matched_rules": [],
  "questions_to_ask_next": [],
  "skip_questions": [],
  "reason_for_backend": "สรุปสั้น ๆ จาก rule id เท่านั้น ไม่วินิจฉัย",
  "source_refs": []
}
```
