# ตาราง `drugitems` - ข้อมูลยาหลัก

## คำอธิบาย

ตารางนี้เป็นตารางหลักที่เก็บข้อมูลยาทั้งหมดในระบบ HOSxP ทุกรายการยาจะมีรหัส `icode` ที่ไม่ซ้ำกัน ใช้อ้างอิงในทุกกระบวนการเกี่ยวกับยา

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `icode` | varchar(7) | **PRI** | **รหัสยา (Item Code)** |
| `name` | varchar(100) | MUL | **ชื่อยา** |
| `strength` | varchar(50) | MUL | ความแรง/ขนาด |
| `units` | varchar(50) | MUL | หน่วย |
| `unitprice` | double | - | ราคาต่อหน่วย |
| `stdprice` | double | - | ราคามาตรฐาน |
| `dosageform` | varchar(100) | MUL | รูปแบบยา (tablet, capsule, injection) |
| `drugcategory` | varchar(150) | MUL | หมวดหมู่ยา |
| `therapeutic` | varchar(150) | MUL | กลุ่มการรักษา |
| `therapeuticgroup` | varchar(150) | MUL | กลุ่มรักษาย่อย |
| `generic_name` | varchar(250) | MUL | ชื่อสามัญทางยา |
| `trade_name` | varchar(200) | - | ชื่อการค้า |
| `drugaccount` | varchar(2) | MUL | บัญชียา |
| `drugnote` | varchar(150) | MUL | หมายเหตุยา |
| `packqty` | int | MUL | จำนวนต่อแพ็ค |
| `maxlevel` | int | - | สต็อกสูงสุด |
| `minlevel` | int | - | สต็อกต่ำสุด |
| `stdtaken` | varchar(30) | - | วิธีใช้มาตรฐาน |
| `istatus` | char(1) | MUL | สถานะ (Y=ใช้งาน, N=เลิกใช้) |
| `high_cost` | varchar(1) | - | ยาราคาสูง (Y/N) |
| `antibiotic` | char(1) | - | ยาปฏิชีวนะ (Y/N) |
| `habit_forming` | char(1) | - | ยาเสพติด (Y/N) |
| `gpo_code` | varchar(7) | - | รหัส GPO |
| `oldcode` | varchar(25) | MUL | รหัสเก่า |
| `did` | varchar(30) | - | Drug ID |
| `income` | varchar(2) | MUL | รหัสรายได้ |
| `ipd_price` | double | - | ราคาผู้ป่วยใน |
| `price2` | double | - | ราคา 2 |
| `price3` | double | - | ราคา 3 |
| `sks_drug_code` | varchar(25) | - | รหัสยา สกส. |
| `tmt_tp_code` | varchar(10) | - | TMT Trade Product Code |
| `tmt_gp_code` | varchar(10) | - | TMT Generic Product Code |
| `atc_code` | varchar(10) | - | รหัส ATC |
| `begin_date` | date | - | วันเริ่มใช้ |
| `finish_date` | date | - | วันเลิกใช้ |
| `last_update` | datetime | - | วันปรับปรุงล่าสุด |

## ฟิลด์สำคัญที่ใช้บ่อย

| ฟิลด์ | ใช้ทำอะไร |
|-------|----------|
| `icode` | เชื่อมกับ `opitemrece`, `drugstock` |
| `name` | ชื่อยาสำหรับแสดง |
| `strength` | ความแรงของยา |
| `units` | หน่วยนับ |
| `unitprice` | ราคาขาย |
| `dosageform` | รูปแบบยา |
| `istatus` | ตรวจสอบว่ายายังใช้งานอยู่หรือไม่ |
| `high_cost` | กรองยาราคาสูง |
| `antibiotic` | กรองยาปฏิชีวนะ |

## ความสัมพันธ์

```sql
drugitems.icode → opitemrece.icode      (ใบสั่งยา)
drugitems.icode → drugstock.icode       (สต็อก)
drugitems.income → income.income        (รายละเอียดรายได้)
```

## ตัวอย่าง Query

```sql
-- ค้นหายาจากชื่อ
SELECT icode, name, strength, units, unitprice, dosageform
FROM drugitems
WHERE name LIKE '%metformin%'
  AND istatus = 'Y';

-- ยาปฏิชีวนะที่ใช้งานอยู่
SELECT icode, name, strength, units, unitprice
FROM drugitems
WHERE antibiotic = 'Y'
  AND istatus = 'Y'
ORDER BY name;

-- ยาราคาสูง
SELECT icode, name, strength, unitprice
FROM drugitems
WHERE high_cost = 'Y'
  AND istatus = 'Y'
ORDER BY unitprice DESC;
```

## หมายเหตุ

- `icode` เป็นรหัสเฉพาะของแต่ละรายการยา ไม่ซ้ำกัน
- `istatus = 'Y'` คือยาที่ยังใช้งานอยู่ ควรกรองเสมอ
- `unitprice` คือราคาขายต่อหน่วย
- `sks_drug_code` ใช้สำหรับส่งเคลม 43 แฟ้ม
- `tmt_tp_code` และ `tmt_gp_code` เป็นมาตรฐาน TMT (Thai Medicines Terminology)
