# HOSxP Master Database Knowledge Base & Data Dictionary
> Consolidated reference for AI prompts and Hospital Informatics.

---

## File: 01-patient/common-queries.md

# ตัวอย่าง Query โมดูล Patient

## 1. ค้นหาผู้ป่วยจาก HN

```sql
SELECT hn, pname, fname, lname, birthday, sex, pttype, cid
FROM patient
WHERE hn = '000000001';
```

## 2. ค้นหาผู้ป่วยจากชื่อ

```sql
-- ค้นหาจากชื่อ (模糊搜索)
SELECT hn, pname, fname, lname, birthday, sex
FROM patient
WHERE fname LIKE '%สมชาย%'
   OR lname LIKE '%ใจดี%';

-- ใช้ Soundex สำหรับค้นหาที่ออกเสียงคล้ายกัน
SELECT hn, pname, fname, lname
FROM patient
WHERE fname_soundex LIKE '%SOMC%'
   OR lname_soundex LIKE '%JAI%'
```

## 3. ค้นหาผู้ป่วยจากเลขบัตรประชาชน

```sql
SELECT hn, pname, fname, lname, birthday, cid
FROM patient
WHERE cid = '1234567890123';
```

## 4. ดูข้อมูลผู้ป่วยพร้อมที่อยู่

```sql
SELECT 
    p.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS full_name,
    p.birthday,
    TIMESTAMPDIFF(YEAR, p.birthday, CURDATE()) AS age,
    p.sex,
    CONCAT(p.addrpart, ' หมู่ ', p.moopart) AS address,
    p.hometel,
    p.mobile_phone_number
FROM patient p
WHERE p.hn = '000000001';
```

## 5. ดูผู้ป่วยพร้อมสิทธิปัจจุบัน

```sql
SELECT 
    p.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS full_name,
    p.pttype AS current_pttype,
    pt.name AS pttype_name,
    pp.pttypeno,
    pp.begin_date,
    pp.expire_date
FROM patient p
LEFT JOIN pttype pt ON p.pttype = pt.pttype
LEFT JOIN patient_pttype pp ON p.hn = pp.hn AND p.pttype = pp.pttype
WHERE p.hn = '000000001';
```

## 6. นับจำนวนผู้ป่วยตามสิทธิ

```sql
SELECT 
    p.pttype,
    pt.name AS pttype_name,
    COUNT(*) AS patient_count
FROM patient p
LEFT JOIN pttype pt ON p.pttype = pt.pttype
GROUP BY p.pttype
ORDER BY patient_count DESC;
```

## 7. ผู้ป่วยที่มารับบริการล่าสุด

```sql
SELECT 
    p.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS full_name,
    p.last_visit,
    DATEDIFF(CURDATE(), p.last_visit) AS days_since_last_visit
FROM patient p
WHERE p.last_visit IS NOT NULL
ORDER BY p.last_visit DESC
LIMIT 50;
```

## 8. ผู้ป่วยใหม่ (ลงทะเบียนวันนี้)

```sql
SELECT 
    p.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS full_name,
    p.firstday,
    p.birthday,
    TIMESTAMPDIFF(YEAR, p.birthday, CURDATE()) AS age
FROM patient p
WHERE p.firstday = CURDATE()
ORDER BY p.reg_time;
```

## 9. ผู้ป่วยตามช่วงอายุ

```sql
SELECT 
    p.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS full_name,
    p.birthday,
    TIMESTAMPDIFF(YEAR, p.birthday, CURDATE()) AS age
FROM patient p
WHERE TIMESTAMPDIFF(YEAR, p.birthday, CURDATE()) BETWEEN 60 AND 80
ORDER BY age;
```

## 10. ตัวอย่าง Vale Query

```vale
-- Vale: ดึงข้อมูลผู้ป่วยตาม HN
SELECT 
    hn,
    CONCAT(pname, fname, ' ', lname) AS patient_name,
    birthday,
    sex,
    pttype
FROM patient
WHERE hn = @hn;

-- Vale: ค้นหาผู้ป่วยจากชื่อ
SELECT 
    hn,
    CONCAT(pname, fname, ' ', lname) AS patient_name,
    cid,
    birthday
FROM patient
WHERE fname LIKE @name_pattern
   OR lname LIKE @name_pattern;

-- Vale: ดูสิทธิผู้ป่วย
SELECT 
    pp.pttype,
    pt.name AS pttype_name,
    pp.begin_date,
    pp.expire_date,
    pp.pttypeno
FROM patient_pttype pp
LEFT JOIN pttype pt ON pp.pttype = pt.pttype
WHERE pp.hn = @hn
  AND (pp.expire_date >= CURDATE() OR pp.expire_date IS NULL)
ORDER BY pp.begin_date DESC;
```

## เคล็ดลับ

- ใช้ `TIMESTAMPDIFF(YEAR, birthday, CURDATE())` เพื่อคำนวณอายุ
- `sex = '1'` = ชาย, `sex = '2'` = หญิง
- ฟิลด์ `fname`, `lname`, `cid` ถูก mask โดยอัตโนมัติ
- `last_visit` ช่วยตรวจสอบว่าผู้ป่วยยังมารับบริการอยู่หรือไม่


---

## File: 01-patient/patient-address.md

# ตาราง `patient_address` - รหัสที่อยู่ผู้ป่วย

## คำอธิบาย

ตารางนี้เก็บรหัสจังหวัด อำเภอ และตำบล ของผู้ป่วย แยกจากตาราง `patient` ที่เก็บข้อมูลที่อยู่ในรูปข้อความ เพื่อให้สามารถ query และรายงานตามพื้นที่ได้ง่าย

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `hn` | varchar(9) | **PRI** | เลขประจำตัวผู้ป่วย (เชื่อมกับ `patient`) |
| `province_code` | varchar(2) | - | รหัสจังหวัด |
| `district_code` | varchar(4) | - | รหัสอำเภอ |
| `tambol_code` | varchar(6) | - | รหัสตำบล |

## ความสัมพันธ์

```sql
patient_address.hn → patient.hn
patient_address.province_code → thaiaddress.chwpart
patient_address.district_code → thaiaddress.amppart  
patient_address.tambol_code → thaiaddress.tmbpart
```

## หลักการใช้งาน

ตาราง `patient` เก็บที่อยู่ในรูปข้อความ (`addrpart`, `moopart`, `tmbpart`, `amppart`, `chwpart`) แต่บางครั้งเป็นรหัส บางครั้งเป็นชื่อ ทำให้ยากต่อการ query

ตาราง `patient_address` ช่วยให้สามารถ:
- ค้นหาผู้ป่วยตามจังหวัด/อำเภอ/ตำบลได้แม่นยำ
- Join กับตาราง `thaiaddress` เพื่อแสดงชื่อจังหวัด/อำเภอ/ตำบล
- ทำรายงานเชิงพื้นที่ (GIS report)

## ตัวอย่าง Query

```sql
-- ดูที่อยู่ผู้ป่วยพร้อมชื่อจังหวัด
SELECT 
    p.hn,
    p.fname,
    p.lname,
    p.addrpart,
    pa.province_code,
    pa.district_code,
    pa.tambol_code
FROM patient p
LEFT JOIN patient_address pa ON p.hn = pa.hn
WHERE p.hn = '000000001';
```

## หมายเหตุ

- ไม่ใช่ทุกคนจะมี record ใน `patient_address` (บางคนอาจลงทะเบียนก่อนสร้างตารางนี้)
- รหัสตำบล (`tambol_code`) มี 6 หลัก ประกอบด้วย จังหวัด(2) + อำเภอ(2) + ตำบล(2)


---

## File: 01-patient/patient-pttype.md

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


---

## File: 01-patient/patient.md

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


---

## File: 02-opd/common-queries.md

# ตัวอย่าง Query โมดูล OPD

## 1. ผู้ป่วยนอกวันนี้พร้อมชื่อ

```sql
SELECT 
    o.vn,
    o.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    o.vstdate,
    o.vsttime,
    d.name AS doctor_name,
    o.pttype,
    pt.name AS pttype_name,
    o.spclty,
    s.name AS spclty_name
FROM ovst o
LEFT JOIN patient p ON o.hn = p.hn
LEFT JOIN doctor d ON o.doctor = d.code
LEFT JOIN pttype pt ON o.pttype = pt.pttype
LEFT JOIN spclty s ON o.spclty = s.spclty
WHERE o.vstdate = CURDATE()
ORDER BY o.vsttime;
```

## 2. ผู้ป่วยนอกพร้อมข้อมูลคัดกรอง

```sql
SELECT 
    o.vn,
    o.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    o.vstdate,
    s.bps,
    s.bpd,
    s.bw,
    s.height,
    s.temperature,
    s.pulse,
    s.cc
FROM ovst o
LEFT JOIN patient p ON o.hn = p.hn
LEFT JOIN opdscreen s ON o.vn = s.vn
WHERE o.vstdate = CURDATE()
ORDER BY o.vsttime;
```

## 3. ผู้ป่วยนอกพร้อมการวินิจฉัย

```sql
SELECT 
    o.vn,
    o.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    o.vstdate,
    d.icd10,
    i.name AS disease_name,
    d.diagtype
FROM ovst o
LEFT JOIN patient p ON o.hn = p.hn
LEFT JOIN ovstdiag d ON o.vn = d.vn AND d.diagtype = '1'
LEFT JOIN icd101 i ON d.icd10 = i.icd10
WHERE o.vstdate = CURDATE()
ORDER BY o.vsttime;
```

## 4. นับจำนวน visit รายวัน

```sql
SELECT 
    vstdate,
    COUNT(*) AS visit_count,
    COUNT(DISTINCT hn) AS patient_count
FROM ovst
WHERE vstdate BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY vstdate
ORDER BY vstdate;
```

