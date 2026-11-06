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
