# ตาราง `iptdiag` - การวินิจฉัยโรคผู้ป่วยใน

## คำอธิบาย

ตารางนี้เก็บการวินิจฉัยโรค (Diagnosis) ของผู้ป่วยในในแต่ละครั้งที่ Admit ใช้รหัส ICD10 เป็นมาตรฐาน เช่นเดียวกับ `ovstdiag` ของผู้ป่วยนอก

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `ipt_diag_id` | int | **PRI** | รหัส running number |
| `an` | varchar(9) | MUL | เลข Admit Number |
| `hn` | varchar(9) | - | เลขประจำตัวผู้ป่วย |
| `icd10` | varchar(9) | - | **รหัสโรค ICD10** |
| `diagtype` | char(2) | - | **ประเภทการวินิจฉัย** |
| `doctor` | varchar(7) | MUL | รหัสแพทย์ |
| `entry_datetime` | datetime | - | วันเวลาบันทึก |
| `modify_datetime` | datetime | - | วันเวลาปรับปรุง |
| `diagnosis_note` | varchar(250) | - | หมายเหตุการวินิจฉัย |
| `diag_no` | int | - | ลำดับการวินิจฉัย |
| `hos_guid` | varchar(38) | MUL | GUID |
| `dx_guid` | varchar(38) | MUL | GUID วินิจฉัย |
| `staff` | varchar(25) | - | ผู้บันทึก |

## ประเภทการวินิจฉัย (`diagtype`)

| รหัส | ความหมาย | คำอธิบาย |
|------|---------|---------|
| 1 | **PDX** (Principal Diagnosis) | โรคหลัก |
| 2 | **SDX** (Secondary Diagnosis) | โรครอง |
| 3 | **COM** (Complication) | ภาวะแทรกซ้อน |
| 4 | **EXT** (External Cause) | สาเหตุภายนอก |
| 5 | **ODX** (Other Diagnosis) | การวินิจฉัยอื่นๆ |

## ความสัมพันธ์

```sql
iptdiag.an → ipt.an              (ข้อมูล Admit)
iptdiag.hn → patient.hn          (ข้อมูลผู้ป่วย)
iptdiag.icd10 → icd101.icd10    (รายละเอียดโรค)
iptdiag.doctor → doctor.code     (ข้อมูลแพทย์)
```

## ตัวอย่าง Query

```sql
-- ดูการวินิจฉัยของผู้ป่วยใน
SELECT 
    d.an,
    d.hn,
    d.icd10,
    i.name AS disease_name,
    d.diagtype,
    CASE d.diagtype 
        WHEN '1' THEN 'PDX (หลัก)' 
        WHEN '2' THEN 'SDX (รอง)' 
        ELSE d.diagtype 
    END AS diag_type_name,
    d.entry_datetime
FROM iptdiag d
LEFT JOIN icd101 i ON d.icd10 = i.icd10
WHERE d.an = '650000001'
ORDER BY d.diagtype;

-- โรคที่พบบ่อยในผู้ป่วยใน (Top 10)
SELECT 
    d.icd10,
    i.name AS disease_name,
    COUNT(DISTINCT d.an) AS admit_count
FROM iptdiag d
LEFT JOIN icd101 i ON d.icd10 = i.icd10
WHERE d.diagtype = '1'
  AND d.entry_datetime BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY d.icd10
ORDER BY admit_count DESC
LIMIT 10;
```

## หมายเหตุ

- โครงสร้างคล้าย `ovstdiag` แต่ใช้ `an` แทน `vn`
- `diagtype = '1'` คือโรคหลักที่ใช้สำหรับส่งเคลมและคำนวณ DRG
- การวินิจฉัยผู้ป่วยในมีความสำคัญมากในการคำนวณค่าใช้จ่ายตามระบบ DRG
