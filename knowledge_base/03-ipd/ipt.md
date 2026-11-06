# ตาราง `ipt` - การ Admit ผู้ป่วยใน

## คำอธิบาย

ตารางนี้เป็นตารางหลักของการรับผู้ป่วยใน (Inpatient/Admit) ทุกครั้งที่มีการ Admit ผู้ป่วยจะสร้าง record ใหม่ในตารางนี้ โดยมี `an` เป็นรหัสประจำการ Admit นั้นๆ

## โครงสร้างตาราง

| คอลัมน์ | ประเภท | คีย์ | คำอธิบาย |
|---------|--------|------|---------|
| `an` | varchar(9) | **PRI** | **เลข Admit Number (AN)** - คีย์หลัก |
| `hn` | varchar(9) | MUL | เลขประจำตัวผู้ป่วย (เชื่อม `patient`) |
| `vn` | varchar(13) | MUL | เลข VN (ถ้ามี OPD visit ก่อน) |
| `regdate` | date | MUL | **วันที่ Admit** |
| `regtime` | time | MUL | เวลาที่ Admit |
| `dchdate` | date | MUL | **วันที่ Discharge** |
| `dchtime` | time | - | เวลาที่ Discharge |
| `dchstts` | char(2) | MUL | สถานะ Discharge |
| `dchtype` | char(2) | - | **ประเภทการ Discharge** |
| `ward` | varchar(4) | MUL | Ward ปัจจุบัน |
| `cur_bedno` | varchar(6) | - | เตียงปัจจุบัน |
| `first_ward` | varchar(4) | - | Ward แรก |
| `admdoctor` | varchar(7) | MUL | แพทย์ที่ Admit |
| `dch_doctor` | varchar(7) | - | แพทย์ที่ Discharge |
| `incharge_doctor` | varchar(7) | - | แพทย์เจ้าของไข้ |
| `rxdoctor` | varchar(7) | - | แพทย์สั่งยา |
| `pttype` | char(2) | MUL | สิทธิการรักษา |
| `spclty` | char(2) | MUL | ความเชี่ยวชาญ |
| `ipt_spclty` | char(2) | - | ความเชี่ยวชาญ IPD |
| `prediag` | varchar(250) | - | การวินิจฉัยเบื้องต้น |
| `provision_dx` | varchar(200) | - | การวินิจฉัยโดยประมาณ |
| `provision_dx_icd` | varchar(9) | - | รหัส ICD10 โดยประมาณ |
| `rcpt_disease` | varchar(100) | - | โรคที่ระบุในใบเสร็จ |
| `ivstist` | char(2) | - | สถานะ IPD |
| `ivstost` | varchar(4) | - | สถานะออก |
| `ipt_type` | tinyint | MUL | ประเภทการ Admit |
| `bw` | int | - | น้ำหนัก (kg) |
| `body_height` | int | - | ส่วนสูง (cm) |
| `gravidity` | tinyint | - | จำนวนครั้งตั้งครรภ์ |
| `parity` | tinyint | - | จำนวนครั้งคลอด |
| `living_children` | tinyint | - | จำนวนบุตรที่มีชีวิต |
| `leave_home_day` | int | - | จำนวนวันลาบ้าน |
| `operation_status` | char(1) | - | สถานะผ่าตัด |
| `operation_status_id` | int | - | รหัสสถานะผ่าตัด |
| `finance_lock` | char(1) | - | ล็อกการเงิน |
| `finance_status_flag` | int | - | สถานะการเงิน |
| `finance_summary_date` | date | - | วันสรุปการเงิน |
| `finance_transfer` | char(1) | - | โอนเงิน |
| `confirm_discharge` | char(1) | MUL | ยืนยัน Discharge |
| `data_ok` | char(1) | MUL | ข้อมูลครบถ้วน |
| `data_exp_date` | date | MUL | วันหมดอายุข้อมูล |
| `auto_charge_amount` | double | - | ยอดค่าใช้จ่ายอัตโนมัติ |
| `act_money_limit` | double | - | วงเงิน |
| `drg` | varchar(5) | - | รหัส DRG |
| `mdc` | char(2) | - | Major Diagnostic Category |
| `rw` | double | - | Relative Weight |
| `adjrw` | double | - | Adjusted RW |
| `grouper_version` | varchar(15) | - | เวอร์ชัน Grouper |
| `grouper_actlos` | int | - | Actual LOS (Grouper) |
| `reimburse_price` | double | - | ราคาเบิกจ่าย |
| `err` | int | - | ข้อผิดพลาด Grouper |
| `warn` | int | - | คำเตือน Grouper |
| `oldcode` | varchar(20) | - | รหัสเก่า |
| `update_datetime` | datetime | - | วันเวลาปรับปรุง |
| `dateupdate` | timestamp | - | วันเวลาปรับปรุง (auto) |

