# ตาราง `ovst` - การ Visit ผู้ป่วยนอก

## คำอธิบาย

ตารางนี้เป็นตารางหลักของการรับบริการผู้ป่วยนอก (OPD) ทุกครั้งที่ผู้ป่วยมารับบริการจะสร้าง record ใหม่ในตารางนี้ โดยมี `vn` เป็นรหัสประจำการ visit นั้นๆ

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `hos_guid` | varchar(38) | **PRI** | GUID |
| `vn` | varchar(13) | **UNI** | **เลข Visit Number (VN)** - คีย์หลัก |
| `hn` | varchar(9) | MUL | เลขประจำตัวผู้ป่วย (เชื่อม `patient`) |
| `an` | varchar(9) | MUL | เลข Admit Number (ถ้าถูก Admit) |
| `vstdate` | date | MUL | **วันที่มารับบริการ** |
| `vsttime` | time | - | เวลาที่มารับบริการ |
| `doctor` | varchar(7) | MUL | รหัสแพทย์ที่ตรวจ |
| `hospmain` | varchar(9) | - | หน่วยบริการหลัก |
| `hospsub` | varchar(9) | - | หน่วยบริส่งเสริม |
| `oqueue` | int | - | ลำดับคิว |
| `ovstist` | char(2) | - | สถานะ visit (01=รอตรวจ, 02=ตรวจเสร็จ, 03=ส่งตรวจ) |
| `ovstost` | varchar(4) | - | สถานะออก (ตาย, รักษา, ส่งต่อ, หนีกลับ) |
| `pttype` | char(2) | MUL | สิทธิการรักษา |
| `pttypeno` | varchar(50) | MUL | เลขที่สิทธิ |
| `spclty` | char(2) | MUL | รหัสความเชี่ยวชาญ (แผนก) |
| `rcpt_disease` | varchar(100) | - | โรคที่ระบุในใบเสร็จ |
| `hcode` | varchar(5) | MUL | รหัสหน่วยบริการ |
| `cur_dep` | char(3) | MUL | แผนกปัจจุบัน |
| `last_dep` | char(3) | - | แผนกก่อนหน้า |
| `cur_dep_time` | time | - | เวลาที่แผนก |
| `rx_queue` | int | - | คิวรับยา |
| `diag_text` | varchar(250) | - | ข้อความวินิจฉัย |
| `main_dep` | char(3) | - | แผนกหลัก |
| `main_dep_queue` | int | - | คิวแผนกหลัก |
| `visit_type` | char(1) | - | ประเภทการ visit |
| `waiting` | char(1) | - | สถานะรอ |
| `o_refer_number` | int | MUL | เลขส่งตัวออก |
| `i_refer_number` | varchar(25) | MUL | เลขส่งตัวเข้า |
| `refer_type` | char(1) | - | ประเภทการส่งตัว |
| `staff` | varchar(25) | MUL | ผู้บันทึก |
| `command_doctor` | varchar(6) | - | แพทย์เจ้าของไข้ |
| `send_person` | varchar(150) | - | ผู้นำส่ง |
| `pt_priority` | int | - | ระดับความเร่งด่วน |
| `finance_lock` | char(1) | - | ล็อกการเงิน |
| `anonymous_visit` | char(1) | MUL | ผู้ป่วยนิรนาม |
| `ovst_key` | varchar(40) | - | รหัสกุญแจ visit |

## ฟิลด์สำคัญที่ใช้บ่อย

| ฟิลด์ | ใช้ทำอะไร |
|-------|----------|
| `vn` | เชื่อมทุกตาราง OPD (คัดกรอง, วินิจฉัย, สั่งยา, Lab) |
| `hn` | เชื่อมกับ `patient` |
| `vstdate` | กรองตามวันที่ |
| `doctor` | กรองตามแพทย์ |
| `pttype` | กรองตามสิทธิ |
| `spclty` | กรองตามแผนก |
| `ovstist` | ตรวจสอบสถานะ visit |
| `an` | ตรวจสอบว่า Admit หรือไม่ |

## ความสัมพันธ์

```sql
ovst.hn → patient.hn              (ข้อมูลผู้ป่วย)
ovst.vn → opdscreen.vn            (คัดกรอง)
ovst.vn → ovstdiag.vn             (วินิจฉัย)
ovst.vn → opitemrece.vn           (สั่งยา/ค่ารักษา)
ovst.vn → lab_head.vn             (สั่ง Lab)
ovst.doctor → doctor.code         (ข้อมูลแพทย์)
ovst.pttype → pttype.pttype       (ชื่อสิทธิ)
ovst.spclty → spclty.spclty       (ชื่อแผนก)
```

## สถานะ Visit (`ovstist`)

| รหัส | ความหมาย |
|------|---------|
| 01 | รอตรวจ |
| 02 | ตรวจเสร็จ |
| 03 | ส่งตรวจ |
| 04 | รอผล |
| 05 | รับยา |
| 99 | ยกเลิก |

## ตัวอย่าง Query

```sql
-- ดูข้อมูล visit วันนี้
SELECT vn, hn, vstdate, vsttime, doctor, pttype, spclty
FROM ovst
WHERE vstdate = CURDATE()
ORDER BY vsttime;

-- ดู visit พร้อมชื่อผู้ป่วย
SELECT 
    o.vn,
    o.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    o.vstdate,
    o.vsttime,
    d.name AS doctor_name,
    o.pttype
FROM ovst o
LEFT JOIN patient p ON o.hn = p.hn
LEFT JOIN doctor d ON o.doctor = d.code
WHERE o.vstdate = CURDATE();
```

## หมายเหตุ

- `vn` เป็นรหัสเฉพาะของแต่ละการ visit จะไม่ซ้ำกัน
- หาก `an` มีค่า แสดงว่าผู้ป่วยรายนี้ถูก Admit เป็นผู้ป่วยใน
- `ovstist` ใช้ตรวจสอบสถานะปัจจุบันของผู้ป่วยในระบบ
- `cur_dep` บ่งบอกว่าผู้ป่วยอยู่แผนกไหนในขณะนั้น
