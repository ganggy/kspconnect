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
