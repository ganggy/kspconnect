# โมดูลเภสัช (Drug Module)

## ภาพรวม

โมดูลนี้เก็บข้อมูลเกี่ยวกับยา การสั่งยา การจ่ายยา และสต็อกยา เป็นส่วนสำคัญของระบบ HOSxP ที่เชื่อมโยงกับทั้งผู้ป่วยนอก (OPD) และผู้ป่วยใน (IPD)

## กระบวนการทำงาน (Workflow)

```
แพทย์สั่งยา
    ↓
บันทึกใน opitemrece (icode, qty, drugusage)
    ↓
เภสัชกรตรวจสอบ → จัดยา
    ↓
จ่ายยาให้ผู้ป่วย / ส่งยาขึ้น Ward
```

## ตารางหลักในโมดูลนี้

| ตาราง | คำอธิบาย | ความสำคัญ |
|-------|---------|----------|
| `drugitems` | ข้อมูลยาหลัก | ⭐⭐⭐ |
| `opitemrece` | ใบสั่งยา/ค่ารักษา (ทั้ง OPD และ IPD) | ⭐⭐⭐ |
| `drugstock` | สต็อกยา | ⭐⭐⭐ |
| `drugusage` | วิธีใช้ยา | ⭐⭐ |
| `drugunits` | หน่วยยา | ⭐⭐ |

## Key Identifiers

- **icode** - รหัสยา อยู่ใน `drugitems.icode` เชื่อมกับ `opitemrece.icode`
- **vn** - ใช้สำหรับ OPD (opitemrece.vn)
- **an** - ใช้สำหรับ IPD (opitemrece.an)
- **drugusage** - รหัสวิธีใช้ยา

## ความสัมพันธ์เบื้องต้น

```
drugitems (icode)
    └──→ opitemrece (icode)    [สั่งยา]

ovst (vn)
    └──→ opitemrece (vn)       [สั่งยา OPD]

ipt (an)
    └──→ opitemrece (an)       [สั่งยา IPD]

opitemrece (drugusage)
    └──→ drugusage (code)      [วิธีใช้ยา]
```

## หมายเหตุสำคัญ

- `opitemrece` ไม่ใช่แค่ตารางยา แต่เป็นตารางค่ารักษาทั้งหมด (ยา, lab, x-ray, ค่าห้อง, ค่าอาหาร)
- `opitemrece.item_type` บ่งบอกว่าเป็นรายการประเภทไหน
- `opitemrece.income` บ่งบอกรหัสรายได้

## ลิงก์ไปยังเอกสารอื่น

- [ตาราง drugitems](drugitems.md)
- [ตาราง opitemrece](opitemrece.md)
- [ตัวอย่าง Query](common-queries.md)
