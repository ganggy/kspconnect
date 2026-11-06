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