## 5. นับจำนวน visit ตามแผนก

```sql
SELECT 
    o.spclty,
    s.name AS spclty_name,
    COUNT(*) AS visit_count
FROM ovst o
LEFT JOIN spclty s ON o.spclty = s.spclty
WHERE o.vstdate = CURDATE()
GROUP BY o.spclty
ORDER BY visit_count DESC;
```

## 6. นับจำนวน visit ตามแพทย์

```sql
SELECT 
    o.doctor,
    d.name AS doctor_name,
    COUNT(*) AS visit_count
FROM ovst o
LEFT JOIN doctor d ON o.doctor = d.code
WHERE o.vstdate = CURDATE()
GROUP BY o.doctor
ORDER BY visit_count DESC;
```

## 7. ผู้ป่วยที่มาซ้ำภายใน 7 วัน

```sql
SELECT 
    o1.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    o1.vn AS first_vn,
    o1.vstdate AS first_visit,
    o2.vn AS repeat_vn,
    o2.vstdate AS repeat_visit,
    DATEDIFF(o2.vstdate, o1.vstdate) AS days_between
FROM ovst o1
JOIN ovst o2 ON o1.hn = o2.hn AND o1.vn < o2.vn
LEFT JOIN patient p ON o1.hn = p.hn
WHERE DATEDIFF(o2.vstdate, o1.vstdate) <= 7
  AND o1.vstdate BETWEEN '2024-01-01' AND '2024-01-31'
ORDER BY o1.hn, o1.vstdate;
```

## 8. ผู้ป่วยที่ยังไม่ได้วินิจฉัย

```sql
SELECT 
    o.vn,
    o.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    o.vstdate,
    o.vsttime
FROM ovst o
LEFT JOIN patient p ON o.hn = p.hn
LEFT JOIN ovstdiag d ON o.vn = d.vn
WHERE o.vstdate = CURDATE()
  AND d.vn IS NULL;
```

## 9. ตัวอย่าง Vale Query

```vale
-- Vale: ดึงข้อมูล visit วันนี้
SELECT 
    o.vn,
    o.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    o.vstdate,
    o.vsttime,
    d.name AS doctor_name
FROM ovst o
LEFT JOIN patient p ON o.hn = p.hn
LEFT JOIN doctor d ON o.doctor = d.code
WHERE o.vstdate = CURDATE()
ORDER BY o.vsttime;

-- Vale: ดูคัดกรองของ visit
SELECT 
    s.vn,
    s.bps,
    s.bpd,
    s.bw,
    s.height,
    s.temperature,
    s.pulse,
    s.cc
FROM opdscreen s
WHERE s.vn = @vn;

-- Vale: ดูการวินิจฉัยของ visit
SELECT 
    d.icd10,
    i.name AS disease_name,
    d.diagtype
FROM ovstdiag d
LEFT JOIN icd101 i ON d.icd10 = i.icd10
WHERE d.vn = @vn
ORDER BY d.diagtype;
```

## เคล็ดลับ

- ใช้ `o.vstdate = CURDATE()` สำหรับข้อมูลวันนี้
- ใช้ `o.vstdate BETWEEN '2024-01-01' AND '2024-01-31'` สำหรับช่วงเวลา
- `COUNT(DISTINCT hn)` จะได้จำนวนผู้ป่วยที่ไม่ซ้ำกัน
- `diagtype = '1'` คือโรคหลัก (PDX) ที่ใช้สำหรับส่งเคลม


---

## File: 02-opd/opdscreen.md

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


---

## File: 02-opd/ovst.md

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


---

## File: 02-opd/ovstdiag.md

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


---

## File: 03-ipd/common-queries.md

# ตัวอย่าง Query โมดูล IPD

## 1. ผู้ป่วยที่ยัง Admit อยู่

```sql
SELECT 
    i.an,
    i.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    TIMESTAMPDIFF(YEAR, p.birthday, CURDATE()) AS age,
    p.sex,
    i.regdate,
    i.ward,
    w.name AS ward_name,
    i.cur_bedno,
    i.admdoctor,
    d.name AS doctor_name,
    DATEDIFF(CURDATE(), i.regdate) AS los_days
FROM ipt i
LEFT JOIN patient p ON i.hn = p.hn
LEFT JOIN ward w ON i.ward = w.ward
LEFT JOIN doctor d ON i.admdoctor = d.code
WHERE i.dchdate IS NULL
ORDER BY i.ward, i.cur_bedno;
```

## 2. ผู้ป่วยที่ Discharge วันนี้

```sql
SELECT 
    i.an,
    i.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    i.regdate,
    i.dchdate,
    DATEDIFF(i.dchdate, i.regdate) AS los_days,
    i.dchtype,
    CASE i.dchtype 
        WHEN '01' THEN 'หาย/ดีขึ้น'
        WHEN '02' THEN 'ยังไม่หาย'
        WHEN '03' THEN 'ตาย'
        WHEN '04' THEN 'หนีกลับ'
        WHEN '05' THEN 'ส่งต่อ'
        WHEN '08' THEN 'ส่งต่อตามสิทธิ'
        WHEN '09' THEN 'ปฏิเสธการรักษา'
        ELSE i.dchtype
    END AS discharge_status,
    i.ward,
    w.name AS ward_name
FROM ipt i
LEFT JOIN patient p ON i.hn = p.hn
LEFT JOIN ward w ON i.ward = w.ward
WHERE i.dchdate = CURDATE()
ORDER BY i.dchtime;
```

## 3. จำนวนผู้ป่วยในแต่ละ Ward

```sql
SELECT 
    i.ward,
    w.name AS ward_name,
    COUNT(*) AS patient_count
FROM ipt i
LEFT JOIN ward w ON i.ward = w.ward
WHERE i.dchdate IS NULL
GROUP BY i.ward
ORDER BY patient_count DESC;
```

## 4. สรุป Admit/Discharge รายวัน

```sql
SELECT 
    regdate AS date,
    COUNT(*) AS admit_count,
    SUM(CASE WHEN dchdate = regdate THEN 1 ELSE 0 END) AS same_day_dch,
    SUM(CASE WHEN dchdate IS NULL THEN 1 ELSE 0 END) AS still_admit
FROM ipt
WHERE regdate BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY regdate
ORDER BY regdate;
```

## 5. ค่าเฉลี่ย LOS ตาม Ward

```sql
SELECT 
    i.ward,
    w.name AS ward_name,
    COUNT(*) AS total_cases,
    ROUND(AVG(DATEDIFF(i.dchdate, i.regdate)), 2) AS avg_los,
    ROUND(MIN(DATEDIFF(i.dchdate, i.regdate)), 0) AS min_los,
    ROUND(MAX(DATEDIFF(i.dchdate, i.regdate)), 0) AS max_los
FROM ipt i
LEFT JOIN ward w ON i.ward = w.ward
WHERE i.dchdate IS NOT NULL
  AND i.regdate BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY i.ward
ORDER BY avg_los DESC;
```

## 6. ผู้ป่วยใน พร้อมการวินิจฉัยหลัก

```sql
SELECT 
    i.an,
    i.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    i.regdate,
    d.icd10,
    ic.name AS disease_name,
    i.ward,
    w.name AS ward_name
FROM ipt i
LEFT JOIN patient p ON i.hn = p.hn
LEFT JOIN ward w ON i.ward = w.ward
LEFT JOIN iptdiag d ON i.an = d.an AND d.diagtype = '1'
LEFT JOIN icd101 ic ON d.icd10 = ic.icd10
WHERE i.dchdate IS NULL;
```

## 7. ประวัติการย้ายเตียง

```sql
SELECT 
    bm.an,
    i.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    bm.movedate,
    bm.movetime,
    bm.oward,
    ow.name AS old_ward,
    bm.obedno AS old_bed,
    bm.nward,
    nw.name AS new_ward,
    bm.nbedno AS new_bed,
    bm.movereason
FROM iptbedmove bm
LEFT JOIN ipt i ON bm.an = i.an
LEFT JOIN patient p ON i.hn = p.hn
LEFT JOIN ward ow ON bm.oward = ow.ward
LEFT JOIN ward nw ON bm.nward = nw.ward
WHERE bm.an = '650000001'
ORDER BY bm.movedate, bm.movetime;
```

## 8. ตัวอย่าง Vale Query

```vale
-- Vale: ผู้ป่วยที่ยัง Admit อยู่
SELECT 
    i.an,
    i.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    i.regdate,
    i.ward,
    w.name AS ward_name,
    i.cur_bedno,
    DATEDIFF(CURDATE(), i.regdate) AS los_days
FROM ipt i
LEFT JOIN patient p ON i.hn = p.hn
LEFT JOIN ward w ON i.ward = w.ward
WHERE i.dchdate IS NULL
ORDER BY i.ward, i.cur_bedno;

-- Vale: ค้นหาผู้ป่วยใน AN
SELECT 
    i.an,
    i.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    i.regdate,
    i.dchdate,
    i.ward,
    w.name AS ward_name,
    i.cur_bedno
FROM ipt i
LEFT JOIN patient p ON i.hn = p.hn
LEFT JOIN ward w ON i.ward = w.ward
WHERE i.an = @an;
```

## เคล็ดลัด

- `dchdate IS NULL` = ยัง Admit อยู่
- `DATEDIFF(dchdate, regdate)` = จำนวนวัน LOS
- ใช้ `CASE` เพื่อแปลงรหัส `dchtype` เป็นข้อความ
- ผู้ป่วยที่เสียชีวิต: `dchtype = '03'`
- ผู้ป่วยที่หนีกลับ: `dchtype = '04'`


---

## File: 03-ipd/ipt.md

# ตาราง `ipt` - การ Admit ผู้ป่วยใน

## คำอธิบาย

