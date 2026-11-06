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
