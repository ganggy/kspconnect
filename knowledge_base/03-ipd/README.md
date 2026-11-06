# โมดูลผู้ป่วยใน (IPD Module)

## ภาพรวม

โมดูลนี้เก็บข้อมูลการรับบริการผู้ป่วยใน (Inpatient) ทั้งหมด ตั้งแต่การ Admit ผู้ป่วย การย้ายเตียง/ward การวินิจฉัย จนถึงการ Discharge

## กระบวนการทำงาน (Workflow)

```
ผู้ป่วยมารับบริการ
    ↓
OPD ตรวจ → ตัดสินใจ Admit
    ↓
สร้าง record ใน ipt (ได้ AN)
    ↓
พักรักษา → อาจมีการย้ายเตียง/ward → บันทึกใน iptbedmove
    ↓
แพทย์วินิจฉัย → บันทึกใน iptdiag (ICD10)
    ↓
สั่งยา/สั่ง Lab → บันทึกใน opitemrece
    ↓
Discharge → บันทึก dchdate, dchtype
```

## ตารางหลักในโมดูลนี้

| ตาราง | คำอธิบาย | ความสำคัญ |
|-------|---------|----------|
| `ipt` | ตารางหลักของการ Admit | ⭐⭐⭐ |
| `iptdiag` | การวินิจฉัยโรคผู้ป่วยใน (ICD10) | ⭐⭐⭐ |
| `iptbedmove` | การย้ายเตียง/ย้าย Ward | ⭐⭐⭐ |
| `iptdrugorder` | สั่งยาผู้ป่วยใน | ⭐⭐⭐ |
| `iptdeath` | ข้อมูลการเสียชีวิต | ⭐⭐ |
| `iptadm` | ข้อมูลการ Admit เพิ่มเติม | ⭐⭐ |

## Key Identifiers

- **AN (Admit Number)** - รหัสการ Admit ผู้ป่วยใน อยู่ใน `ipt.an` เป็นคีย์หลักของทุกกระบวนการ
- **HN** - เชื่อมกับตาราง `patient`
- **VN** - เชื่อมกับตาราง `ovst` (ถ้ามี OPD visit ก่อน Admit)
- **regdate** - วันที่ Admit
- **dchdate** - วันที่ Discharge

## ความสัมพันธ์เบื้องต้น

```
ipt (an)
    ├──→ patient (hn)           [ข้อมูลผู้ป่วย]
    ├──→ ovst (vn)              [OPD visit ก่อน Admit]
    ├──→ iptdiag (an)           [วินิจฉัย]
    ├──→ iptbedmove (an)        [ย้ายเตียง]
    ├──→ iptdrugorder (an)      [สั่งยา]
    ├──→ opitemrece (an)        [ค่ารักษา]
    ├──→ doctor (code)          [แพทย์]
    ├──→ pttype (pttype)        [สิทธิ]
    └──→ ward (ward)            [Ward]
```

## หมายเหตุสำคัญ

- 1 HN อาจมีหลาย AN (Admit หลายครั้ง)
- AN สร้างใหม่ทุกครั้งที่ Admit
- `ipt.vn` จะมีค่าเมื่อผู้ป่วยมาจาก OPD ก่อน Admit
- `iptbedmove` บันทึกทุกครั้งที่มีการย้ายเตียง/ward
- LOS (Length of Stay) = dchdate - regdate

## ลิงก์ไปยังเอกสารอื่น

- [ตาราง ipt](ipt.md)
- [ตาราง iptdiag](iptdiag.md)
- [ตาราง iptbedmove](iptbedmove.md)
- [ตัวอย่าง Query](common-queries.md)