ตารางนี้เป็นตารางหลักของการรับผู้ป่วยใน (Inpatient/Admit) ทุกครั้งที่มีการ Admit ผู้ป่วยจะสร้าง record ใหม่ในตารางนี้ โดยมี `an` เป็นรหัสประจำการ Admit นั้นๆ

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `an` | varchar(9) | **PRI** | **เลข Admit Number (AN)** - คีย์หลัก |
| `hn` | varchar(9) | MUL | เลขประจำตัวผู้ป่วย (เชื่อม `patient`) |
| `vn` | varchar(13) | MUL | เลข VN (ถ้ามี OPD visit ก่อน) |
| `regdate` | date | MUL | **วันที่ Admit** |
| `regtime` | time | MUL | เวลาที่ Admit |
| `dchdate` | date | MUL | **วันที่ Discharge** |
| `dchtime` | time | - | เวลาที่ Discharge |
| `dchstts` | char(2) | MUL | สถานะ Discharge |
| `dchtype` | char(2) | - | **ประเภทการ Discharge** |
| `ward` | varchar(4) | MUL | Ward ปัจจุบัน |
| `cur_bedno` | varchar(6) | - | เตียงปัจจุบัน |
| `first_ward` | varchar(4) | - | Ward แรก |
| `admdoctor` | varchar(7) | MUL | แพทย์ที่ Admit |
| `dch_doctor` | varchar(7) | - | แพทย์ที่ Discharge |
| `incharge_doctor` | varchar(7) | - | แพทย์เจ้าของไข้ |
| `rxdoctor` | varchar(7) | - | แพทย์สั่งยา |
| `pttype` | char(2) | MUL | สิทธิการรักษา |
| `spclty` | char(2) | MUL | ความเชี่ยวชาญ |
| `ipt_spclty` | char(2) | - | ความเชี่ยวชาญ IPD |
| `prediag` | varchar(250) | - | การวินิจฉัยเบื้องต้น |
| `provision_dx` | varchar(200) | - | การวินิจฉัยโดยประมาณ |
| `provision_dx_icd` | varchar(9) | - | รหัส ICD10 โดยประมาณ |
| `rcpt_disease` | varchar(100) | - | โรคที่ระบุในใบเสร็จ |
| `ivstist` | char(2) | - | สถานะ IPD |
| `ivstost` | varchar(4) | - | สถานะออก |
| `ipt_type` | tinyint | MUL | ประเภทการ Admit |
| `bw` | int | - | น้ำหนัก (kg) |
| `body_height` | int | - | ส่วนสูง (cm) |
| `gravidity` | tinyint | - | จำนวนครั้งตั้งครรภ์ |
| `parity` | tinyint | - | จำนวนครั้งคลอด |
| `living_children` | tinyint | - | จำนวนบุตรที่มีชีวิต |
| `leave_home_day` | int | - | จำนวนวันลาบ้าน |
| `operation_status` | char(1) | - | สถานะผ่าตัด |
| `operation_status_id` | int | - | รหัสสถานะผ่าตัด |
| `finance_lock` | char(1) | - | ล็อกการเงิน |
| `finance_status_flag` | int | - | สถานะการเงิน |
| `finance_summary_date` | date | - | วันสรุปการเงิน |
| `finance_transfer` | char(1) | - | โอนเงิน |
| `confirm_discharge` | char(1) | MUL | ยืนยัน Discharge |
| `data_ok` | char(1) | MUL | ข้อมูลครบถ้วน |
| `data_exp_date` | date | MUL | วันหมดอายุข้อมูล |
| `auto_charge_amount` | double | - | ยอดค่าใช้จ่ายอัตโนมัติ |
| `act_money_limit` | double | - | วงเงิน |
| `drg` | varchar(5) | - | รหัส DRG |
| `mdc` | char(2) | - | Major Diagnostic Category |
| `rw` | double | - | Relative Weight |
| `adjrw` | double | - | Adjusted RW |
| `grouper_version` | varchar(15) | - | เวอร์ชัน Grouper |
| `grouper_actlos` | int | - | Actual LOS (Grouper) |
| `reimburse_price` | double | - | ราคาเบิกจ่าย |
| `err` | int | - | ข้อผิดพลาด Grouper |
| `warn` | int | - | คำเตือน Grouper |
| `oldcode` | varchar(20) | - | รหัสเก่า |
| `update_datetime` | datetime | - | วันเวลาปรับปรุง |
| `dateupdate` | timestamp | - | วันเวลาปรับปรุง (auto) |

## ฟิลด์สำคัญที่ใช้บ่อย

| ฟิลด์ | ใช้ทำอะไร |
|-------|----------|
| `an` | เชื่อมทุกตาราง IPD (วินิจฉัย, ย้ายเตียง, สั่งยา) |
| `hn` | เชื่อมกับ `patient` |
| `vn` | เชื่อมกับ `ovst` (ถ้ามี) |
| `regdate` | วัน Admit |
| `dchdate` | วัน Discharge (NULL = ยัง Admit อยู่) |
| `ward` | Ward ปัจจุบัน |
| `cur_bedno` | เตียงปัจจุบัน |
| `dchtype` | ประเภทการ Discharge |

## ประเภทการ Discharge (`dchtype`)

| รหัส | ความหมาย |
|------|---------|
| 01 | หาย/ดีขึ้น |
| 02 | ยังไม่หาย |
| 03 | ตาย |
| 04 | หนีกลับ |
| 05 | ส่งต่อ |
| 08 | ส่งต่อตามสิทธิ |
| 09 | ปฏิเสธการรักษา |

## ความสัมพันธ์

```sql
ipt.hn → patient.hn              (ข้อมูลผู้ป่วย)
ipt.vn → ovst.vn                 (OPD visit ก่อน Admit)
ipt.an → iptdiag.an              (วินิจฉัย)
ipt.an → iptbedmove.an           (ย้ายเตียง)
ipt.an → iptdrugorder.an         (สั่งยา)
ipt.an → opitemrece.an           (ค่ารักษา)
ipt.admdoctor → doctor.code      (แพทย์)
ipt.ward → ward.ward             (ชื่อ Ward)
```

## ตัวอย่าง Query

```sql
-- ผู้ป่วยที่ยัง Admit อยู่
SELECT 
    i.an,
    i.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    i.regdate,
    i.ward,
    w.name AS ward_name,
    i.cur_bedno,
    i.admdoctor,
    d.name AS doctor_name
FROM ipt i
LEFT JOIN patient p ON i.hn = p.hn
LEFT JOIN ward w ON i.ward = w.ward
LEFT JOIN doctor d ON i.admdoctor = d.code
WHERE i.dchdate IS NULL;

-- คำนวณ LOS (Length of Stay)
SELECT 
    i.an,
    i.hn,
    i.regdate,
    i.dchdate,
    DATEDIFF(IFNULL(i.dchdate, CURDATE()), i.regdate) AS los_days
FROM ipt i
WHERE i.an = '650000001';

-- ผู้ป่วยที่ Discharge วันนี้
SELECT 
    i.an,
    i.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    i.dchdate,
    i.dchtype,
    CASE i.dchtype 
        WHEN '01' THEN 'หาย/ดีขึ้น'
        WHEN '03' THEN 'ตาย'
        WHEN '04' THEN 'หนีกลับ'
        WHEN '05' THEN 'ส่งต่อ'
        ELSE i.dchtype
    END AS discharge_status
FROM ipt i
LEFT JOIN patient p ON i.hn = p.hn
WHERE i.dchdate = CURDATE();
```

## หมายเหตุ

- `dchdate IS NULL` หมายถึงผู้ป่วยยัง Admit อยู่
- `LOS` (Length of Stay) = จำนวนวันที่พักรักษา = dchdate - regdate
- `dchtype = '03'` คือผู้ป่วยเสียชีวิต ควรตรวจสอบกับ `iptdeath`
- `drg`, `mdc`, `rw` ใช้สำหรับการคำนวณค่าใช้จ่ายตาม DRG


---

## File: 03-ipd/iptbedmove.md

# ตาราง `iptbedmove` - การย้ายเตียง/Ward

## คำอธิบาย

ตารางนี้เก็บประวัติการย้ายเตียงและย้าย Ward ของผู้ป่วยใน ทุกครั้งที่มีการย้ายเตียงจะสร้าง record ใหม่ในตารางนี้ ช่วยให้ทราบประวัติการเคลื่อนย้ายของผู้ป่วยตลอดการ Admit

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `iptbedmove_id` | int | **PRI** | รหัส running number |
| `an` | varchar(9) | MUL | เลข Admit Number |
| `movedate` | date | - | **วันที่ย้าย** |
| `movetime` | time | - | เวลาที่ย้าย |
| `oward` | varchar(9) | - | **Ward เดิม** |
| `obedno` | varchar(9) | - | **เตียงเดิม** |
| `nward` | varchar(9) | - | **Ward ใหม่** |
| `nbedno` | varchar(9) | - | **เตียงใหม่** |
| `nroomno` | varchar(10) | - | ห้องใหม่ |
| `spclty` | char(2) | - | ความเชี่ยวชาญ |
| `movereason` | varchar(250) | - | เหตุผลการย้าย |
| `entry_datetime` | datetime | - | วันเวลาบันทึก |
| `staff` | varchar(50) | - | ผู้บันทึก |
| `hos_guid` | varchar(38) | MUL | GUID |

## ความสัมพันธ์

```sql
iptbedmove.an → ipt.an           (ข้อมูล Admit)
iptbedmove.oward → ward.ward     (Ward เดิม)
iptbedmove.nward → ward.ward     (Ward ใหม่)
```

## หลักการทำงาน

1. ผู้ป่วย Admit → บันทึก ward/เตียงแรกใน `ipt` และสร้าง record ใน `iptbedmove`
2. มีการย้ายเตียง → สร้าง record ใหม่ใน `iptbedmove` โดย:
   - `oward`/`obedno` = ward/เตียงเดิม
   - `nward`/`nbedno` = ward/เตียงใหม่
