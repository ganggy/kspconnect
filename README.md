# 🏥 KSP Connect: Universal Hospital Intelligence Gateway & Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-purple.svg)](https://github.com/modelcontextprotocol)

**KSP Connect (`kspconnect`)** คือ คลังความรู้สารสนเทศโรงพยาบาลและเกตเวย์เชื่อมต่อข้อมูลอัจฉริยะ (Universal Hospital Intelligence Gateway) สำหรับเชื่อมระบบฐานข้อมูลโรงพยาบาล **HOSxP** เข้ากับ AI ทุกค่าย ไม่ว่าจะเป็น **Claude, ChatGPT, Google Gemini, Antigravity, Cursor** หรือ **Local LLM**

---

## 💡 วิธีนำไปใช้วางใน Prompt กับ AI ทุกเจ้า (Prompt Injection Guide)

เมื่อต้องการให้ AI เจ้าไหนก็ตาม (ChatGPT, Claude, Gemini, DeepSeek, Antigravity, Cursor) มีความเข้าใจโครงสร้างฐานข้อมูลและระบบสารสนเทศของโรงพยาบาลเกษตรสมบูรณ์ (KSP) อย่างสมบูรณ์แบบ เพียงคัดลอกข้อความด้านล่างไปวางใน Prompt:

```text
โปรดใช้คลังความรู้โครงสร้างฐานข้อมูลโรงพยาบาลจาก https://github.com/ganggy/kspconnect 
เพื่อช่วยฉัน:
[ใส่คำถามหรือความต้องการของคุณที่นี่ เช่น:
 - ออกแบบ SQL ดึงข้อมูลสถิติผู้ป่วยนอกแยกตามสิทธิการรักษาเดือนล่าสุด
 - ตรวจสอบว่าผลแล็บน้ำตาลในเลือดสะสม (HbA1c) เชื่อมโยงกับตารางไหนบ้าง
 - อธิบายโครงสร้างของตาราง opitemrece และวิธีหาค่ารักษาพยาบาล]
```

### 🧠 สิ่งที่ AI จะได้รับทันทีที่อ่าน Repo นี้:
1. **บริบทโรงพยาบาล:** รพ.เกษตรสมบูรณ์ (ขนาด 90 เตียง, รหัส 10714)
2. **โครงสร้างตาราง HOSxP ครบวงจร:** ในไฟล์ [`KNOWLEDGE_BASE.md`](KNOWLEDGE_BASE.md) ครอบคลุมผู้ป่วย (`patient`), ผู้ป่วยนอก (`ovst`), ผู้ป่วยใน (`ipt`), คัดกรอง (`opdscreen`), การวินิจฉัย (`ovstdiag`), คลังยา (`drugitems`), ผลแล็บ (`lab_head`, `lab_order`), ค่ารักษา (`opitemrece`), และสิทธิการรักษา (`pttype`)
3. **คลังคิวรีสำเร็จรูป:** ในไฟล์ [`QUERY_COOKBOOK.md`](QUERY_COOKBOOK.md) รวบรวมคำสั่ง SQL จริงที่ทดสอบแล้วบน MariaDB/MySQL ของโรงพยาบาล
4. **มาตรฐานความปลอดภัย:** กฎ PDPA ในการ Mask เลขบัตรประชาชน 13 หลักและชื่อ-นามสกุล

---

## ⚡ การเชื่อมต่อแบบ Live Tools / Skill (ให้ AI ดึงข้อมูลจริงจาก รพ.)

### 1. เชื่อมต่อผ่าน MCP (Claude Desktop, Cursor, Antigravity)
สำหรับ AI ที่รองรับโปรโตคอล **Model Context Protocol (MCP)** สามารถตั้งค่าให้ AI เรียกฟังก์ชันดึงข้อมูลแบบ Real-time ได้ทันที:

เพิ่มบล็อกนี้ใน `claude_desktop_config.json` หรือ `antigravity.json`:
```json
{
  "mcpServers": {
    "kspconnect": {
      "command": "python",
      "args": ["d:/skill for ai connect ksp/run_mcp.py"]
    }
  }
}
```

**Tools ที่ AI จะได้รับ:**
- `get_hospital_daily_summary(target_date)`: สรุปยอด OPD วันนี้, ยอด Admit, Discharged, ผู้ป่วยนอน รพ. ปัจจุบัน, อัตราครองเตียง (%)
- `get_bed_occupancy()`: สรุปสถานะเตียงแยกตามตึก/วอร์ดเทียบกับขนาด 90 เตียง
- `search_hospital_knowledge(query)`: ค้นหาคู่มือและพจนานุกรมตาราง HOSxP
- `get_table_schema(table_name)`: ดึงข้อมูลคอลัมน์และคีย์ของตาราง HOSxP
- `search_drug_catalog(keyword)`: ค้นหารายการยาและราคาในคลัง
- `search_lab_catalog(keyword)`: ค้นหารายการทดสอบทางห้องปฏิบัติการ
- `execute_safe_hospital_query(sql_query)`: รันคำสั่ง SQL อ่านข้อมูลอย่างปลอดภัยพร้อมระบบ Masking อัตโนมัติ

