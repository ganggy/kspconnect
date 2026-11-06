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