3. อัปเดต `ipt.ward` และ `ipt.cur_bedno` เป็นค่าใหม่

## ตัวอย่าง Query

```sql
-- ประวัติการย้ายเตียงของผู้ป่วย
SELECT 
    bm.an,
    bm.movedate,
    bm.movetime,
    bm.oward,
    ow.name AS old_ward_name,
    bm.obedno AS old_bed,
    bm.nward,
    nw.name AS new_ward_name,
    bm.nbedno AS new_bed,
    bm.movereason
FROM iptbedmove bm
LEFT JOIN ward ow ON bm.oward = ow.ward
LEFT JOIN ward nw ON bm.nward = nw.ward
WHERE bm.an = '650000001'
ORDER BY bm.movedate, bm.movetime;

-- จำนวนวันที่พักในแต่ละ Ward
SELECT 
    bm.an,
    bm.nward,
    w.name AS ward_name,
    MIN(bm.movedate) AS first_date,
    MAX(COALESCE(next_bm.movedate, i.dchdate, CURDATE())) AS last_date,
    DATEDIFF(MAX(COALESCE(next_bm.movedate, i.dchdate, CURDATE())), MIN(bm.movedate)) AS days
FROM iptbedmove bm
LEFT JOIN iptbedmove next_bm ON bm.an = next_bm.an AND bm.iptbedmove_id < next_bm.iptbedmove_id
LEFT JOIN ward w ON bm.nward = w.ward
LEFT JOIN ipt i ON bm.an = i.an
WHERE bm.an = '650000001'
GROUP BY bm.an, bm.nward, bm.iptbedmove_id
ORDER BY MIN(bm.movedate);
```

## หมายเหตุ

- ถ้า `oward` เป็น NULL หรือว่าง แสดงว่าเป็นการ Admit ครั้งแรก
- สามารถนับจำนวนครั้งที่ย้ายเตียงได้จากจำนวน record
- ใช้ตรวจสอบการใช้งาน Ward/เตียงในแต่ละช่วงเวลา


---

## File: 03-ipd/iptdiag.md

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


---

## File: 04-drug/common-queries.md

# ตัวอย่าง Query โมดูล Drug

## 1. รายการยาที่สั่งใน visit

```sql
SELECT 
    o.vn,
    o.icode,
    d.name AS drug_name,
    d.strength,
    o.qty,
    o.unitprice,
    o.sum_price,
    du.name1 AS usage_name,
    o.iperday,
    o.iperdose,
    o.rxdate,
    o.doctor
FROM opitemrece o
LEFT JOIN drugitems d ON o.icode = d.icode
LEFT JOIN drugusage du ON o.drugusage = du.code
WHERE o.vn = '2024010100001'
  AND o.item_type = '1'
ORDER BY o.item_no;
```

## 2. ยาที่สั่งบ่อยที่สุด (Top 20)

```sql
SELECT 
    o.icode,
    d.name AS drug_name,
    d.strength,
    COUNT(*) AS order_count,
    SUM(o.qty) AS total_qty
FROM opitemrece o
LEFT JOIN drugitems d ON o.icode = d.icode
WHERE o.item_type = '1'
  AND o.rxdate BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY o.icode
ORDER BY order_count DESC
LIMIT 20;
```

## 3. มูลค่าการใช้ยารายเดือน

```sql
SELECT 
    DATE_FORMAT(o.rxdate, '%Y-%m') AS month,
    COUNT(DISTINCT o.vn) AS visit_count,
    COUNT(*) AS item_count,
    SUM(o.sum_price) AS total_amount
FROM opitemrece o
WHERE o.item_type = '1'
  AND o.rxdate BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY DATE_FORMAT(o.rxdate, '%Y-%m')
ORDER BY month;
```

## 4. ค่าใช้จ่ายรวมของ visit (แยกตามประเภทรายได้)

```sql
SELECT 
    o.vn,
    o.hn,
    i.name AS income_name,
    COUNT(*) AS item_count,
    SUM(o.sum_price) AS total_amount
FROM opitemrece o
LEFT JOIN income i ON o.income = i.income
WHERE o.vn = '2024010100001'
GROUP BY o.vn, o.income
ORDER BY o.income;
```

## 5. ยาปฏิชีวนะที่ใช้

```sql
SELECT 
    o.vn,
    o.hn,
    o.icode,
    d.name AS drug_name,
    d.strength,
    o.qty,
    o.rxdate,
    doc.name AS doctor_name
FROM opitemrece o
LEFT JOIN drugitems d ON o.icode = d.icode
LEFT JOIN doctor doc ON o.doctor = doc.code
WHERE d.antibiotic = 'Y'
  AND o.rxdate BETWEEN '2024-01-01' AND '2024-01-31'
ORDER BY o.rxdate;
```

## 6. สต็อกยา

```sql
-- ยาที่ใกล้หมดสต็อก (ต่ำกว่า minlevel)
SELECT 
    d.icode,
    d.name,
    s.department_id,
    s.qty AS current_stock,
    d.minlevel,
    d.maxlevel
FROM drugitems d
JOIN drugstock s ON d.icode = s.icode
WHERE s.qty < d.minlevel
  AND d.istatus = 'Y';
```

## 7. ตัวอย่าง Vale Query

```vale
-- Vale: รายการยาของ visit
SELECT 
    o.icode,
    d.name AS drug_name,
    d.strength,
    o.qty,
    o.sum_price,
    du.name1 AS usage_name,
    o.iperday,
    o.iperdose
FROM opitemrece o
LEFT JOIN drugitems d ON o.icode = d.icode
LEFT JOIN drugusage du ON o.drugusage = du.code
WHERE o.vn = @vn
  AND o.item_type = '1';

-- Vale: สรุปค่าใช้จ่าย visit
SELECT 
    i.name AS income_name,
    COUNT(*) AS item_count,
    SUM(o.sum_price) AS total_amount
FROM opitemrece o
LEFT JOIN income i ON o.income = i.income
WHERE o.vn = @vn
GROUP BY o.income
ORDER BY total_amount DESC;
```

## เคล็ดลับ

- `item_type = '1'` คือยาเท่านั้น
- `item_type` อื่นๆ: 2=บริการ, 3=Lab, 4=X-Ray, 5=ห้อง, 6=อาหาร
- ใช้ `income` เพื่อแยกประเภทรายได้
- `sum_price` คือมูลค่ารวม (qty * unitprice)
- ยาที่เลิกใช้: `d.istatus != 'Y'`


---

## File: 04-drug/drugitems.md

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


---

## File: 04-drug/opitemrece.md

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


---

## File: 05-finance/common-queries.md

# คำสั่ง SQL ที่ใช้บ่อยในงานการเงิน

เอกสารนี้รวบรวมคำสั่ง SQL ที่ใช้บ่อยในงานด้านการเงินของ HOSxP พร้อมคำอธิบายเป็นภาษาไทย

---

## 1. ดึงรายการค่าใช้จ่ายของการมารับบริการหนึ่งครั้ง

ดึงรายการทั้งหมดที่เกิดขึ้นใน VN ที่ระบุ พร้อมราคาและสถานะการจ่ายเงิน

```sql
SELECT
    o.item_no,
    o.icode,
    o.qty,
    o.unitprice,
    o.sum_price,
    o.income,
    i.name AS income_name,
    o.paid,
    o.rcpt_no,
    o.vstdate
FROM opitemrece o
LEFT JOIN income i ON o.income = i.income_id
WHERE o.vn = 'V20240001'
  AND o.paid != 'C'
  AND o.confirm = 'Y'
ORDER BY o.item_no;
```

**คำอธิบาย:**
- `LEFT JOIN income` เพื่อดึงชื่อประเภทรายได้
- `paid != 'C'` กรองรายการที่ถูกยกเลิกออก
- `confirm = 'Y'` แสดงเฉพาะรายการที่ยืนยันแล้ว

---

## 2. สรุปยอดค่าใช้จ่ายรวมต่อการมารับบริการ

คำนวณยอดรวมของแต่ละ VN แยกตามสถานะการจ่ายเงิน

```sql
SELECT
    o.vn,
    o.hn,
    SUM(CASE WHEN o.paid = 'N' THEN o.sum_price ELSE 0 END) AS unpaid_amount,
    SUM(CASE WHEN o.paid = 'Y' THEN o.sum_price ELSE 0 END) AS paid_amount,
    SUM(o.sum_price) AS total_amount,
    COUNT(*) AS item_count
FROM opitemrece o
WHERE o.vn = 'V20240001'
  AND o.paid != 'C'
  AND o.confirm = 'Y'
GROUP BY o.vn, o.hn;
```

**คำอธิบาย:**
- `unpaid_amount` — ยอดที่ยังไม่ได้จ่าย
- `paid_amount` — ยอดที่จ่ายแล้ว
- `total_amount` — ยอดรวมทั้งหมด

---

## 3. ดึงรายการที่ยังไม่ได้ชำระเงิน

แสดงรายการค่ารักษาที่ยังไม่มีการรับเงิน (unpaid bills)

```sql
SELECT
    o.vn,
    o.hn,
    p.fname,
    p.lname,
    o.icode,
    o.sum_price,
    o.income,
    o.vstdate,
    o.doctor
FROM opitemrece o
JOIN patient p ON o.hn = p.hn
WHERE o.paid = 'N'
  AND o.confirm = 'Y'
  AND o.vstdate >= '2024-01-01'
ORDER BY o.vstdate DESC
LIMIT 50;
```

**คำอธิบาย:**
- `paid = 'N'` เฉพาะรายการที่ยังไม่จ่าย
- `JOIN patient` เพื่อดึงชื่อผู้ป่วย
- กรองตามช่วงวันที่ที่ต้องการ