---

### 2. เชื่อมต่อกับ ChatGPT (Custom GPT Actions)
1. เปิดรัน Web API ด้วยคำสั่ง:
   ```bash
   python run_api.py
   ```
2. ใช้ Cloudflare Tunnel หรือ Reverse Proxy ชี้มายังพอร์ต `8000` (เช่น `https://ksp-ai.yourdomain.com`)
3. ใน OpenAI GPT Builder เมนู **Actions** ให้ Import ไฟล์ [`openapi.json`](openapi.json)

---

## 🛠️ การติดตั้งและรันภายในเครื่อง (Local Setup)

### 1. ติดตั้ง Dependencies
```bash
git clone https://github.com/ganggy/kspconnect.git
cd kspconnect
pip install -r requirements.txt
```

### 2. ตั้งค่าการเชื่อมต่อ (`.env`)
คัดลอกไฟล์ `.env.example` เป็น `.env` และระบุ IP ของ MySQL HOSxP:
```ini
HOS_DB_HOST=192.168.2.254
HOS_DB_PORT=3306
HOS_DB_USER=opd
HOS_DB_PASSWORD=opd
HOS_DB_NAME=hos
HOSPITAL_NAME=โรงพยาบาลเกษตรสมบูรณ์ (KSP)
HOSPITAL_BED_CAPACITY=90
ENABLE_PDPA_MASKING=true
```

### 3. รันการทดสอบระบบ (Test Suite)
```bash
python test_suite.py
```
*(ระบบจะทดสอบการเชื่อมต่อฐานข้อมูล HOSxP, ตัวกรอง PDPA Masker, SQL Safety Validator, และคลังความรู้ 11 รายการ)*

### 4. รันเซิร์ฟเวอร์
* **เปิดโหมด MCP:** `python run_mcp.py`
* **เปิดโหมด REST API:** `python run_api.py`

---

## 🔒 มาตรการความปลอดภัยและ PDPA (Security & Compliance)
- **Read-Only Enforced:** อนุญาตเฉพาะคำสั่ง `SELECT` เท่านั้น บล็อกคำสั่ง `INSERT/UPDATE/DELETE/DROP` โดยเด็ดขาด
- **Anti-SQL Injection:** ตรวจสอบโครงสร้างคิวรีและปฏิเสธคำสั่งซ้อน (Stacked Queries `;`)
- **Memory Protection:** บังคับใส่ `LIMIT` อัตโนมัติ ป้องกันฐานข้อมูลค้างจากคิวรีขนาดใหญ่
- **PDPA Data Masking:** กรองและเซ็นเซอร์เลขบัตรประชาชน 13 หลัก, ชื่อ-นามสกุล, และเบอร์โทรศัพท์โดยอัตโนมัติก่อนส่งผลลัพธ์ให้ AI

---

## 📂 โครงสร้างโปรเจกต์ (Repository Structure)

```text
kspconnect/
├── README.md               # เอกสารแนะนำและคู่มือการ Prompt
├── SKILL.md                # ข้อกำหนด Agent Skill สำหรับ AI
├── KNOWLEDGE_BASE.md       # คลังรวมเอกสารโครงสร้างฐานข้อมูล HOSxP ทั้งหมด
├── QUERY_COOKBOOK.md       # รวมตัวอย่าง SQL คิวรีสถิติโรงพยาบาลจริง
├── openapi.json            # สเปก OpenAPI สำหรับ ChatGPT Actions
├── requirements.txt        # รายการไลบรารีที่จำเป็น
├── run_mcp.py              # สคริปต์เปิด FastMCP Server
├── run_api.py              # สคริปต์เปิด FastAPI REST Server
├── test_suite.py           # สคริปต์ทดสอบระบบอัตโนมัติ
├── knowledge_base/         # โฟลเดอร์คู่มือแยกโมดูล (Patient, OPD, IPD, Drug, Lab, Finance)
└── src/
    ├── config.py           # ค่า Config และการตั้งค่าระบบ
    ├── database/           # ตัวเชื่อม MySQL HOSxP และ SQL Safety Validator
    ├── security/           # ตัวเซ็นเซอร์ข้อมูลส่วนบุคคล (PDPA Masking Engine)
    ├── knowledge/          # เอนจินค้นหาและอ่านข้อมูล Schema
    ├── tools/              # ฟังก์ชันรายงานสถิติสำเร็จรูป (OPD, เตียง, ยา, แล็บ)
    └── server/             # ตัวให้บริการ MCP Server และ FastAPI App
```

---

## 📄 License
MIT License - พัฒนาขึ้นเพื่อประโยชน์ทางด้านการแพทย์และสารสนเทศโรงพยาบาล (Hospital Informatics)
