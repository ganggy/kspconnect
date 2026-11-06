# ตาราง `patient_address` - รหัสที่อยู่ผู้ป่วย

## คำอธิบาย

ตารางนี้เก็บรหัสจังหวัด อำเภอ และตำบล ของผู้ป่วย แยกจากตาราง `patient` ที่เก็บข้อมูลที่อยู่ในรูปข้อความ เพื่อให้สามารถ query และรายงานตามพื้นที่ได้ง่าย

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `hn` | varchar(9) | **PRI** | เลขประจำตัวผู้ป่วย (เชื่อมกับ `patient`) |
| `province_code` | varchar(2) | - | รหัสจังหวัด |
| `district_code` | varchar(4) | - | รหัสอำเภอ |
| `tambol_code` | varchar(6) | - | รหัสตำบล |

## ความสัมพันธ์

```sql
patient_address.hn → patient.hn
patient_address.province_code → thaiaddress.chwpart
patient_address.district_code → thaiaddress.amppart  
patient_address.tambol_code → thaiaddress.tmbpart
```

## หลักการใช้งาน

ตาราง `patient` เก็บที่อยู่ในรูปข้อความ (`addrpart`, `moopart`, `tmbpart`, `amppart`, `chwpart`) แต่บางครั้งเป็นรหัส บางครั้งเป็นชื่อ ทำให้ยากต่อการ query

ตาราง `patient_address` ช่วยให้สามารถ:
- ค้นหาผู้ป่วยตามจังหวัด/อำเภอ/ตำบลได้แม่นยำ
- Join กับตาราง `thaiaddress` เพื่อแสดงชื่อจังหวัด/อำเภอ/ตำบล
- ทำรายงานเชิงพื้นที่ (GIS report)

## ตัวอย่าง Query

```sql
-- ดูที่อยู่ผู้ป่วยพร้อมชื่อจังหวัด
SELECT 
    p.hn,
    p.fname,
    p.lname,
    p.addrpart,
    pa.province_code,
    pa.district_code,
    pa.tambol_code
FROM patient p
LEFT JOIN patient_address pa ON p.hn = pa.hn
WHERE p.hn = '000000001';
```

## หมายเหตุ

- ไม่ใช่ทุกคนจะมี record ใน `patient_address` (บางคนอาจลงทะเบียนก่อนสร้างตารางนี้)
- รหัสตำบล (`tambol_code`) มี 6 หลัก ประกอบด้วย จังหวัด(2) + อำเภอ(2) + ตำบล(2)