---

## 4. สรุปรายได้รายวัน

สรุปยอดรายได้แยกตามวันและประเภทรายได้

```sql
SELECT
    o.vstdate,
    o.income,
    i.name AS income_name,
    COUNT(*) AS transaction_count,
    SUM(o.sum_price) AS daily_total
FROM opitemrece o
LEFT JOIN income i ON o.income = i.income_id
WHERE o.vstdate BETWEEN '2024-01-01' AND '2024-01-31'
  AND o.paid = 'Y'
  AND o.confirm = 'Y'
GROUP BY o.vstdate, o.income, i.name
ORDER BY o.vstdate DESC, daily_total DESC;
```

**คำอธิบาย:**
- แยกรายงานตามวัน (`vstdate`) และประเภทรายได้ (`income`)
- `paid = 'Y'` นับเฉพาะรายการที่รับเงินแล้ว

---

## 5. สรุปรายได้รายวัน (แบบรวม)

สรุปยอดรายได้รวมต่อวัน ไม่แยกประเภท

```sql
SELECT
    vstdate,
    COUNT(DISTINCT vn) AS visit_count,
    COUNT(*) AS item_count,
    SUM(sum_price) AS total_revenue
FROM opitemrece
WHERE vstdate BETWEEN '2024-01-01' AND '2024-01-31'
  AND paid = 'Y'
  AND confirm = 'Y'
GROUP BY vstdate
ORDER BY vstdate DESC;
```

---

## 6. ดึงข้อมูลเงินมัดจำของผู้ป่วยใน

แสดงเงินมัดจำทั้งหมดของผู้ป่วยในรายหนึ่ง

```sql
SELECT
    fd.deposit_id,
    fd.an,
    fd.hn,
    fd.deposit_date,
    fd.amount,
    fd.used_amount,
    fd.remain_amount,
    fd.receive_type,
    fd.rcpt_no,
    fd.remark
FROM finance_deposit fd
WHERE fd.an = 'AN20240001'
  AND fd.cancel_date IS NULL
ORDER BY fd.deposit_date;
```

**คำอธิบาย:**
- `cancel_date IS NULL` กรองรายการที่ถูกยกเลิกออก
- แสดงยอดคงเหลือ (`remain_amount`) เพื่อติดตามสถานะเงินมัดจำ

---

## 7. สรุปเงินมัดจำคงเหลือต่อผู้ป่วยใน

```sql
SELECT
    fd.an,
    fd.hn,
    p.fname,
    p.lname,
    SUM(fd.amount) AS total_deposit,
    SUM(fd.used_amount) AS total_used,
    SUM(fd.remain_amount) AS total_remain
FROM finance_deposit fd
JOIN patient p ON fd.hn = p.hn
WHERE fd.cancel_date IS NULL
GROUP BY fd.an, fd.hn, p.fname, p.lname
HAVING total_remain != 0
ORDER BY total_remain DESC;
```

---

## 8. ดึงรายการค่าใช้จ่ายพร้อมชื่อผู้ป่วยและแพทย์

```sql
SELECT
    o.vn,
    o.hn,
    p.pname,
    p.fname,
    p.lname,
    o.icode,
    o.sum_price,
    o.income,
    i.name AS income_name,
    o.paid,
    o.rcpt_no,
    d.name AS doctor_name,
    o.vstdate
FROM opitemrece o
JOIN patient p ON o.hn = p.hn
LEFT JOIN income i ON o.income = i.income_id
LEFT JOIN doctor d ON o.doctor = d.code
WHERE o.vstdate = '2024-01-15'
  AND o.paid != 'C'
  AND o.confirm = 'Y'
ORDER BY o.vn, o.item_no
LIMIT 100;
```

---

## 9. ตรวจสอบรายการที่ออกใบเสร็จแล้ว

```sql
SELECT
    rcpt_no,
    vn,
    hn,
    COUNT(*) AS item_count,
    SUM(sum_price) AS receipt_total
FROM opitemrece
WHERE rcpt_no IS NOT NULL
  AND rcpt_no != ''
  AND vstdate = '2024-01-15'
GROUP BY rcpt_no, vn, hn
ORDER BY rcpt_no;
```

---

## 10. รายงานรายได้แยกตามสิทธิการรักษา

```sql
SELECT
    o.pttype,
    ptt.name AS pttype_name,
    COUNT(DISTINCT o.vn) AS visit_count,
    COUNT(*) AS item_count,
    SUM(o.sum_price) AS total_amount
FROM opitemrece o
LEFT JOIN pttype ptt ON o.pttype = ptt.pttype
WHERE o.vstdate BETWEEN '2024-01-01' AND '2024-01-31'
  AND o.paid = 'Y'
  AND o.confirm = 'Y'
GROUP BY o.pttype, ptt.name
ORDER BY total_amount DESC;
```

---

## ตัวอย่างการใช้งานกับ Vale

ถ้าคุณใช้ Vale สำหรับตรวจสอบเอกสาร Markdown คุณสามารถเพิ่มคอมเมนต์เพื่ออธิบายโค้ด SQL ได้:

```markdown
<!-- vale off -->
```sql
SELECT vn, SUM(sum_price) AS total
FROM opitemrece
WHERE paid = 'N'
GROUP BY vn;
```
<!-- vale on -->
```

การปิด Vale ชั่วคราว (`<!-- vale off -->`) จะช่วยให้โค้ด SQL ไม่ถูกตรวจสอบเรื่องภาษา ซึ่งเหมาะสมสำหรับโค้ดที่เป็นภาษาอังกฤษ

---

## เคล็ดลับการเขียน SQL สำหรับงานการเงิน

1. **Always use LIMIT** — ฐานข้อมูล HOSxP อาจมีข้อมูลหลายล้านรายการ
2. **ตรวจสอบ confirm = 'Y'** — กรองรายการที่ยังไม่ยืนยันออกเสมอ
3. **ตรวจสอบ paid != 'C'** — กรองรายการที่ถูกยกเลิกออก
4. **ใช้ JOIN กับตารางอ้างอิง** — เช่น `income`, `patient`, `doctor` เพื่อดึงชื่อที่อ่านง่าย
5. **ระวัง NULL** — ฟิลด์ `rcpt_no` อาจเป็น NULL ถ้ายังไม่มีการออกใบเสร็จ


---

## File: 05-finance/finance-deposit.md

# ตาราง finance_deposit — เงินมัดจำ

## ภาพรวม

`finance_deposit` เป็นตารางที่ใช้บันทึกข้อมูลเงินมัดจำของผู้ป่วยใน (IPD) ผู้ป่วยที่เข้ารับการรักษาในห้องผู้ป่วยในมักต้องชำระเงินมัดจำก่อนการรักษา และระบบจะบันทึกข้อมูลลงตารางนี้

ตารางนี้มีความสำคัญในการติดตามเงินมัดจำที่รับไว้ การใช้เงินมัดจำ และการคืนเงินมัดจำเมื่อผู้ป่วยออกจากโรงพยาบาล

---

## โครงสร้างตาราง (Column Details)

| คอลัมน์ | ประเภท | คำอธิบาย |
|---|---|---|
| `deposit_id` | INT | **รหัสอ้างอิงเงินมัดจำ** (Primary Key, Auto Increment) |
| `an` | VARCHAR | เลขที่ผู้ป่วยใน (Admission Number) — เชื่อมกับ `ipt.an` |
| `hn` | VARCHAR | เลขประจำตัวผู้ป่วย — เชื่อมกับ `patient.hn` |
| `deposit_date` | DATE | **วันที่รับเงินมัดจำ** |
| `deposit_time` | TIME | **เวลาที่รับเงินมัดจำ** |
| `amount` | DECIMAL | **จำนวนเงินมัดจำ** |
| `receive_type` | VARCHAR | ประเภทการรับเงิน (เงินสด/โอน/บัตรเครดิต) |
| `staff` | VARCHAR | รหัสผู้รับเงิน |
| `remark` | TEXT | หมายเหตุ |
| `cancel_date` | DATE | วันที่ยกเลิก (ถ้ามี) |
| `cancel_staff` | VARCHAR | รหัสผู้ยกเลิก |
| `cancel_remark` | TEXT | หมายเหตุการยกเลิก |
| `used_amount` | DECIMAL | จำนวนเงินที่ใช้ไปแล้ว |
| `remain_amount` | DECIMAL | จำนวนเงินคงเหลือ |
| `rcpt_no` | VARCHAR | เลขที่ใบเสร็จรับเงินมัดจำ |
| `old_rcpt_no` | VARCHAR | เลขที่ใบเสร็จเดิม (กรณีแก้ไข) |
| `last_modified` | DATETIME | เวลาที่แก้ไขล่าสุด |

---

## ฟิลด์สำคัญ

### 1. `amount` — จำนวนเงินมัดจำ
- จำนวนเงินที่ผู้ป่วยชำระเป็นเงินมัดจำ
- อาจมีหลายรายการต่อหนึ่ง AN (ถ้ามีการเติมเงินมัดจำ)

### 2. `used_amount` — จำนวนเงินที่ใช้ไปแล้ว
- ระบบจะอัปเดตเมื่อมีการนำเงินมัดจำไปหักกับค่าใช้จ่าย

### 3. `remain_amount` — จำนวนเงินคงเหลือ
- คำนวณจาก `amount - used_amount`
- ถ้าค่าเป็นลบ แสดงว่าผู้ป่วยมีค่าใช้จ่ายเกินเงินมัดจำ

### 4. `receive_type` — ประเภทการรับเงิน
| ค่าที่พบบ่อย | ความหมาย |
|---|---|
| 01 | เงินสด |
| 02 | โอนผ่านธนาคาร |
| 03 | บัตรเครดิต |
| 04 | เช็ค |

