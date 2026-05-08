---
document_type: ems_source_map
source_title: "ปกเกณฑ์วิธีการคัดแยกฯ ผู้ป่วยฉุกเฉิน2"
source_file: "255810141123522877_js96Mk3f0tfQ2VsJ (1).pdf"
source_version: "#0.77"
extracted_at: "2026-05-07"
scope: "source traceability for check-in risk screening only"
needs_human_review: true
---

# Source Map

| group_id | group_name_th | pdf_pages_used | source_heading_or_code | extraction_note |
|---|---|---|---|---|
| EMS01 | ปวดท้อง/หลัง/เชิงกรานและขาหนีบ | PDF p.3 | Module 1 | risk rules summarized from triage criteria only |
| EMS02 | แอนาฟิแล็กซิส(ช็อกภูมิแพ้)/ปฏิกิริยาภูมิแพ้ | PDF p.7 | Module 2 | risk rules summarized from triage criteria only |
| EMS03 | สัตว์กัด | PDF p.11 | Module 3 | risk rules summarized from triage criteria only |
| EMS04 | เลือดออก (ไม่มีสาเหตุจากการบาดเจ็บ) | PDF p.15-16 | Module 4 | risk rules summarized from triage criteria only |
| EMS05 | หายใจยากลำบาก | PDF p.19-20 | Module 5 | risk rules summarized from triage criteria only |
| EMS06 | หัวใจหยุดเต้น | PDF p.23 | Module 6 | risk rules summarized from triage criteria only |
| EMS07 | เจ็บแน่นทรวงอก/หัวใจ | PDF p.27-28 | Module 7 | risk rules summarized from triage criteria only |
| EMS08 | สำลักอุดทางหายใจ | PDF p.31 | Module 8 | risk rules summarized from triage criteria only |
| EMS09 | เบาหวาน | PDF p.35 | Module 9 | risk rules summarized from triage criteria only |
| EMS10 | ภยันตรายจากสภาพแวดล้อม | PDF p.39-40 | Module 10 | risk rules summarized from triage criteria only |
| EMS11 | เว้นว่างใน PDF | PDF p.41 | Module 11 | เว้นว่างตาม PDF; no runtime triage rules |
| EMS12 | ปวดศีรษะ/ภาวะผิดปกติของตา/หู/คอ/จมูก | PDF p.44-45 | Module 12 | risk rules summarized from triage criteria only |
| EMS13 | คลุ้มคลั่ง/ภาวะทางจิตประสาท/อารมณ์ | PDF p.48-49 | Module 13 | risk rules summarized from triage criteria only |
| EMS14 | ยาเกินขนาด/ได้รับพิษ | PDF p.52-53 | Module 14 | risk rules summarized from triage criteria only |
| EMS15 | มีครรภ์/คลอด/นรีเวช | PDF p.56-57 | Module 15 | risk rules summarized from triage criteria only |
| EMS16 | ชัก | PDF p.60-61 | Module 16 | risk rules summarized from triage criteria only |
| EMS17 | ป่วย/อ่อนเพลีย (ไม่จำเพาะ/ไม่ทราบสาเหตุ)/อื่นๆ | PDF p.64-65 | Module 17 | risk rules summarized from triage criteria only |
| EMS18 | แขนขาอ่อนแรง/พูดลำบาก/ปากเบี้ยว (หลอดเลือดสมองอุดตัน/แตก) | PDF p.68-69 | Module 18 | risk rules summarized from triage criteria only |
| EMS19 | หมดสติ/ไม่ตอบสนอง/หมดสติชั่ววูบ | PDF p.72-73 | Module 19 | risk rules summarized from triage criteria only |
| EMS20 | เด็ก (กุมารเวชกรรม) | PDF p.76-77 | Module 20 | risk rules summarized from triage criteria only |
| EMS21 | ถูกทำร้าย/บาดเจ็บ | PDF p.80-81 | Module 21 | risk rules summarized from triage criteria only |
| EMS22 | ไหม้/ลวก - ความร้อน/กระแสไฟฟ้า/สารเคมี | PDF p.84-85 | Module 22 | risk rules summarized from triage criteria only |
| EMS23 | จมน้ำ/หน้าคว่ำจมน้ำ/บาดเจ็บเหตุดำน้ำ/บาดเจ็บทางน้ำ | PDF p.88-89 | Module 23 | risk rules summarized from triage criteria only |
| EMS24 | พลัดตกหกล้ม/อุบัติเหตุ/เจ็บปวด | PDF p.92-93 | Module 24 | risk rules summarized from triage criteria only |
| EMS25 | อุบัติเหตุยานยนต์ | PDF p.96 | Module 25 | risk rules summarized from triage criteria only |

## Source Handling Notes

- ใช้เฉพาะหัวข้อ `เกณฑ์คัดแยก` และรหัสแดง/เหลือง/เขียวจาก PDF
- ตัดส่วน `คำสั่งแนะนำก่อนหน่วยปฏิบัติการไปถึง` ออกจาก runtime screening เพราะอยู่นอกขอบเขต check-in/alert
- รหัสขาวถูกละไว้จากไฟล์กลุ่มอาการ เพราะงานนี้กำหนดเฉพาะ red/yellow/green
- เลขหน้าอ้างอิงใช้เลขหน้า PDF จากไฟล์ต้นฉบับร่วมกับหมายเลข Module และ code เพื่อให้ตรวจย้อนกลับได้
