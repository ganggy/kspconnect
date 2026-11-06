# ตาราง `patient_pttype` - สิทธิการรักษาของผู้ป่วย

## คำอธิบาย

ตารางนี้เก็บประวัติสิทธิการรักษาของผู้ป่วยแต่ละคน หนึ่งคนอาจมีหลายสิทธิ (เช่น สิทธิหลักประกันสุขภาพ + สิทธิประกันสังคม) โดยแต่ละสิทธิจะมีวันเริ่มต้นและวันหมดอายุ

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `patient_pttype_id` | int | **PRI** | รหัส running number |
| `hn` | varchar(9) | MUL | เลขประจำตัวผู้ป่วย |
| `pttype` | char(2) | - | **รหัสสิทธิการรักษา** |
| `begin_date` | date | - | วันเริ่มต้นสิทธิ |
| `expire_date` | date | - | วันหมดอายุสิทธิ |
| `hospmain` | varchar(9) | - | รหัสหน่วยบริการหลัก (สปสช.) |
| `hospsub` | varchar(9) | - | รหัสหน่วยบริส่งเสริม |
| `pttypeno` | varchar(50) | - | เลขที่สิทธิ (เลขบัตร สปสช., เลขสมาชิก ประกันสังคม) |
| `pttype_number` | int | - | ลำดับสิทธิ |
| `company_id` | int | - | รหัสบริษัท |
| `contract_id` | int | - | รหัสสัญญา |
| `max_debt_amount` | double | - | วงเงินเบิกสูงสุด |
| `paid_amount` | double | - | ยอดที่ใช้ไปแล้ว |
| `authorize_staff` | varchar(25) | - | ผู้รับรอง |
| `authorize_datetime` | datetime | - | วันเวลารับรอง |
| `pttype_note` | text | - | หมายเหตุสิทธิ |
| `staff` | varchar(50) | - | ผู้บันทึก |
| `update_datetime` | datetime | - | วันเวลาปรับปรุง |

## ความสัมพันธ์

```sql
patient_pttype.hn → patient.hn
patient_pttype.pttype → pttype.pttype   (รายละเอียดชื่อสิทธิ)
```

## หลักการทำงาน

1. **สิทธิปัจจุบัน** - ฟิลด์ `patient.pttype` เก็บสิทธิที่ใช้งานปัจจุบัน
2. **ประวัติสิทธิ** - `patient_pttype` เก็บทุกสิทธิที่เคยมี รวมถึงสิทธิที่หมดอายุแล้ว
3. **ตรวจสอบอายุสิทธิ** - ใช้ `begin_date` และ `expire_date` ตรวจสอบว่าสิทธิยังใช้ได้หรือไม่

## ตัวอย่าง Query

```sql
-- ดูสิทธิทั้งหมดของผู้ป่วย
SELECT 
    pp.hn,
    pp.pttype,
    pt.name AS pttype_name,
    pp.begin_date,
    pp.expire_date,
    pp.pttypeno,
    pp.hospmain
FROM patient_pttype pp
LEFT JOIN pttype pt ON pp.pttype = pt.pttype
WHERE pp.hn = '000000001'
ORDER BY pp.begin_date DESC;

-- ดูสิทธิที่ยังไม่หมดอายุ
SELECT 
    pp.hn,
    pp.pttype,
    pp.begin_date,
    pp.expire_date
FROM patient_pttype pp
WHERE pp.hn = '000000001'
  AND pp.begin_date <= CURDATE()
  AND (pp.expire_date IS NULL OR pp.expire_date >= CURDATE());
```

## หมายเหตุ

- สิทธิบัตรทอง (หลักประกันสุขภาพแห่งชาติ) มักใช้รหัส `01` หรือ `02`
- ประกันสังคม มักใช้รหัส `03`
- ข้าราชการ/รัฐวิสาหกิจ มักใช้รหัส `04` หรือ `05`
- `hospmain` สำคัญมากสำหรับการส่ง e-Claim (ต้องตรงกับ สปสช.)
