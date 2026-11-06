# ความสัมพันธ์ Patient → OPD → IPD

## โครงสร้างหลัก

```
patient (hn)
    ├──→ ovst (vn) ──→ opdscreen (vn)
    │                  ├──→ ovstdiag (vn)
    │                  ├──→ opitemrece (vn)
    │                  └──→ lab_head (vn)
    │
    └──→ ipt (an) ───→ iptdiag (an)
                       ├──→ iptbedmove (an)
                       ├──→ iptdrugorder (an)
                       └──→ opitemrece (an)
```

## ความสัมพันธ์ละเอียด

### Patient → OPD

| ตารางต้นทาง | คอลัมน์ | ตารางปลายทาง | คอลัมน์ | ความหมาย |
|-----------|--------|------------|--------|---------|
| patient | hn | ovst | hn | ผู้ป่วย → การ visit |
| ovst | vn | opdscreen | vn | visit → คัดกรอง |
| ovst | vn | ovstdiag | vn | visit → วินิจฉัย |
| ovst | vn | opitemrece | vn | visit → สั่งยา/ค่ารักษา |
| ovst | vn | lab_head | vn | visit → สั่ง Lab |
| ovst | doctor | doctor | code | visit → แพทย์ |
| ovst | pttype | pttype | pttype | visit → สิทธิ |
| ovst | spclty | spclty | spclty | visit → แผนก |

### Patient → IPD

| ตารางต้นทาง | คอลัมน์ | ตารางปลายทาง | คอลัมน์ | ความหมาย |
|-----------|--------|------------|--------|---------|
| patient | hn | ipt | hn | ผู้ป่วย → การ Admit |
| ipt | an | iptdiag | an | Admit → วินิจฉัย |
| ipt | an | iptbedmove | an | Admit → ย้ายเตียง |
| ipt | an | iptdrugorder | an | Admit → สั่งยา |
| ipt | an | opitemrece | an | Admit → ค่ารักษา |
| ipt | ward | ward | ward | Admit → Ward |
| ipt | admdoctor | doctor | code | Admit → แพทย์ |

### OPD → IPD (เชื่อมกัน)

| ตารางต้นทาง | คอลัมน์ | ตารางปลายทาง | คอลัมน์ | ความหมาย |
|-----------|--------|------------|--------|---------|
| ovst | vn | ipt | vn | OPD visit → Admit |
| ovst | an | ipt | an | OPD → IPD (ผ่าน ovst.an) |

## ตัวอย่าง Query ข้ามตาราง

```sql
-- ดูประวัติการรักษาทั้งหมดของผู้ป่วย (OPD + IPD)
SELECT 
    p.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    'OPD' AS type,
    o.vn AS ref_no,
    o.vstdate AS date,
    o.vsttime AS time,
    d.name AS doctor_name
FROM patient p
LEFT JOIN ovst o ON p.hn = o.hn
LEFT JOIN doctor d ON o.doctor = d.code
WHERE p.hn = '000000001'

UNION ALL

SELECT 
    p.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    'IPD' AS type,
    i.an AS ref_no,
    i.regdate AS date,
    i.regtime AS time,
    d.name AS doctor_name
FROM patient p
LEFT JOIN ipt i ON p.hn = i.hn
LEFT JOIN doctor d ON i.admdoctor = d.code
WHERE p.hn = '000000001'

ORDER BY date DESC;
```
