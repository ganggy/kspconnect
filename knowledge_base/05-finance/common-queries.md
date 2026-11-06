# คำสั่ง SQL ที่ใช้บ่อยในงานการเงิน

เอกสารนี้รวบรวมคำสั่ง SQL ที่ใช้บ่อยในงานด้านการเงินของ HOSxP พร้อมคำอธิบายเป็นภาษาไทย

---

## 1. ดึงรายการค่าใช้จ่ายของการมารับบริการหนึ่งครั้ง

ดึงรายการทั้งหมดที่เกิดขึ้นใน VN ที่ระบุ พร้อมราคาและสถานะการจ่ายเงิน

```sql
SELECT
    o.item_no,
    o.icode,
    o.qty,
    o.unitprice,
    o.sum_price,
    o.income,
    i.name AS income_name,
    o.paid,
    o.rcpt_no,
    o.vstdate
FROM opitemrece o
LEFT JOIN income i ON o.income = i.income_id
WHERE o.vn = 'V20240001'
  AND o.paid != 'C'
  AND o.confirm = 'Y'
ORDER BY o.item_no;
```

**คำอธิบาย:**
- `LEFT JOIN income` เพื่อดึงชื่อประเภทรายได้
- `paid != 'C'` กรองรายการที่ถูกยกเลิกออก
- `confirm = 'Y'` แสดงเฉพาะรายการที่ยืนยันแล้ว

---

## 2. สรุปยอดค่าใช้จ่ายรวมต่อการมารับบริการ

คำนวณยอดรวมของแต่ละ VN แยกตามสถานะการจ่ายเงิน

```sql
SELECT
    o.vn,
    o.hn,
    SUM(CASE WHEN o.paid = 'N' THEN o.sum_price ELSE 0 END) AS unpaid_amount,
    SUM(CASE WHEN o.paid = 'Y' THEN o.sum_price ELSE 0 END) AS paid_amount,
    SUM(o.sum_price) AS total_amount,
    COUNT(*) AS item_count
FROM opitemrece o
WHERE o.vn = 'V20240001'
  AND o.paid != 'C'
  AND o.confirm = 'Y'
GROUP BY o.vn, o.hn;
```

**คำอธิบาย:**
- `unpaid_amount` — ยอดที่ยังไม่ได้จ่าย
- `paid_amount` — ยอดที่จ่ายแล้ว
- `total_amount` — ยอดรวมทั้งหมด

---

## 3. ดึงรายการที่ยังไม่ได้ชำระเงิน

แสดงรายการค่ารักษาที่ยังไม่มีการรับเงิน (unpaid bills)

```sql
SELECT
    o.vn,
    o.hn,
    p.fname,
    p.lname,
    o.icode,
    o.sum_price,
    o.income,
    o.vstdate,
    o.doctor
FROM opitemrece o
JOIN patient p ON o.hn = p.hn
WHERE o.paid = 'N'
  AND o.confirm = 'Y'
  AND o.vstdate >= '2024-01-01'
ORDER BY o.vstdate DESC
LIMIT 50;
```

**คำอธิบาย:**
- `paid = 'N'` เฉพาะรายการที่ยังไม่จ่าย
- `JOIN patient` เพื่อดึงชื่อผู้ป่วย
- กรองตามช่วงวันที่ที่ต้องการ

---

## 4. สรุปรายได้รายวัน

สรุปยอดรายได้แยกตามวันและประเภทรายได้

```sql
SELECT
    o.vstdate,
    o.income,
    i.name AS income_name,
    COUNT(*) AS transaction_count,
    SUM(o.sum_price) AS daily_total
FROM opitemrece o
LEFT JOIN income i ON o.income = i.income_id
WHERE o.vstdate BETWEEN '2024-01-01' AND '2024-01-31'
  AND o.paid = 'Y'
  AND o.confirm = 'Y'
GROUP BY o.vstdate, o.income, i.name
ORDER BY o.vstdate DESC, daily_total DESC;
```

**คำอธิบาย:**
- แยกรายงานตามวัน (`vstdate`) และประเภทรายได้ (`income`)
- `paid = 'Y'` นับเฉพาะรายการที่รับเงินแล้ว

---

## 5. สรุปรายได้รายวัน (แบบรวม)

สรุปยอดรายได้รวมต่อวัน ไม่แยกประเภท

```sql
SELECT
    vstdate,
    COUNT(DISTINCT vn) AS visit_count,
    COUNT(*) AS item_count,
    SUM(sum_price) AS total_revenue
FROM opitemrece
WHERE vstdate BETWEEN '2024-01-01' AND '2024-01-31'
  AND paid = 'Y'
  AND confirm = 'Y'
GROUP BY vstdate
ORDER BY vstdate DESC;
```

---

## 6. ดึงข้อมูลเงินมัดจำของผู้ป่วยใน

