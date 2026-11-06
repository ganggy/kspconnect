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