> หมายเหตุ: รหัส receive_type อาจแตกต่างกันตามการตั้งค่าของแต่ละโรงพยาบาล

---

## ตัวอย่างข้อมูล (Sample Data)

```sql
SELECT deposit_id, an, hn, deposit_date, amount, used_amount, remain_amount, receive_type, rcpt_no
FROM finance_deposit
WHERE an IS NOT NULL
ORDER BY deposit_date DESC
LIMIT 3;
```

ตัวอย่างผลลัพธ์:

| deposit_id | an | hn | deposit_date | amount | used_amount | remain_amount | receive_type | rcpt_no |
|---|---|---|---|---|---|---|---|---|
| 1001 | AN20240001 | HN0001 | 2024-01-10 | 5000.00 | 3500.00 | 1500.00 | 01 | R20240010 |
| 1002 | AN20240002 | HN0002 | 2024-01-11 | 10000.00 | 8000.00 | 2000.00 | 01 | R20240011 |
| 1003 | AN20240003 | HN0003 | 2024-01-12 | 3000.00 | 0.00 | 3000.00 | 02 | R20240012 |

---

## ข้อควรระวัง

1. **ตรวจสอบการยกเลิก** — ตรวจสอบ `cancel_date IS NULL` เพื่อกรองรายการที่ถูกยกเลิกออก
2. **ผู้ป่วยอาจมีหลายรายการมัดจำ** — ใช้ `GROUP BY an` และ `SUM(amount)` เมื่อต้องการยอดรวม
3. **เงินคงเหลือติดลบ** — ถ้า `remain_amount < 0` แสดงว่าผู้ป่วยต้องชำระเพิ่ม
4. **เชื่อมกับ ipt** — ใช้ `an` เชื่อมกับตาราง `ipt` เพื่อดูข้อมูลผู้ป่วยใน


---

## File: 05-finance/opitemrece-finance.md

# ตาราง opitemrece — รายการค่าใช้จ่ายต่อครั้งมา

## ภาพรวม

`opitemrece` เป็นตารางหลักที่เก็บรายการค่าใช้จ่ายทั้งหมดที่เกิดขึ้นในแต่ละครั้งที่ผู้ป่วยมารับบริการ ไม่ว่าจะเป็นยา ค่าบริการ ค่าตรวจ หรือค่าห้อง ทุกรายการจะถูกบันทึกลงตารางนี้

ตารางนี้เชื่อมโยงกับการเงินโดยตรง เพราะเป็นต้นทางของข้อมูลค่าใช้จ่ายที่ต้องนำมาคิดเงินและออกใบเสร็จ

---

## โครงสร้างตาราง (Column Details)

| คอลัมน์ | ประเภท | คำอธิบาย |
|---|---|---|
| `vn` | VARCHAR | เลขที่การมารับบริการ (Visit Number) — เชื่อมกับ `ovst.vn` |
| `hn` | VARCHAR | เลขประจำตัวผู้ป่วย (Hospital Number) — เชื่อมกับ `patient.hn` |
| `icode` | VARCHAR | รหัสรายการ (item code) — เชื่อมกับ `drugitems.icode` หรือตารางอื่น |
| `qty` | DECIMAL | จำนวน |
| `unitprice` | DECIMAL | ราคาต่อหน่วย |
| `sum_price` | DECIMAL | **ราคารวม** = qty * unitprice (ฟิลด์สำคัญสำหรับการเงิน) |
| `income` | VARCHAR | **รหัสประเภทรายได้** — เชื่อมกับ `income.income_id` |
| `paid` | CHAR(1) | **สถานะการจ่ายเงิน** — 'N'=ยังไม่จ่าย, 'Y'=จ่ายแล้ว, 'C'=ยกเลิก |
| `rcpt_no` | VARCHAR | **เลขที่ใบเสร็จรับเงิน** — อ้างอิงใบเสร็จที่รับเงิน |
| `item_no` | INT | ลำดับรายการในครั้งนั้น |
| `last_modified` | DATETIME | เวลาที่แก้ไขล่าสุด |
| `staff` | VARCHAR | รหัสผู้บันทึก |
| `confirm` | CHAR(1) | สถานะยืนยัน — 'N'=ยังไม่ยืนยัน, 'Y'=ยืนยันแล้ว |
| `drugusage` | VARCHAR | รหัสวิธีใช้ยา (ถ้าเป็นยา) |
| `sp_use` | CHAR(1) | สถานะการใช้สิทธิพิเศษ |
| `hcode` | VARCHAR | รหัสโรงพยาบาล |
| `vstdate` | DATE | วันที่มารับบริการ |
| `vsttime` | TIME | เวลาที่มารับบริการ |
| `doctor` | VARCHAR | รหัสแพทย์ผู้สั่ง |
| `rxdate` | DATE | วันที่สั่ง |
| `rxtime` | TIME | เวลาที่สั่ง |
| `an` | VARCHAR | เลขที่ผู้ป่วยใน (ถ้าเป็นผู้ป่วยใน) |
| `pttype` | VARCHAR | รหัสสิทธิการรักษา |
| `sub_type` | VARCHAR | รหัสประเภทย่อย |
| `oldcode` | VARCHAR | รหัสเก่า (ถ้ามี) |
| `charge_list_id` | INT | รหัสอ้างอิง charge list |
| `department_id` | INT | รหัสแผนก |

---

## ฟิลด์สำคัญสำหรับงานการเงิน

### 1. `sum_price` — ราคารวม
- คำนวณจาก `qty * unitprice`
- เป็นยอดเงินที่ต้องเรียกเก็บจากผู้ป่วยในแต่ละรายการ
- ใช้สำหรับสรุปยอดรายได้

### 2. `income` — รหัสประเภทรายได้
- แยกประเภทรายได้ตามหมวดหมู่ เช่น ยา ค่าบริการ ค่าตรวจ ค่าห้อง
- อ้างอิงตาราง `income`
- ใช้สำหรับรายงานสรุปรายได้ตามประเภท

### 3. `paid` — สถานะการจ่ายเงิน
| ค่า | ความหมาย |
|---|---|
| 'N' | ยังไม่ได้รับเงิน (ยังไม่จ่าย) |
| 'Y' | รับเงินแล้ว (จ่ายแล้ว) |
| 'C' | ยกเลิกรายการ |

### 4. `rcpt_no` — เลขที่ใบเสร็จ
- บันทึกเมื่อมีการรับเงินและออกใบเสร็จ
- ใช้อ้างอิงกลับไปหาใบเสร็จฉบับเต็ม
- ถ้าเป็น NULL แสดงว่ายังไม่มีการออกใบเสร็จ

---

## รหัสประเภทรายได้ (income codes)

ตาราง `income` เป็นตารางอ้างอิงที่แยกประเภทรายได้ ตัวอย่างรหัสที่พบบ่อย:

| รหัส income | ประเภทรายได้ |
|---|---|
| 01 | ค่ายา |
| 02 | ค่าบริการทางการแพทย์ |
| 03 | ค่าห้อง |
| 04 | ค่าตรวจทางห้องปฏิบัติการ |
| 05 | ค่าตรวจรังสี |
| 06 | ค่าอุปกรณ์ |
| 07 | ค่าอาหาร |
| 08 | ค่าอื่น ๆ |

> หมายเหตุ: รหัส income อาจแตกต่างกันตามการตั้งค่าของแต่ละโรงพยาบาล ควรตรวจสอบตาราง `income` ของแต่ละสถานที่

---

## ตัวอย่างข้อมูล (Sample Data)

```sql
SELECT vn, hn, icode, qty, unitprice, sum_price, income, paid, rcpt_no, vstdate
FROM opitemrece
WHERE vn IS NOT NULL
LIMIT 3;
```

ตัวอย่างผลลัพธ์:

| vn | hn | icode | qty | unitprice | sum_price | income | paid | rcpt_no | vstdate |
|---|---|---|---|---|---|---|---|---|---|
| V20240001 | HN0001 | IC0001 | 2 | 15.50 | 31.00 | 01 | N | NULL | 2024-01-15 |
| V20240001 | HN0001 | IC0002 | 1 | 250.00 | 250.00 | 02 | N | NULL | 2024-01-15 |
| V20240002 | HN0002 | IC0003 | 1 | 500.00 | 500.00 | 04 | Y | R20240001 | 2024-01-15 |

---

## ข้อควรระวัง

1. **รายการที่ยังไม่ยืนยัน** — ตรวจสอบ `confirm = 'Y'` เพื่อให้แน่ใจว่ารายการได้รับการยืนยันแล้ว
2. **รายการที่ยกเลิก** — ตรวจสอบ `paid != 'C'` เพื่อกรองรายการที่ถูกยกเลิกออก
3. **รายการผู้ป่วยใน** — ถ้ามีค่า `an` แสดงว่าเป็นรายการของผู้ป่วยใน อาจมีกระบวนการวางบิลที่ต่างจากผู้ป่วยนอก
4. **สิทธิการรักษา** — ฟิลด์ `pttype` มีผลต่อการคำนวณค่าใช้จ่ายที่ผู้ป่วยต้องจ่ายจริง


---

## File: 06-lab/common-queries.md

# ตัวอย่าง Query โมดูล Lab

## 1. ผล Lab ของ visit

```sql
SELECT 
    lh.lab_order_number,
    lh.order_date,
    li.lab_items_name,
    lo.lab_order_result,
    li.lab_items_normal_value,
    lo.lab_order_remark,
    CASE WHEN lo.abnormal_result = 'Y' THEN 'ผิดปกติ' ELSE 'ปกติ' END AS status
FROM lab_head lh
JOIN lab_order lo ON lh.lab_order_number = lo.lab_order_number
JOIN lab_items li ON lo.lab_items_code = li.lab_items_code
WHERE lh.vn = '2024010100001'
ORDER BY lh.order_date, li.display_order;
```

