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
