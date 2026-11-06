# ตาราง `patient` - ข้อมูลผู้ป่วยหลัก

## คำอธิบาย

ตารางนี้เป็นตารางหลักที่เก็บข้อมูลประจำตัวผู้ป่วยทุกคนในระบบ HOSxP ทุกครั้งที่มีการรับบริการ (OPD หรือ IPD) จะต้องอ้างอิงถึง `hn` ในตารางนี้

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `hos_guid` | varchar(38) | **PRI** | GUID ของระบบ |
| `hn` | varchar(9) | **UNI** | **เลขประจำตัวผู้ป่วย (Hospital Number)** - คีย์หลัก |
| `pname` | varchar(25) | MUL | คำนำหน้าชื่อ (นาย, นาง, น.ส.) |
| `fname` | varchar(100) | MUL | ชื่อ |
| `lname` | varchar(100) | MUL | นามสกุล |
| `occupation` | varchar(4) | - | รหัสอาชีพ |
| `citizenship` | char(3) | - | สัญชาติ |
| `birthday` | date | - | วันเกิด |
| `addrpart` | varchar(50) | - | บ้านเลขที่ |
| `moopart` | char(3) | - | หมู่ |
| `tmbpart` | char(2) | - | รหัสตำบล |
| `amppart` | char(2) | MUL | รหัสอำเภอ |
| `chwpart` | char(2) | MUL | รหัสจังหวัด |
| `bloodgrp` | varchar(20) | - | หมู่เลือด |
| `clinic` | varchar(100) | MUL | คลินิกประจำ |
| `deathday` | date | MUL | วันที่เสียชีวิต (ถ้ามี) |
| `drugallergy` | varchar(250) | - | ประวัติแพ้ยา (ข้อความ) |
| `familyno` | int | - | รหัสครอบครัว |
| `fathername` | varchar(100) | - | ชื่อบิดา |
| `firstday` | date | MUL | วันลงทะเบียนครั้งแรก |
| `hometel` | varchar(50) | - | โทรศัพท์บ้าน |
| `informaddr` | varchar(200) | - | ที่อยู่ผู้ติดต่อ |
| `informname` | varchar(100) | - | ชื่อผู้ติดต่อ |
| `informrelation` | varchar(50) | - | ความสัมพันธ์ผู้ติดต่อ |
| `informtel` | varchar(50) | - | โทรศัพท์ผู้ติดต่อ |
| `marrystatus` | char(1) | - | สถานภาพสมรส |
| `mathername` | varchar(100) | - | ชื่อมารดา |
| `nationality` | char(3) | - | สัญชาติ |
| `pttype` | char(2) | MUL | **สิทธิการรักษาปัจจุบัน** |
| `religion` | char(2) | - | ศาสนา |
| `sex` | char(1) | - | เพศ (1=ชาย, 2=หญิง) |
| `spsname` | varchar(100) | - | ชื่อคู่สมรส |
| `workaddr` | varchar(50) | - | ที่อยู่ที่ทำงาน |
| `worktel` | varchar(20) | - | โทรศัพท์ที่ทำงาน |
| `hcode` | varchar(5) | MUL | รหัสหน่วยบริการ |
| `cid` | varchar(13) | MUL | **เลขบัตรประชาชน** |
| `educate` | char(1) | - | การศึกษา |
| `last_update` | datetime | MUL | วันเวลาปรับปรุงล่าสุด |
| `road` | varchar(50) | - | ถนน |
| `passport_no` | varchar(25) | MUL | เลขพาสปอร์ต |
| `email` | varchar(50) | - | อีเมล |
| `birthtime` | time | - | เวลาเกิด |
| `last_visit` | date | MUL | วันมารับบริการล่าสุด |
| `death` | char(1) | - | สถานะเสียชีวิต |
| `height` | int | - | ส่วนสูง |
| `mobile_phone_number` | varchar(50) | - | เบอร์มือถือ |
| `full_name` | varchar(150) | - | ชื่อเต็ม |

## ฟิลด์สำคัญที่ใช้บ่อย

| ฟิลด์ | ใช้ทำอะไร |
|-------|----------|
| `hn` | เชื่อมทุกตาราง (OPD, IPD, Drug, Lab) |
| `cid` | ตรวจสอบตัวตน, ส่งเคลม |
| `pttype` | ตรวจสอบสิทธิการรักษา |
| `birthday` | คำนวณอายุ |
| `sex` | กรองตามเพศ |
| `firstday` | วันลงทะเบียนครั้งแรก |
| `last_visit` | วันมาล่าสุด |

## ความสัมพันธ์

```sql
-- patient เชื่อมกับตารางอื่น
patient.hn → ovst.hn        (ผู้ป่วยนอก)
patient.hn → ipt.hn         (ผู้ป่วยใน)
patient.hn → patient_pttype.hn   (สิทธิ)
patient.pttype → pttype.pttype   (รายละเอียดสิทธิ)
```

## ตัวอย่างข้อมูล

```sql
SELECT hn, pname, fname, lname, birthday, sex, pttype, cid
FROM patient
WHERE hn = '000000001';
```

ผลลัพธ์ตัวอย่าง:
| hn | pname | fname | lname | birthday | sex | pttype | cid |
|----|-------|-------|-------|----------|-----|--------|-----|
| 000000001 | นาย | ส*** | ท*** | 1985-03-15 | 1 | 01 | 1234*******890 |

## หมายเหตุ

- ฟิลด์ `fname`, `lname`, `cid` จะถูก mask โดยอัตโนมัติจากระบบ (แสดงบางส่วน)
- `hos_guid` เป็น Primary Key ทางเทคนิค แต่ `hn` เป็นตัวระบุทางธุรกิจที่ใช้งานจริง
- `sex`: 1 = ชาย, 2 = หญิง
