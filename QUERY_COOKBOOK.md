# HOSxP Query Cookbook (คู่มือคิวรีระบบสารสนเทศโรงพยาบาล)

> คลังรวมตัวอย่าง SQL Query จริงที่ใช้งานในโรงพยาบาล (HOSxP Database) สำหรับให้ AI นำไปปรับใช้ตอบคำถามผู้ใช้ได้ทันที

---

## 1. ข้อมูลผู้ป่วยนอก (OPD)

### 1.1 จำนวนผู้ป่วยนอกมารับบริการวันนี้
```sql
SELECT COUNT(DISTINCT vn) AS total_opd_visits, COUNT(DISTINCT hn) AS total_patients
FROM ovst 
WHERE vstdate = CURDATE();
```

### 1.2 สถิติผู้ป่วยนอกแยกตามแผนก/คลินิก (วันนี้)
```sql
SELECT 
    c.clinic, 
    c.name AS clinic_name, 
    COUNT(o.vn) AS visit_count
FROM ovst o
LEFT JOIN clinic c ON o.cur_dep = c.clinic
WHERE o.vstdate = CURDATE()
GROUP BY c.clinic, c.name
ORDER BY visit_count DESC;
```

### 1.3 10 อันดับโรคยอดนิยมผู้ป่วยนอก (Primary Diagnosis)
```sql
SELECT 
    d.icd10, 
    i.name AS diag_name, 
    COUNT(d.vn) AS total_cases
FROM ovstdiag d
LEFT JOIN icd101 i ON d.icd10 = i.code
WHERE d.vstdate BETWEEN DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND CURDATE()
  AND d.diagtype = '1'
GROUP BY d.icd10, i.name
ORDER BY total_cases DESC
LIMIT 10;
```

---

## 2. ข้อมูลผู้ป่วยใน (IPD)

### 2.1 ผู้ป่วยในที่นอนพักรักษาตัวอยู่ปัจจุบัน (Active Inpatients)
```sql
SELECT 
    i.an, 
    i.hn, 
    i.regdate, 
    i.regtime, 
    w.name AS ward_name, 
    it.bedno,
    TIMESTAMPDIFF(DAY, i.regdate, CURDATE()) AS admitted_days
FROM ipt i
LEFT JOIN ward w ON i.ward = w.ward
LEFT JOIN iptadm it ON i.an = it.an
WHERE i.dchdate IS NULL
ORDER BY i.ward, i.regdate ASC;
```

### 2.2 อัตราการครองเตียงแยกตามตึก/วอร์ด (Bed Occupancy by Ward)
```sql
SELECT 
    w.ward, 
    w.name AS ward_name, 
    COUNT(i.an) AS current_admitted_patients
FROM ward w
LEFT JOIN ipt i ON w.ward = i.ward AND i.dchdate IS NULL
WHERE w.ward_active = 'Y'
GROUP BY w.ward, w.name
ORDER BY current_admitted_patients DESC;
```

---

## 3. ข้อมูลยาและเวชภัณฑ์ (Drug & Pharmacy)

### 3.1 ค้นหารายการยาและราคาในคลัง
```sql
SELECT 
    icode, 
    name AS trade_name, 
    generic_name, 
    strength, 
    units, 
    unitprice, 
    istatus
FROM drugitems
WHERE name LIKE '%paracetamol%' OR generic_name LIKE '%paracetamol%'
ORDER BY name ASC;
```

### 3.2 รายการยาที่ใช้บ่อยที่สุดประจำเดือน
```sql
SELECT 
    o.icode, 
    d.name AS drug_name, 
    d.strength, 
    SUM(o.qty) AS total_qty, 
    SUM(o.sum_price) AS total_amount
FROM opitemrece o
JOIN drugitems d ON o.icode = d.icode
WHERE o.vstdate BETWEEN DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND CURDATE()
GROUP BY o.icode, d.name, d.strength
ORDER BY total_qty DESC
LIMIT 20;
```

---

## 4. ห้องปฏิบัติการ (Laboratory)

### 4.1 ค้นหารายการสั่งตรวจ Lab วันนี้
```sql
SELECT 
    lh.lab_order_number, 
    lh.hn, 
    lh.order_date, 
    lh.order_time, 
    lh.department, 
    lh.form_name
FROM lab_head lh
WHERE lh.order_date = CURDATE()
ORDER BY lh.order_time DESC
LIMIT 50;
```

### 4.2 ผลตรวจ Lab รายบุคคล (เชื่อมโยง lab_head และ lab_order)
```sql
SELECT 
    lo.lab_items_code, 
    li.lab_items_name, 
    lo.lab_order_result, 
    li.lab_items_unit, 
    li.lab_items_normal_value, 
    lh.order_date
FROM lab_order lo
JOIN lab_head lh ON lo.lab_order_number = lh.lab_order_number
JOIN lab_items li ON lo.lab_items_code = li.lab_items_code
WHERE lh.hn = '000000001'
ORDER BY lh.order_date DESC, lo.lab_items_code ASC
LIMIT 50;
```

---

## 5. การเงินและค่ารักษาพยาบาล (Finance & opitemrece)

### 5.1 ยอดรวมค่าใช้จ่ายแยกตามหมวดหมู่รายได้
```sql
SELECT 
    o.income, 
    inc.name AS income_name, 
    SUM(o.sum_price) AS total_income
FROM opitemrece o
LEFT JOIN income inc ON o.income = inc.income
WHERE o.vstdate = CURDATE()
GROUP BY o.income, inc.name
ORDER BY total_income DESC;
```

---

## 6. กฎสำคัญสำหรับ AI เมื่อเขียนคิวรี HOSxP
1. **หลีกเลี่ยงการทำ `SELECT *`** จากตารางขนาดใหญ่ เช่น `opitemrece`, `ovst`, `patient` เพราะมีข้อมูลหลักแสน/ล้านเรคอร์ด
2. **ต้องระบุช่วงวันที่เสมอ (`vstdate` หรือ `regdate`)** เพื่อใช้ Index ของฐานข้อมูล
3. **Primary Key ที่ต้องจำ:**
   - ผู้ป่วย: `hn` (`patient.hn`)
   - ผู้ป่วยนอก: `vn` (`ovst.vn`)
   - ผู้ป่วยใน: `an` (`ipt.an`)
   - รหัสยา/รายการ: `icode` (`drugitems.icode`, `opitemrece.icode`)
   - ใบสั่งแล็บ: `lab_order_number` (`lab_head.lab_order_number`)
