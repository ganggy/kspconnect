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
