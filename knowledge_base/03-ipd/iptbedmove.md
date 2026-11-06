# ตาราง `iptbedmove` - การย้ายเตียง/Ward

## คำอธิบาย

ตารางนี้เก็บประวัติการย้ายเตียงและย้าย Ward ของผู้ป่วยใน ทุกครั้งที่มีการย้ายเตียงจะสร้าง record ใหม่ในตารางนี้ ช่วยให้ทราบประวัติการเคลื่อนย้ายของผู้ป่วยตลอดการ Admit

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `iptbedmove_id` | int | **PRI** | รหัส running number |
| `an` | varchar(9) | MUL | เลข Admit Number |
| `movedate` | date | - | **วันที่ย้าย** |
| `movetime` | time | - | เวลาที่ย้าย |
| `oward` | varchar(9) | - | **Ward เดิม** |
| `obedno` | varchar(9) | - | **เตียงเดิม** |
| `nward` | varchar(9) | - | **Ward ใหม่** |
| `nbedno` | varchar(9) | - | **เตียงใหม่** |
| `nroomno` | varchar(10) | - | ห้องใหม่ |
| `spclty` | char(2) | - | ความเชี่ยวชาญ |
| `movereason` | varchar(250) | - | เหตุผลการย้าย |
| `entry_datetime` | datetime | - | วันเวลาบันทึก |
| `staff` | varchar(50) | - | ผู้บันทึก |
| `hos_guid` | varchar(38) | MUL | GUID |

## ความสัมพันธ์

```sql
iptbedmove.an → ipt.an           (ข้อมูล Admit)
iptbedmove.oward → ward.ward     (Ward เดิม)
iptbedmove.nward → ward.ward     (Ward ใหม่)
```

## หลักการทำงาน

1. ผู้ป่วย Admit → บันทึก ward/เตียงแรกใน `ipt` และสร้าง record ใน `iptbedmove`
2. มีการย้ายเตียง → สร้าง record ใหม่ใน `iptbedmove` โดย:
   - `oward`/`obedno` = ward/เตียงเดิม
   - `nward`/`nbedno` = ward/เตียงใหม่
3. อัปเดต `ipt.ward` และ `ipt.cur_bedno` เป็นค่าใหม่

## ตัวอย่าง Query

```sql
-- ประวัติการย้ายเตียงของผู้ป่วย
SELECT 
    bm.an,
    bm.movedate,
    bm.movetime,
    bm.oward,
    ow.name AS old_ward_name,
    bm.obedno AS old_bed,
    bm.nward,
    nw.name AS new_ward_name,
    bm.nbedno AS new_bed,
    bm.movereason
FROM iptbedmove bm
LEFT JOIN ward ow ON bm.oward = ow.ward
LEFT JOIN ward nw ON bm.nward = nw.ward
WHERE bm.an = '650000001'
ORDER BY bm.movedate, bm.movetime;

-- จำนวนวันที่พักในแต่ละ Ward
SELECT 
    bm.an,
    bm.nward,
    w.name AS ward_name,
    MIN(bm.movedate) AS first_date,
    MAX(COALESCE(next_bm.movedate, i.dchdate, CURDATE())) AS last_date,
    DATEDIFF(MAX(COALESCE(next_bm.movedate, i.dchdate, CURDATE())), MIN(bm.movedate)) AS days
FROM iptbedmove bm
LEFT JOIN iptbedmove next_bm ON bm.an = next_bm.an AND bm.iptbedmove_id < next_bm.iptbedmove_id
LEFT JOIN ward w ON bm.nward = w.ward
LEFT JOIN ipt i ON bm.an = i.an
WHERE bm.an = '650000001'
GROUP BY bm.an, bm.nward, bm.iptbedmove_id
ORDER BY MIN(bm.movedate);
```

## หมายเหตุ

- ถ้า `oward` เป็น NULL หรือว่าง แสดงว่าเป็นการ Admit ครั้งแรก
- สามารถนับจำนวนครั้งที่ย้ายเตียงได้จากจำนวน record
- ใช้ตรวจสอบการใช้งาน Ward/เตียงในแต่ละช่วงเวลา
