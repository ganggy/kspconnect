# ตาราง `opitemrece` - ใบสั่งยาและค่ารักษา

## คำอธิบาย

ตารางนี้เป็นตารางกลางที่เก็บรายการค่ารักษาทั้งหมด ไม่ใช่แค่ยา แต่รวมถึง:
- ยา (drug)
- ค่าตรวจ Lab
- ค่า X-Ray
- ค่าห้อง/เตียง
- ค่าอาหาร
- ค่าบริการอื่นๆ

ตารางนี้เชื่อมโยง OPD, IPD, Drug, และ Finance เข้าด้วยกัน

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `hos_guid` | varchar(38) | **PRI** | GUID |
| `vn` | varchar(13) | MUL | เลข VN (OPD) |
| `hn` | varchar(9) | MUL | เลข HN |
| `an` | varchar(9) | MUL | เลข AN (IPD) |
| `icode` | varchar(7) | MUL | **รหัสยา/รายการ** |
| `qty` | int | - | **จำนวน** |
| `drugusage` | varchar(7) | MUL | รหัสวิธีใช้ยา |
| `idr` | varchar(30) | - | รหัสใบสั่งยา |
| `iperday` | int | - | จำนวนครั้งต่อวัน |
| `iperdose` | double | - | จำนวนต่อครั้ง |
| `recetime` | time | - | เวลาบันทึก |
| `unitprice` | double | - | ราคาต่อหน่วย |
| `vstdate` | date | MUL | วันที่ visit |
| `vsttime` | time | - | เวลา visit |
| `rxdate` | date | MUL | วันที่สั่ง |
| `rxtime` | time | - | เวลาสั่ง |
| `doctor` | varchar(10) | MUL | รหัสแพทย์ |
| `dep_code` | char(3) | - | รหัสแผนก |
| `finance_number` | varchar(7) | MUL | เลขการเงิน |
| `discount` | double | - | ส่วนลด |
| `sum_price` | double | - | **ราคารวม** |
| `cost` | double | - | ต้นทุน |
| `pttype` | char(2) | MUL | สิทธิ |
| `income` | char(2) | - | **รหัสรายได้** |
| `sub_type` | char(1) | MUL | ประเภทย่อย |
| `item_type` | char(1) | MUL | **ประเภทรายการ** |
| `remain` | char(1) | - | คงเหลือ |
| `paidst` | char(2) | - | สถานะจ่าย |
| `item_no` | tinyint | - | ลำดับรายการ |
| `staff` | varchar(25) | MUL | ผู้บันทึก |
| `last_modified` | datetime | - | วันเวลาปรับปรุง |
| `stock_department_id` | int | - | รหัสแผนกสต็อก |
| `command_doctor` | varchar(10) | - | แพทย์เจ้าของไข้ |

## ประเภทรายการ (`item_type`)

| รหัส | ความหมาย |
|------|---------|
| 1 | ยา (Drug) |
| 2 | ค่าบริการ (Service) |
| 3 | ค่า Lab |
| 4 | ค่า X-Ray |
| 5 | ค่าห้อง |
| 6 | ค่าอาหาร |
| 7 | ค่าเวชภัณฑ์ |
| 8 | ค่าอื่นๆ |

## รหัสรายได้ (`income`)

| รหัส | ความหมาย |
|------|---------|
| 01 | ค่ายา |
| 02 | ค่าบริการทั่วไป |
| 03 | ค่า Lab |
| 04 | ค่า X-Ray |
| 05 | ค่าห้อง |
| 06 | ค่าอาหาร |
| 07 | ค่าเวชภัณฑ์ |
| 08 | ค่าอื่นๆ |
| 09 | ค่าผ่าตัด |
| 10 | ค่าเคมีบำบัด |

## ฟิลด์สำคัญที่ใช้บ่อย

| ฟิลด์ | ใช้ทำอะไร |
|-------|----------|
| `vn` | เชื่อม OPD (ถ้ามี) |
| `an` | เชื่อม IPD (ถ้ามี) |
| `icode` | เชื่อม `drugitems` |
| `qty` | จำนวนที่สั่ง |
| `unitprice` | ราคาต่อหน่วย |
| `sum_price` | ราคารวม (qty * unitprice) |
| `income` | ประเภทรายได้ |
| `item_type` | ประเภทรายการ |
| `rxdate` | วันที่สั่ง |

## ความสัมพันธ์

```sql
opitemrece.vn → ovst.vn                  (OPD)
opitemrece.an → ipt.an                   (IPD)
opitemrece.hn → patient.hn               (ผู้ป่วย)
opitemrece.icode → drugitems.icode       (ยา)
opitemrece.icode → nondrugitems.icode    (เวชภัณฑ์)
opitemrece.drugusage → drugusage.code    (วิธีใช้)
opitemrece.doctor → doctor.code          (แพทย์)
opitemrece.income → income.income        (รายได้)
```

## ตัวอย่าง Query

```sql
-- ดูรายการสั่งยาของ visit
SELECT 
    o.icode,
    d.name AS drug_name,
    d.strength,
    o.qty,
    o.unitprice,
    o.sum_price,
    du.name1 AS usage_name,
    o.iperday,
    o.iperdose,
    o.rxdate
FROM opitemrece o
LEFT JOIN drugitems d ON o.icode = d.icode
LEFT JOIN drugusage du ON o.drugusage = du.code
WHERE o.vn = '2024010100001'
  AND o.item_type = '1';

-- ดูค่ารักษาทั้งหมดของ visit
SELECT 
    o.icode,
    d.name,
    o.qty,
    o.unitprice,
    o.sum_price,
    i.name AS income_name,
    o.income
FROM opitemrece o
LEFT JOIN drugitems d ON o.icode = d.icode
LEFT JOIN income i ON o.income = i.income
WHERE o.vn = '2024010100001'
ORDER BY o.income;

-- รวมค่าใช้จ่ายตามประเภทรายได้
SELECT 
    o.income,
    i.name AS income_name,
    COUNT(*) AS item_count,
    SUM(o.sum_price) AS total_amount
FROM opitemrece o
LEFT JOIN income i ON o.income = i.income
WHERE o.vn = '2024010100001'
GROUP BY o.income;
```

## หมายเหตุ

- `opitemrece` เป็นตารางกลางที่สำคัญที่สุดในการคำนวณค่าใช้จ่าย
- `vn` จะมีค่าเมื่อเป็น OPD, `an` จะมีค่าเมื่อเป็น IPD
- ถ้าทั้ง `vn` และ `an` เป็น NULL อาจเป็นรายการที่ไม่ผูกกับ visit/admit
- `sum_price` = `qty` * `unitprice` (โดยปกติ)
- ใช้ `income` เพื่อแยกประเภทรายได้ในการทำรายงาน