## ฟิลด์สำคัญที่ใช้บ่อย

| ฟิลด์ | ใช้ทำอะไร |
|-------|----------|
| `an` | เชื่อมทุกตาราง IPD (วินิจฉัย, ย้ายเตียง, สั่งยา) |
| `hn` | เชื่อมกับ `patient` |
| `vn` | เชื่อมกับ `ovst` (ถ้ามี) |
| `regdate` | วัน Admit |
| `dchdate` | วัน Discharge (NULL = ยัง Admit อยู่) |
| `ward` | Ward ปัจจุบัน |
| `cur_bedno` | เตียงปัจจุบัน |
| `dchtype` | ประเภทการ Discharge |

## ประเภทการ Discharge (`dchtype`)

| รหัส | ความหมาย |
|------|---------|
| 01 | หาย/ดีขึ้น |
| 02 | ยังไม่หาย |
| 03 | ตาย |
| 04 | หนีกลับ |
| 05 | ส่งต่อ |
| 08 | ส่งต่อตามสิทธิ |
| 09 | ปฏิเสธการรักษา |

## ความสัมพันธ์

```sql
ipt.hn → patient.hn              (ข้อมูลผู้ป่วย)
ipt.vn → ovst.vn                 (OPD visit ก่อน Admit)
ipt.an → iptdiag.an              (วินิจฉัย)
ipt.an → iptbedmove.an           (ย้ายเตียง)
ipt.an → iptdrugorder.an         (สั่งยา)
ipt.an → opitemrece.an           (ค่ารักษา)
ipt.admdoctor → doctor.code      (แพทย์)
ipt.ward → ward.ward             (ชื่อ Ward)
```

## ตัวอย่าง Query

```sql
-- ผู้ป่วยที่ยัง Admit อยู่
SELECT 
    i.an,
    i.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    i.regdate,
    i.ward,
    w.name AS ward_name,
    i.cur_bedno,
    i.admdoctor,
    d.name AS doctor_name
FROM ipt i
LEFT JOIN patient p ON i.hn = p.hn
LEFT JOIN ward w ON i.ward = w.ward
LEFT JOIN doctor d ON i.admdoctor = d.code
WHERE i.dchdate IS NULL;

-- คำนวณ LOS (Length of Stay)
SELECT 
    i.an,
    i.hn,
    i.regdate,
    i.dchdate,
    DATEDIFF(IFNULL(i.dchdate, CURDATE()), i.regdate) AS los_days
FROM ipt i
WHERE i.an = '650000001';

-- ผู้ป่วยที่ Discharge วันนี้
SELECT 
    i.an,
    i.hn,
    CONCAT(p.pname, p.fname, ' ', p.lname) AS patient_name,
    i.dchdate,
    i.dchtype,
    CASE i.dchtype 
        WHEN '01' THEN 'หาย/ดีขึ้น'
        WHEN '03' THEN 'ตาย'
        WHEN '04' THEN 'หนีกลับ'
        WHEN '05' THEN 'ส่งต่อ'
        ELSE i.dchtype
    END AS discharge_status
FROM ipt i
LEFT JOIN patient p ON i.hn = p.hn
WHERE i.dchdate = CURDATE();
```

## หมายเหตุ

- `dchdate IS NULL` หมายถึงผู้ป่วยยัง Admit อยู่
- `LOS` (Length of Stay) = จำนวนวันที่พักรักษา = dchdate - regdate
- `dchtype = '03'` คือผู้ป่วยเสียชีวิต ควรตรวจสอบกับ `iptdeath`
- `drg`, `mdc`, `rw` ใช้สำหรับการคำนวณค่าใช้จ่ายตาม DRG
