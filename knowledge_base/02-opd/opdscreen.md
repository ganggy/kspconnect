# ตาราง `opdscreen` - ข้อมูลคัดกรองผู้ป่วยนอก

## คำอธิบาย

ตารางนี้เก็บข้อมูลการคัดกรอง (Screening) ของผู้ป่วยนอก โดยพยาบาลจะเป็นผู้บันทึกข้อมูลก่อนที่ผู้ป่วยจะเข้าพบแพทย์ ประกอบด้วย vital signs, อาการสำคัญ (Chief Complaint), และประวัติสุขภาพ

## โครงสร้างตาราง

### ฟิลด์หลัก

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `hos_guid` | varchar(38) | **PRI** | GUID |
| `vn` | varchar(13) | **UNI** | เลข Visit Number |
| `hn` | varchar(9) | MUL | เลขประจำตัวผู้ป่วย |
| `vstdate` | date | MUL | วันที่ visit |
| `vsttime` | time | - | เวลา visit |
| `begintime` | time | - | เวลาเริ่มคัดกรอง |
| `outtime` | time | - | เวลาออก |
| `endtime` | time | - | เวลาสิ้นสุด |

### Vital Signs

| คอลัมน์ | ประเภท | คำอธิบาย |
|---------|--------|---------|
| `bpd` | double | ความดันโลหิต diastolic (mmHg) |
| `bps` | double | ความดันโลหิต systolic (mmHg) |
| `bw` | double | น้ำหนัก (kg) |
| `hr` | double | อัตราการเต้นของหัวใจ (bpm) |
| `pulse` | double | ชีพจร |
| `temperature` | double | อุณหภูมิร่างกาย (°C) |
| `rr` | double | อัตราการหายใจ (rpm) |
| `height` | int | ส่วนสูง (cm) |
| `spo2` | double | ออกซิเจนในเลือด (%) |
| `o2sat` | int | O2 saturation |
| `bmi` | double | ดัชนีมวลกาย |
| `waist` | double | รอบเอว (cm) |

### Chief Complaint & History

| คอลัมน์ | ประเภท | คำอธิบาย |
|---------|--------|---------|
| `cc` | text | Chief Complaint (อาการสำคัญ) |
| `cc_begin_date` | date | วันเริ่มอาการ |
| `cc_cause_of_visit` | varchar(250) | สาเหตุที่มา |
| `cc_sign` | varchar(250) | อาการ |
| `cc_duration` | varchar(150) | ระยะเวลาอาการ |
| `cc_position` | varchar(250) | ตำแหน่งอาการ |
| `cc_note` | text | หมายเหตุ |
| `hpi` | text | History of Present Illness |
| `pmh` | text | Past Medical History |
| `fh` | text | Family History |
| `sh` | text | Social History |
| `ros` | text | Review of Systems |

### Physical Examination

| คอลัมน์ | ประเภท | คำอธิบาย |
|---------|--------|---------|
| `pe` | text | Physical Examination โดยรวม |
| `pe_ga` | char(1) | General Appearance |
| `pe_heent` | char(1) | HEENT |
| `pe_heart` | char(1) | Cardiovascular |
| `pe_lung` | char(1) | Respiratory |
| `pe_ab` | char(1) | Abdomen |
| `pe_ext` | char(1) | Extremities |
| `pe_neuro` | char(1) | Neurological |
| `pe_ga_text` | varchar(250) | ข้อความ GA |
| `pe_heent_text` | varchar(250) | ข้อความ HEENT |
| `pe_heart_text` | varchar(250) | ข้อความ Heart |
| `pe_lung_text` | varchar(250) | ข้อความ Lung |
| `pe_ab_text` | varchar(250) | ข้อความ Abdomen |
| `pe_neuro_text` | varchar(250) | ข้อความ Neuro |
| `pe_ext_text` | varchar(250) | ข้อความ Extremities |

### Lab คัดกรอง

| คอลัมน์ | ประเภท | คำอธิบาย |
|---------|--------|---------|
| `fbs` | double | Fasting Blood Sugar |
| `tc` | double | Total Cholesterol |
| `ldl` | double | LDL |
| `hdl` | double | HDL |
| `tg` | double | Triglyceride |
| `hba1c` | double | HbA1c |
| `creatinine` | double | Creatinine |
| `bun` | double | BUN |
| `ua` | double | Uric Acid |
| `ast` | double | AST |
| `alt` | double | ALT |
| `egfr` | double | eGFR |

### อื่นๆ

| คอลัมน์ | ประเภท | คำอธิบาย |
|---------|--------|---------|
| `pain_score` | int | คะแนนความเจ็บปวด (0-10) |
| `screen_dep` | char(3) | แผนกที่คัดกรอง |
| `note` | text | หมายเหตุ |
| `er_note` | text | หมายเหตุ ER |
| `symptom` | varchar(200) | อาการ |
| `update_datetime` | datetime | วันเวลาปรับปรุง |

## ความสัมพันธ์

```sql
opdscreen.vn → ovst.vn
opdscreen.hn → patient.hn
```

## ตัวอย่าง Query

```sql
-- ดูข้อมูลคัดกรองของ visit
SELECT 
    s.vn,
    s.hn,
    s.bps,
    s.bpd,
    s.bw,
    s.height,
    s.temperature,
    s.pulse,
    s.rr,
    s.cc,
    s.pain_score
FROM opdscreen s
WHERE s.vn = '2024010100001';

-- ดู BMI ของผู้ป่วย
SELECT 
    s.vn,
    s.hn,
    s.bw,
    s.height,
    s.bmi,
    s.waist
FROM opdscreen s
WHERE s.vn = '2024010100001';

-- ผู้ป่วยที่มีอุณหภูมิสูง (>37.5)
SELECT 
    s.vn,
    s.hn,
    s.temperature,
    s.cc,
    o.vstdate
FROM opdscreen s
JOIN ovst o ON s.vn = o.vn
WHERE s.temperature > 37.5
  AND o.vstdate = CURDATE();
```

## หมายเหตุ

- ตารางนี้มีฟิลด์มากกว่า 200 คอลัมน์ (แสดงเฉพาะที่สำคัญ)
- ข้อมูลคัดกรองเป็นข้อมูลที่พยาบาลบันทึกก่อนผู้ป่วยเข้าพบแพทย์
- `bmi` คำนวณจาก `bw` และ `height` โดยอัตโนมัติ
- `pain_score` ใช้ระบบ 0-10 (0=ไม่เจ็บ, 10=เจ็บมากที่สุด)
- ฟิลด์ `pe_*` ใช้บันทึกผลตรวจร่างกายแต่ละระบบ
