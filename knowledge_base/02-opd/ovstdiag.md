# ตาราง `ovstdiag` - การวินิจฉัยโรคผู้ป่วยนอก

## คำอธิบาย

ตารางนี้เก็บการวินิจฉัยโรค (Diagnosis) ของผู้ป่วยนอกในแต่ละครั้งที่มารับบริการ ใช้รหัส ICD10 เป็นมาตรฐาน หนึ่ง visit อาจมีหลายการวินิจฉัย (หลายรหัส ICD10)

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `ovst_diag_id` | int | **PRI** | รหัส running number |
| `vn` | varchar(13) | MUL | เลข Visit Number |
| `icd10` | varchar(9) | MUL | **รหัสโรค ICD10** |
| `hn` | varchar(9) | MUL | เลขประจำตัวผู้ป่วย |
| `vstdate` | date | MUL | วันที่ visit |
| `vsttime` | time | - | เวลา |
| `diagtype` | char(2) | - | **ประเภทการวินิจฉัย** (1=PDX, 2=SDX) |
| `icd103` | char(3) | - | รหัส ICD10 3 หลัก |
| `hcode` | varchar(5) | - | รหัสหน่วยบริการ |
| `doctor` | varchar(6) | MUL | รหัสแพทย์ |
| `episode` | tinyint | - | ครั้งที่ |
| `ext_code` | char(2) | - | รหัสเพิ่มเติม |
| `hos_guid` | varchar(38) | MUL | GUID |
| `dep_flag` | char(2) | - | สถานะแผนก |
| `ovst_oper_type` | int | - | ประเภทการดำเนินการ |
| `staff` | varchar(25) | - | ผู้บันทึก |
| `dx_guid` | varchar(38) | - | GUID วินิจฉัย |
| `lock_dx` | char(1) | - | ล็อกการวินิจฉัย |
| `dx_code_note` | varchar(100) | - | หมายเหตุ |
| `ovstdiag_severe_type_id` | int | MUL | ระดับความรุนแรง |
| `diag_no` | int | - | ลำดับการวินิจฉัย |
| `update_datetime` | datetime | - | วันเวลาปรับปรุง |
| `confirm` | char(1) | - | ยืนยัน |
| `confirm_staff` | varchar(25) | - | ผู้ยืนยัน |
| `opi_guid` | varchar(38) | - | GUID |
| `sct_id` | varchar(18) | - | SNOMED CT ID |

## ประเภทการวินิจฉัย (`diagtype`)

| รหัส | ความหมาย | คำอธิบาย |
|------|---------|---------|
| 1 | **PDX** (Principal Diagnosis) | โรคหลัก - วินิจฉัยหลักของการรักษาครั้งนี้ |
| 2 | **SDX** (Secondary Diagnosis) | โรครอง - โรคที่พบร่วม |
| 3 | **COM** (Complication) | ภาวะแทรกซ้อน |
| 4 | **EXT** (External Cause) | สาเหตุภายนอก |
| 5 | **ODX** (Other Diagnosis) | การวินิจฉัยอื่นๆ |

## ความสัมพันธ์

```sql
ovstdiag.vn → ovst.vn              (ข้อมูล visit)
ovstdiag.hn → patient.hn           (ข้อมูลผู้ป่วย)
ovstdiag.icd10 → icd101.icd10     (รายละเอียดโรค)
ovstdiag.doctor → doctor.code      (ข้อมูลแพทย์)
```

## ตัวอย่าง Query

```sql
-- ดูการวินิจฉัยของ visit
SELECT 
    d.vn,
    d.hn,
    d.icd10,
    i.name AS disease_name,
    d.diagtype,
    CASE d.diagtype 
        WHEN '1' THEN 'PDX (หลัก)' 
        WHEN '2' THEN 'SDX (รอง)' 
        ELSE d.diagtype 
    END AS diag_type_name,
    d.vstdate,
    d.doctor
FROM ovstdiag d
LEFT JOIN icd101 i ON d.icd10 = i.icd10
WHERE d.vn = '2024010100001'
ORDER BY d.diagtype;

-- นับจำนวนผู้ป่วยตามโรค (Top 10)
SELECT 
    d.icd10,
    i.name AS disease_name,
    COUNT(DISTINCT d.vn) AS visit_count
FROM ovstdiag d
LEFT JOIN icd101 i ON d.icd10 = i.icd10
WHERE d.vstdate BETWEEN '2024-01-01' AND '2024-01-31'
  AND d.diagtype = '1'  -- เฉพาะโรคหลัก
GROUP BY d.icd10
ORDER BY visit_count DESC
LIMIT 10;

-- ผู้ป่วยที่มาด้วยโรคเบาหวาน (E11-E14)
SELECT DISTINCT
    o.vn,
    o.hn,
    o.vstdate,
    d.icd10,
    i.name AS disease_name
FROM ovst o
JOIN ovstdiag d ON o.vn = d.vn
LEFT JOIN icd101 i ON d.icd10 = i.icd10
WHERE d.icd10 LIKE 'E11%'
  AND o.vstdate BETWEEN '2024-01-01' AND '2024-01-31';
```

## หมายเหตุ

- หนึ่ง VN อาจมีหลายรายการวินิจฉัย (หลายแถวใน `ovstdiag`)
- `diagtype = '1'` คือโรคหลัก (PDX) ที่ใช้สำหรับการส่งเคลม
- `diagtype = '2'` คือโรครอง (SDX) ที่พบร่วม
- รหัส ICD10 ใน HOSxP อาจมีรูปแบบ `E11.9`, `I10`, `J06.9` เป็นต้น
- สำหรับการส่ง e-Claim 43 แฟ้ม ใช้เฉพาะ `diagtype = '1'`
