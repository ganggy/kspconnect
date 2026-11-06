# โมดูลห้องปฏิบัติการ (Lab Module)

## ภาพรวม

โมดูลนี้เก็บข้อมูลการสั่งตรวจห้องปฏิบัติการ (Laboratory) ผลตรวจ และรายการตรวจทั้งหมด เป็นส่วนสำคัญในการวินิจฉัยและติดตามการรักษา

## กระบวนการทำงาน (Workflow)

```
แพทย์/พยาบาลสั่งตรวจ Lab
    ↓
สร้าง record ใน lab_head (ได้ lab_order_number)
    ↓
สร้างรายการตรวจใน lab_order (เชื่อมกับ lab_items)
    ↓
เจ้าหน้าที่ Lab รับตัวอย่าง → บันทึกผล
    ↓
บันทึกผลใน lab_order.lab_order_result
    ↓
แพทย์ดูผล/อนุมัติ
```

## ตารางหลักในโมดูลนี้

| ตาราง | คำอธิบาย | ความสำคัญ |
|-------|---------|----------|
| `lab_head` | หัวใบสั่ง Lab | ⭐⭐⭐ |
| `lab_order` | รายการตรวจและผล | ⭐⭐⭐ |
| `lab_items` | รายการตรวจทั้งหมด | ⭐⭐⭐ |
| `lab_items_group` | กลุ่มรายการตรวจ | ⭐⭐ |
| `lab_specimen` | ประเภทตัวอย่าง | ⭐⭐ |
| `lab_department` | แผนก Lab | ⭐⭐ |

## Key Identifiers

- **lab_order_number** - รหัสใบสั่ง Lab อยู่ใน `lab_head.lab_order_number`
- **lab_items_code** - รหัสรายการตรวจ อยู่ใน `lab_items.lab_items_code`
- **vn** - เชื่อมกับ OPD (ถ้ามี)
- **hn** - เชื่อมกับผู้ป่วย

## ความสัมพันธ์เบื้องต้น

```
lab_head (lab_order_number)
    ├──→ ovst (vn)                  [OPD]
    ├──→ patient (hn)               [ผู้ป่วย]
    ├──→ lab_order (lab_order_number) [รายการตรวจ]
    └──→ doctor (doctor_code)       [แพทย์]

lab_order (lab_order_number, lab_items_code)
    ├──→ lab_head (lab_order_number)
    └──→ lab_items (lab_items_code)  [รายละเอียดตรวจ]
```

## ลิงก์ไปยังเอกสารอื่น

- [ตาราง lab_head](lab-head.md)
- [ตาราง lab_order](lab-order.md)
- [ตาราง lab_items](lab-items.md)
- [ตัวอย่าง Query](common-queries.md)
