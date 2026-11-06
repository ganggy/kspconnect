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
