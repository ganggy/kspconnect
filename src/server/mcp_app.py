"""FastMCP Server providing Universal Hospital Tools to Claude, Antigravity, Cursor, and MCP clients."""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from src.config import HOSPITAL_NAME, HOSPITAL_BED_CAPACITY, HOSPITAL_CODE
from src.database.connection import check_db_health
from src.knowledge.retriever import retriever
from src.tools.prebuilt_reports import (
    get_hospital_daily_summary as _get_daily_summary,
    get_bed_occupancy as _get_bed_occupancy,
    get_top_opd_diagnoses as _get_top_diagnoses,
    search_drug_catalog as _search_drugs,
    search_lab_catalog as _search_labs,
)
from src.tools.sql_runner import execute_safe_hospital_query as _execute_safe_query

# Initialize FastMCP Server
mcp = FastMCP("KSP Hospital Intelligence Gateway")


@mcp.tool()
def get_hospital_overview() -> Dict[str, Any]:
    """
    Get general hospital profile, bed capacity, and live database connection health.
    """
    db_health = check_db_health()
    return {
        "hospital_name": HOSPITAL_NAME,
        "hospital_code": HOSPITAL_CODE,
        "bed_capacity": HOSPITAL_BED_CAPACITY,
        "his_system": "HOSxP (MySQL/MariaDB)",
        "database_health": db_health,
        "available_knowledge_modules": [m["category"] for m in retriever.list_modules()],
    }


@mcp.tool()
def search_hospital_knowledge(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Search hospital knowledge base, HOSxP table dictionaries, query templates, and documentation.
    
    Args:
        query: Search keywords or question in Thai or English (e.g., 'ตารางยา opitemrece', 'ตรวจผลแล็บ', 'สิทธิการรักษา pttype').
        top_k: Number of matching documents to return (default 3).
    """
    return retriever.search(query=query, top_k=top_k)


@mcp.tool()
def get_table_schema(table_name: str) -> Dict[str, Any]:
    """
    Get comprehensive schema, column descriptions, keys, and usage notes for a HOSxP table.
    
    Args:
        table_name: Name of the HOSxP table (e.g., 'patient', 'ovst', 'ipt', 'opitemrece', 'drugitems', 'lab_head', 'lab_order').
    """
    return retriever.get_table_schema(table_name)


@mcp.tool()
def get_table_relationships() -> Dict[str, Any]:
    """
    Get detailed Entity-Relationship documentation explaining how patient, OPD, IPD, and opitemrece tables link together.
    """
    return retriever.get_relationships()


@mcp.tool()
def get_hospital_daily_summary(target_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get hospital operational statistics for today or a specific date (OPD visits, IPD admits/discharges, active admitted patients, occupancy rate).
    
    Args:
        target_date: Date string in 'YYYY-MM-DD' format (optional, defaults to current date).
    """
    return _get_daily_summary(target_date)


@mcp.tool()
def get_bed_occupancy() -> Dict[str, Any]:
    """
    Get real-time inpatient bed occupancy breakdown across all active wards compared against hospital capacity (90 beds).
    """
    return _get_bed_occupancy()


@mcp.tool()
def get_top_opd_diagnoses(date_start: Optional[str] = None, date_end: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """
    Get top OPD ICD-10 primary diagnoses for a given date range.
    
    Args:
        date_start: Start date in 'YYYY-MM-DD' format (defaults to today).
        date_end: End date in 'YYYY-MM-DD' format (defaults to today).
        limit: Number of top diagnoses (default 10, max 50).
    """
    return _get_top_diagnoses(date_start, date_end, limit)


@mcp.tool()
def search_drug_catalog(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search hospital drug formulary by brand name or generic name.
    
    Args:
        keyword: Medicine name to search (e.g. 'paracetamol', 'amoxicillin', 'losartan').
        limit: Maximum results (default 20).
    """
    return _search_drugs(keyword, limit)


@mcp.tool()
def search_lab_catalog(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search hospital laboratory test items by test name.
    
    Args:
        keyword: Laboratory test name to search (e.g. 'glucose', 'cbc', 'lipid', 'covid').
        limit: Maximum results (default 20).
    """
    return _search_labs(keyword, limit)


@mcp.tool()
def execute_safe_hospital_query(sql_query: str) -> Dict[str, Any]:
    """
    Execute custom read-only SQL SELECT queries against the hospital HOSxP database with automatic PDPA masking and security constraints.
    
    Args:
        sql_query: Read-only SELECT SQL statement.
    """
    return _execute_safe_query(sql_query)


@mcp.prompt()
def hospital_analyst_prompt() -> str:
    """Prompt for setting up AI agent as a hospital informatics expert."""
    return f"""คุณคือผู้ช่วยอัจฉริยะด้านสารสนเทศโรงพยาบาล (Hospital Informatics AI Assistant) ของ {HOSPITAL_NAME}
ระบบ HIS หลัก: HOSxP (MySQL Database)
ขนาดโรงพยาบาล: {HOSPITAL_BED_CAPACITY} เตียง

แนวทางการทำงาน:
1. หากต้องการทราบว่าข้อมูลเก็บที่ตารางไหน ให้ใช้ 'search_hospital_knowledge' หรือ 'get_table_schema'
2. หากต้องการตัวเลขภาพรวมโรงพยาบาล ให้ใช้ 'get_hospital_daily_summary' หรือ 'get_bed_occupancy'
3. หากผู้ใช้ต้องการรายงานเฉพาะกิจ ให้ตรวจสอบความสัมพันธ์ของตารางผ่าน 'get_table_relationships' แล้วเขียนคำสั่ง SELECT ส่งให้ 'execute_safe_hospital_query'
4. คำนึงถึงความปลอดภัยของข้อมูลผู้ป่วย (PDPA) เสมอ ไม่เปิดเผยข้อมูลที่ระบุตัวตนจริงแก่บุคคลภายนอก
"""