แสดงเงินมัดจำทั้งหมดของผู้ป่วยในรายหนึ่ง

```sql
SELECT
    fd.deposit_id,
    fd.an,
    fd.hn,
    fd.deposit_date,
    fd.amount,
    fd.used_amount,
    fd.remain_amount,
    fd.receive_type,
    fd.rcpt_no,
    fd.remark
FROM finance_deposit fd
WHERE fd.an = 'AN20240001'
  AND fd.cancel_date IS NULL
ORDER BY fd.deposit_date;
```

**คำอธิบาย:**
- `cancel_date IS NULL` กรองรายการที่ถูกยกเลิกออก
- แสดงยอดคงเหลือ (`remain_amount`) เพื่อติดตามสถานะเงินมัดจำ

---

## 7. สรุปเงินมัดจำคงเหลือต่อผู้ป่วยใน

```sql
SELECT
    fd.an,
    fd.hn,
    p.fname,
    p.lname,
    SUM(fd.amount) AS total_deposit,
    SUM(fd.used_amount) AS total_used,
    SUM(fd.remain_amount) AS total_remain
FROM finance_deposit fd
JOIN patient p ON fd.hn = p.hn
WHERE fd.cancel_date IS NULL
GROUP BY fd.an, fd.hn, p.fname, p.lname
HAVING total_remain != 0
ORDER BY total_remain DESC;
```

---

## 8. ดึงรายการค่าใช้จ่ายพร้อมชื่อผู้ป่วยและแพทย์

```sql
SELECT
    o.vn,
    o.hn,
    p.pname,
    p.fname,
    p.lname,
    o.icode,
    o.sum_price,
    o.income,
    i.name AS income_name,
    o.paid,
    o.rcpt_no,
    d.name AS doctor_name,
    o.vstdate
FROM opitemrece o
JOIN patient p ON o.hn = p.hn
LEFT JOIN income i ON o.income = i.income_id
LEFT JOIN doctor d ON o.doctor = d.code
WHERE o.vstdate = '2024-01-15'
  AND o.paid != 'C'
  AND o.confirm = 'Y'
ORDER BY o.vn, o.item_no
LIMIT 100;
```

---

## 9. ตรวจสอบรายการที่ออกใบเสร็จแล้ว

```sql
SELECT
    rcpt_no,
    vn,
    hn,
    COUNT(*) AS item_count,
    SUM(sum_price) AS receipt_total
FROM opitemrece
WHERE rcpt_no IS NOT NULL
  AND rcpt_no != ''
  AND vstdate = '2024-01-15'
GROUP BY rcpt_no, vn, hn
ORDER BY rcpt_no;
```

---

## 10. รายงานรายได้แยกตามสิทธิการรักษา

```sql
SELECT
    o.pttype,
    ptt.name AS pttype_name,
    COUNT(DISTINCT o.vn) AS visit_count,
    COUNT(*) AS item_count,
    SUM(o.sum_price) AS total_amount
FROM opitemrece o
LEFT JOIN pttype ptt ON o.pttype = ptt.pttype
WHERE o.vstdate BETWEEN '2024-01-01' AND '2024-01-31'
  AND o.paid = 'Y'
  AND o.confirm = 'Y'
GROUP BY o.pttype, ptt.name
ORDER BY total_amount DESC;
```

---

## ตัวอย่างการใช้งานกับ Vale

ถ้าคุณใช้ Vale สำหรับตรวจสอบเอกสาร Markdown คุณสามารถเพิ่มคอมเมนต์เพื่ออธิบายโค้ด SQL ได้:

```markdown
<!-- vale off -->
```sql
SELECT vn, SUM(sum_price) AS total
FROM opitemrece
WHERE paid = 'N'
GROUP BY vn;
```
<!-- vale on -->
```

การปิด Vale ชั่วคราว (`<!-- vale off -->`) จะช่วยให้โค้ด SQL ไม่ถูกตรวจสอบเรื่องภาษา ซึ่งเหมาะสมสำหรับโค้ดที่เป็นภาษาอังกฤษ

---

## เคล็ดลับการเขียน SQL สำหรับงานการเงิน

1. **Always use LIMIT** — ฐานข้อมูล HOSxP อาจมีข้อมูลหลายล้านรายการ
2. **ตรวจสอบ confirm = 'Y'** — กรองรายการที่ยังไม่ยืนยันออกเสมอ
3. **ตรวจสอบ paid != 'C'** — กรองรายการที่ถูกยกเลิกออก
4. **ใช้ JOIN กับตารางอ้างอิง** — เช่น `income`, `patient`, `doctor` เพื่อดึงชื่อที่อ่านง่าย
5. **ระวัง NULL** — ฟิลด์ `rcpt_no` อาจเป็น NULL ถ้ายังไม่มีการออกใบเสร็จ