## 2. ใบสั่ง Lab ที่ยังไม่มีผล

```sql
SELECT 
    lh.lab_order_number,
    lh.hn,
    lh.order_date,
    lh.form_name,
    lh.item_count
FROM lab_head lh
WHERE lh.report_date IS NULL
  AND lh.order_date >= CURDATE() - INTERVAL 7 DAY
ORDER BY lh.order_date DESC;
```

## 3. ผล Lab ผิดปกติวันนี้

```sql
SELECT 
    lh.vn,
    lh.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    lh.order_date,
    li.lab_items_name,
    lo.lab_order_result,
    li.lab_items_normal_value
FROM lab_order lo
JOIN lab_head lh ON lo.lab_order_number = lh.lab_order_number
JOIN lab_items li ON lo.lab_items_code = li.lab_items_code
LEFT JOIN patient p ON lh.hn = p.hn
WHERE lo.abnormal_result = 'Y'
  AND lh.order_date = CURDATE()
ORDER BY lh.hn;
```

## 4. จำนวนการสั่ง Lab รายวัน

```sql
SELECT 
    order_date,
    COUNT(*) AS order_count,
    SUM(item_count) AS total_items
FROM lab_head
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY order_date
ORDER BY order_date;
```

## 5. ตัวอย่าง Vale Query

```vale
-- Vale: ผล Lab ของ visit
SELECT 
    li.lab_items_name,
    lo.lab_order_result,
    li.lab_items_normal_value,
    lo.lab_order_remark
FROM lab_head lh
JOIN lab_order lo ON lh.lab_order_number = lo.lab_order_number
JOIN lab_items li ON lo.lab_items_code = li.lab_items_code
WHERE lh.vn = @vn
ORDER BY li.display_order;
```

## เคล็ดลับ

- `report_date IS NULL` = ยังไม่มีผล
- `abnormal_result = 'Y'` = ผลผิดปกติ
- `critical_result = 'Y'` = ผลวิกฤต


---

## File: 06-lab/lab-head.md

# ตาราง `lab_head` - หัวใบสั่ง Lab

## คำอธิบาย

ตารางนี้เป็นตารางหลักของการสั่งตรวจ Lab ทุกครั้งที่มีการสั่งตรวจจะสร้าง record ใหม่ โดยมี `lab_order_number` เป็นรหัสประจำใบสั่งนั้นๆ

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `lab_order_number` | int | **PRI** | **เลขใบสั่ง Lab** |
| `hn` | varchar(9) | MUL | เลขประจำตัวผู้ป่วย |
| `vn` | varchar(13) | MUL | เลข VN (OPD) |
| `doctor_code` | varchar(7) | - | รหัสแพทย์สั่ง |
| `order_date` | date | MUL | **วันที่สั่ง** |
| `order_time` | time | - | เวลาที่สั่ง |
| `receive_date` | date | - | วันที่รับตัวอย่าง |
| `receive_time` | time | - | เวลารับตัวอย่าง |
| `report_date` | date | - | วันที่รายงานผล |
| `report_time` | time | - | เวลารายงานผล |
| `reporter_name` | varchar(100) | - | ผู้รายงานผล |
| `form_name` | varchar(200) | MUL | ชื่อฟอร์ม |
| `lab_items_group_code` | int | - | กลุ่มรายการ |
| `lab_head_remark` | varchar(250) | - | หมายเหตุ |
| `order_note` | text | - | บันทึกการสั่ง |
| `result_note` | text | - | บันทึกผล |
| `department` | varchar(5) | - | แผนก |
| `ward` | char(2) | - | Ward (ถ้าเป็นผู้ป่วยใน) |
| `confirm_specimen` | char(1) | MUL | ยืนยันตัวอย่าง |
| `confirm_report` | char(1) | - | ยืนยันรายงาน |
| `lock_result` | char(1) | - | ล็อกผล |
| `lab_receive` | char(1) | - | สถานะรับ |
| `abnormal_result` | char(1) | - | ผลผิดปกติ |
| `lab_perform_status_id` | int | - | สถานะดำเนินการ |
| `lab_priority_id` | int | - | ระดับความเร่งด่วน |
| `spclty` | char(2) | - | ความเชี่ยวชาญ |
| `finance_lock` | char(1) | - | ล็อกการเงิน |
| `report_lock` | char(1) | - | ล็อกรายงาน |
| `approve_staff` | varchar(25) | - | ผู้อนุมัติ |
| `order_staff` | varchar(25) | - | ผู้สั่ง |
| `receive_staff` | varchar(25) | - | ผู้รับ |
| `item_count` | int | - | จำนวนรายการ |
| `update_datetime` | datetime | - | วันเวลาปรับปรุง |

## ความสัมพันธ์

```sql
lab_head.hn → patient.hn                      (ผู้ป่วย)
lab_head.vn → ovst.vn                         (OPD)
lab_head.doctor_code → doctor.code            (แพทย์)
lab_head.lab_order_number → lab_order.lab_order_number (รายการตรวจ)
```

## ตัวอย่าง Query

```sql
-- ดูใบสั่ง Lab ของ visit
SELECT 
    lh.lab_order_number,
    lh.hn,
    lh.order_date,
    lh.order_time,
    d.name AS doctor_name,
    lh.form_name,
    lh.item_count
FROM lab_head lh
LEFT JOIN doctor d ON lh.doctor_code = d.code
WHERE lh.vn = '2024010100001';

-- ใบสั่ง Lab ที่ยังไม่มีผล
SELECT 
    lh.lab_order_number,
    lh.hn,
    lh.order_date,
    lh.form_name
FROM lab_head lh
WHERE lh.report_date IS NULL
  AND lh.order_date = CURDATE();
```

## หมายเหตุ

- `lab_order_number` เป็น running number ที่ไม่ซ้ำกัน
- `vn` จะมีค่าเมื่อสั่งจาก OPD
- `report_date IS NULL` หมายถึงยังไม่มีผล
- `abnormal_result = 'Y'` หมายถึงมีผลผิดปกติ


---

## File: 06-lab/lab-items.md

# ตาราง `lab_items` - รายการตรวจ Lab

## คำอธิบาย

ตารางนี้เก็บรายการตรวจ Lab ทั้งหมดในระบบ แต่ละรายการมีรหัส `lab_items_code` ที่ไม่ซ้ำกัน ใช้อ้างอิงใน `lab_order`

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `lab_items_code` | int | **PRI** | **รหัสรายการตรวจ** |
| `lab_items_name` | varchar(250) | MUL | **ชื่อรายการตรวจ** |
| `lab_items_unit` | varchar(150) | - | หน่วย |
| `lab_items_normal_value` | varchar(150) | - | ค่าปกติ |
| `lab_items_hint` | varchar(250) | - | คำแนะนำ |
| `lab_items_default_value` | varchar(250) | - | ค่าเริ่มต้น |
| `service_price` | double | - | ราคา |
| `service_price_ipd` | double | - | ราคาผู้ป่วยใน |
| `lab_items_group` | int | - | กลุ่ม |
| `lab_items_sub_group_code` | int | - | กลุ่มย่อย |
| `require_specimen` | char(1) | - | ต้องการตัวอย่าง |
| `specimen_code` | int | - | รหัสตัวอย่าง |
| `wait_hour` | int | - | ระยะเวลารอผล (ชั่วโมง) |
| `critical_value` | varchar(100) | - | ค่าวิกฤต |
| `display_order` | int | - | ลำดับการแสดง |
| `icode` | varchar(7) | - | รหัสเชื่อม drugitems |
| `range_check` | char(1) | - | ตรวจสอบช่วง |
| `range_check_min` | double | - | ค่าต่ำสุด (ชาย) |
| `range_check_max` | double | - | ค่าสูงสุด (ชาย) |
| `range_check_min_female` | double | - | ค่าต่ำสุด (หญิง) |
| `range_check_max_female` | double | - | ค่าสูงสุด (หญิง) |
| `result_type` | int | - | ประเภทผล |
| `possible_value` | text | - | ค่าที่เป็นไปได้ |
| `active_status` | varchar(1) | - | สถานะใช้งาน |
| `loinc_code` | varchar(15) | MUL | รหัส LOINC |
| `oldcode` | varchar(150) | MUL | รหัสเก่า |
| `update_datetime` | datetime | - | วันเวลาปรับปรุง |

## ความสัมพันธ์

```sql
lab_items.lab_items_code → lab_order.lab_items_code
lab_items.icode → drugitems.icode          (ถ้าเชื่อมกับยา)
lab_items.specimen_code → lab_specimen.specimen_code
```

## ตัวอย่าง Query

```sql
-- ค้นหารายการตรวจ
SELECT lab_items_code, lab_items_name, lab_items_unit, service_price
FROM lab_items
WHERE lab_items_name LIKE '%glucose%'
  AND active_status = 'Y';

-- รายการตรวจตามกลุ่ม
SELECT 
    li.lab_items_code,
    li.lab_items_name,
    li.lab_items_unit,
    li.lab_items_normal_value,
    li.service_price
FROM lab_items li
WHERE li.lab_items_group = 1
  AND li.active_status = 'Y'
ORDER BY li.display_order;
```

## หมายเหตุ

- `lab_items_code` เป็น running number
- `active_status = 'Y'` คือรายการที่ยังใช้งานอยู่
- `loinc_code` เป็นมาตรฐานสากลสำหรับรายการตรวจ Lab
- ช่วงค่าปกติแยกตามเพศ: `_male` และ `_female`


---

## File: 06-lab/lab-order.md

# ตาราง `lab_order` - รายการตรวจและผล Lab

## คำอธิบาย

ตารางนี้เก็บรายละเอียดแต่ละรายการตรวจในใบสั่ง Lab หนึ่งใบสั่ง (`lab_head`) อาจมีหลายรายการตรวจ (`lab_order`) แต่ละรายการมีผลตรวจอยู่ใน `lab_order_result`

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `lab_order_number` | int | **PRI** | เลขใบสั่ง Lab (เชื่อม `lab_head`) |
| `lab_items_code` | int | **PRI** | รหัสรายการตรวจ (เชื่อม `lab_items`) |
| `lab_order_result` | varchar(250) | - | **ผลตรวจ** |
| `lab_order_remark` | varchar(250) | - | หมายเหตุ |
| `staff` | varchar(50) | - | ผู้บันทึกผล |
| `confirm` | char(1) | - | ยืนยันผล |
| `lab_items_name_ref` | varchar(250) | - | ชื่อรายการอ้างอิง |
| `lab_items_normal_value_ref` | varchar(150) | - | ค่าปกติอ้างอิง |
| `specimen_code` | int | - | รหัสตัวอย่าง |
| `lab_items_sub_group_code` | int | - | กลุ่มย่อย |
| `order_type` | char(1) | - | ประเภทการสั่ง |
| `item_cost` | double | - | ต้นทุน |
| `laborder_date` | date | MUL | วันที่ |
| `abnormal_result` | char(1) | - | ผลผิดปกติ |
| `lab_result_status` | int | - | สถานะผล |
| `critical_result` | char(1) | - | ผลวิกฤต |
| `printed` | char(1) | - | พิมพ์แล้ว |
| `update_datetime` | datetime | - | วันเวลาปรับปรุง |

## ความสัมพันธ์

```sql
lab_order.lab_order_number → lab_head.lab_order_number
lab_order.lab_items_code → lab_items.lab_items_code
```

## ตัวอย่าง Query

```sql
-- ดูผล Lab ของใบสั่ง
SELECT 
    lo.lab_order_number,
    lo.lab_items_code,
    li.lab_items_name,
    lo.lab_order_result,
    li.lab_items_normal_value,
    lo.lab_order_remark,
    lo.abnormal_result,
    lo.critical_result
FROM lab_order lo
LEFT JOIN lab_items li ON lo.lab_items_code = li.lab_items_code
WHERE lo.lab_order_number = 12345
ORDER BY li.display_order;

-- ผล Lab ที่ผิดปกติ
SELECT 
    lh.vn,
    lh.hn,
    lh.order_date,
    li.lab_items_name,
    lo.lab_order_result,
    li.lab_items_normal_value
FROM lab_order lo
JOIN lab_head lh ON lo.lab_order_number = lh.lab_order_number
JOIN lab_items li ON lo.lab_items_code = li.lab_items_code
WHERE lo.abnormal_result = 'Y'
  AND lh.order_date = CURDATE();
```

## หมายเหตุ

- Primary key เป็น composite: (`lab_order_number`, `lab_items_code`)
- `lab_order_result` เก็บผลตรวจในรูปข้อความ
- `abnormal_result = 'Y'` แสดงว่าผลอยู่นอกช่วงค่าปกติ
- `critical_result = 'Y'` แสดงว่าเป็นผลวิกฤตที่ต้องแจ้งด่วน


---

## File: relationships/opitemrece-overview.md

# ตารางเชื่อมโยงหลัก: `opitemrece`

## ทำไม `opitemrece` ถึงสำคัญ

`opitemrece` เป็นตารางกลางที่เชื่อมโยง OPD, IPD, Drug, และ Finance เข้าด้วยกัน เกือบทุกรายการค่าใช้จ่ายในโรงพยาบาลจะผ่านตารางนี้

## โครงสร้างการเชื่อมโยง

```
┌────────────────────────────────────────────────────┐
│                  opitemrece                         │
├────────────────────────────────────────────────────┤
│  vn → ovst.vn     (OPD visit)                      │
│  an → ipt.an      (IPD admit)                      │
│  hn → patient.hn  (ผู้ป่วย)                         │
│  icode → drugitems.icode  (ยา)                     │
│  icode → nondrugitems.icode (เวชภัณฑ์/บริการ)      │
│  income → income.income   (ประเภทรายได้)           │
│  doctor → doctor.code     (แพทย์)                  │
└────────────────────────────────────────────────────┘
```

## การแยก OPD/IPD

```sql
-- OPD ใช้ vn
SELECT * FROM opitemrece WHERE vn IS NOT NULL AND vn != '';

-- IPD ใช้ an
SELECT * FROM opitemrece WHERE an IS NOT NULL AND an != '';

-- บางรายการอาจไม่มีทั้ง vn และ an (เช่น ค่าบริการทั่วไป)
```

## การแยกประเภทรายการ

```sql
-- ยา
SELECT * FROM opitemrece WHERE item_type = '1';

-- บริการ
SELECT * FROM opitemrece WHERE item_type = '2';

-- Lab
SELECT * FROM opitemrece WHERE item_type = '3';

-- X-Ray
SELECT * FROM opitemrece WHERE item_type = '4';
```

## ตัวอย่าง Query ที่ใช้บ่อย

```sql
-- ค่าใช้จ่ายรวมของ visit
SELECT 
    o.vn,
    SUM(o.sum_price) AS total_amount
FROM opitemrece o
WHERE o.vn = '2024010100001'
GROUP BY o.vn;

-- ค่าใช้จ่ายรวมของการ Admit
SELECT 
    o.an,
    SUM(o.sum_price) AS total_amount
FROM opitemrece o
WHERE o.an = '650000001'
GROUP BY o.an;

-- ค่าใช้จ่ายแยกตามประเภทรายได้
SELECT 
    o.income,
    i.name AS income_name,
    COUNT(*) AS item_count,
    SUM(o.sum_price) AS total_amount
FROM opitemrece o
LEFT JOIN income i ON o.income = i.income
WHERE o.vn = '2024010100001'
GROUP BY o.income
ORDER BY total_amount DESC;

-- ยาที่ใช้ใน visit
SELECT 
    o.icode,
    d.name AS drug_name,
    o.qty,
    o.sum_price
FROM opitemrece o
LEFT JOIN drugitems d ON o.icode = d.icode
WHERE o.vn = '2024010100001'
  AND o.item_type = '1';
```

## หมายเหตุ

- `sum_price` = `qty` * `unitprice` (โดยปกติ)
- `item_type` บ่งบอกประเภทรายการ
- `income` บ่งบอกรหัสรายได้
- `sub_type` บ่งบอกประเภทย่อย
- ใช้ `vn` หรือ `an` ร่วมกันเพื่อแยก OPD/IPD


---

## File: relationships/patient-opd-ipd.md

# ความสัมพันธ์ Patient → OPD → IPD

## โครงสร้างหลัก

```
patient (hn)
    ├──→ ovst (vn) ──→ opdscreen (vn)
    │                  ├──→ ovstdiag (vn)
    │                  ├──→ opitemrece (vn)
    │                  └──→ lab_head (vn)
    │
    └──→ ipt (an) ───→ iptdiag (an)
                       ├──→ iptbedmove (an)
                       ├──→ iptdrugorder (an)
                       └──→ opitemrece (an)
```

## ความสัมพันธ์ละเอียด

### Patient → OPD

| ตารางต้นทาง | คอลัมน์ | ตารางปลายทาง | คอลัมน์ | ความหมาย |
|-----------|--------|------------|--------|---------|
| patient | hn | ovst | hn | ผู้ป่วย → การ visit |
| ovst | vn | opdscreen | vn | visit → คัดกรอง |
| ovst | vn | ovstdiag | vn | visit → วินิจฉัย |
| ovst | vn | opitemrece | vn | visit → สั่งยา/ค่ารักษา |
| ovst | vn | lab_head | vn | visit → สั่ง Lab |
| ovst | doctor | doctor | code | visit → แพทย์ |
| ovst | pttype | pttype | pttype | visit → สิทธิ |
| ovst | spclty | spclty | spclty | visit → แผนก |

### Patient → IPD

| ตารางต้นทาง | คอลัมน์ | ตารางปลายทาง | คอลัมน์ | ความหมาย |
|-----------|--------|------------|--------|---------|
| patient | hn | ipt | hn | ผู้ป่วย → การ Admit |
| ipt | an | iptdiag | an | Admit → วินิจฉัย |
| ipt | an | iptbedmove | an | Admit → ย้ายเตียง |
| ipt | an | iptdrugorder | an | Admit → สั่งยา |
| ipt | an | opitemrece | an | Admit → ค่ารักษา |
| ipt | ward | ward | ward | Admit → Ward |
| ipt | admdoctor | doctor | code | Admit → แพทย์ |

### OPD → IPD (เชื่อมกัน)

| ตารางต้นทาง | คอลัมน์ | ตารางปลายทาง | คอลัมน์ | ความหมาย |
|-----------|--------|------------|--------|---------|
| ovst | vn | ipt | vn | OPD visit → Admit |
| ovst | an | ipt | an | OPD → IPD (ผ่าน ovst.an) |

## ตัวอย่าง Query ข้ามตาราง

```sql
-- ดูประวัติการรักษาทั้งหมดของผู้ป่วย (OPD + IPD)
SELECT 
    p.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    'OPD' AS type,
    o.vn AS ref_no,
    o.vstdate AS date,
    o.vsttime AS time,
    d.name AS doctor_name
FROM patient p
LEFT JOIN ovst o ON p.hn = o.hn
LEFT JOIN doctor d ON o.doctor = d.code
WHERE p.hn = '000000001'

UNION ALL

SELECT 
    p.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    'IPD' AS type,
    i.an AS ref_no,
    i.regdate AS date,
    i.regtime AS time,
    d.name AS doctor_name
FROM patient p
LEFT JOIN ipt i ON p.hn = i.hn
LEFT JOIN doctor d ON i.admdoctor = d.code
WHERE p.hn = '000000001'

ORDER BY date DESC;
```


