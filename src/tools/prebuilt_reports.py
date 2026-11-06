"""Pre-built curated reports and statistics tools for Hospital KSP."""

from typing import Any, Dict, List, Optional
from src.database.connection import execute_raw_query
from src.config import HOSPITAL_NAME, HOSPITAL_BED_CAPACITY, HOSPITAL_CODE


def get_hospital_daily_summary(target_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get daily hospital operational summary.
    
    Args:
        target_date: Date string in 'YYYY-MM-DD' format (defaults to today).
    """
    date_filter = f"'{target_date}'" if target_date else "CURDATE()"

    # 1. OPD Visits
    sql_opd = f"SELECT COUNT(*) AS total_opd FROM ovst WHERE vstdate = {date_filter}"
    res_opd = execute_raw_query(sql_opd)
    total_opd = res_opd[0]["total_opd"] if res_opd else 0

    # 2. IPD Admissions
    sql_ipd_adm = f"SELECT COUNT(*) AS total_adm FROM ipt WHERE regdate = {date_filter}"
    res_adm = execute_raw_query(sql_ipd_adm)
    total_adm = res_adm[0]["total_adm"] if res_adm else 0

    # 3. IPD Discharges
    sql_ipd_dch = f"SELECT COUNT(*) AS total_dch FROM ipt WHERE dchdate = {date_filter}"
    res_dch = execute_raw_query(sql_ipd_dch)
    total_dch = res_dch[0]["total_dch"] if res_dch else 0

    # 4. Currently Admitted In-Patients (regardless of date)
    sql_inpatient = "SELECT COUNT(*) AS total_inpatient FROM ipt WHERE dchdate IS NULL"
    res_inp = execute_raw_query(sql_inpatient)
    total_inpatient = res_inp[0]["total_inpatient"] if res_inp else 0

    # Occupancy
    occupancy_pct = round((total_inpatient / HOSPITAL_BED_CAPACITY) * 100, 1) if HOSPITAL_BED_CAPACITY > 0 else 0

    return {
        "hospital_name": HOSPITAL_NAME,
        "hospital_code": HOSPITAL_CODE,
        "target_date": target_date or "today",
        "opd_visits_today": total_opd,
        "ipd_admitted_today": total_adm,
        "ipd_discharged_today": total_dch,
        "current_active_inpatients": total_inpatient,
        "total_bed_capacity": HOSPITAL_BED_CAPACITY,
        "bed_occupancy_rate_percent": occupancy_pct,
    }


def get_bed_occupancy() -> Dict[str, Any]:
    """
    Get real-time IPD bed occupancy breakdown across all active wards.
    """
    sql = """
        SELECT 
            w.ward,
            w.name AS ward_name,
            COUNT(i.an) AS admitted_count
        FROM ward w
        LEFT JOIN ipt i ON w.ward = i.ward AND i.dchdate IS NULL
        WHERE w.ward_active = 'Y'
        GROUP BY w.ward, w.name
        ORDER BY admitted_count DESC, w.ward ASC
    """
    rows = execute_raw_query(sql)
    total_admitted = sum(r["admitted_count"] for r in rows)
    occupancy_pct = round((total_admitted / HOSPITAL_BED_CAPACITY) * 100, 1) if HOSPITAL_BED_CAPACITY > 0 else 0

    return {
        "hospital_name": HOSPITAL_NAME,
        "total_bed_capacity": HOSPITAL_BED_CAPACITY,
        "total_current_patients": total_admitted,
        "total_occupancy_percent": occupancy_pct,
        "wards": rows,
    }


def get_top_opd_diagnoses(
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Get top OPD ICD-10 diagnoses for a given date range.
    """
    d_start = f"'{date_start}'" if date_start else "CURDATE()"
    d_end = f"'{date_end}'" if date_end else "CURDATE()"
    limit = min(max(1, limit), 50)

    sql = f"""
        SELECT 
            d.icd10,
            COALESCE(i.name, d.icd10) AS diagnosis_name,
            COUNT(d.vn) AS case_count
        FROM ovstdiag d
        LEFT JOIN icd101 i ON d.icd10 = i.code
        WHERE d.vstdate BETWEEN {d_start} AND {d_end}
          AND d.diagtype = '1'
        GROUP BY d.icd10, i.name
        ORDER BY case_count DESC
        LIMIT {limit}
    """
    rows = execute_raw_query(sql)
    return {
        "date_start": date_start or "today",
        "date_end": date_end or "today",
        "diag_type": "Primary Diagnosis (diagtype=1)",
        "count": len(rows),
        "results": rows,
    }


def search_drug_catalog(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search medicines and medical supplies in the hospital formulary.
    """
    limit = min(max(1, limit), 50)
    sql = """
        SELECT 
            icode,
            name AS trade_name,
            generic_name,
            strength,
            units,
            unitprice,
            istatus AS is_active
        FROM drugitems
        WHERE name LIKE %s OR generic_name LIKE %s
        ORDER BY name ASC
        LIMIT %s
    """
    term = f"%{keyword.strip()}%"
    return execute_raw_query(sql, (term, term, limit))


def search_lab_catalog(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search laboratory test items in the hospital lab catalog.
    """
    limit = min(max(1, limit), 50)
    sql = """
        SELECT 
            lab_items_code,
            lab_items_name,
            lab_items_unit,
            lab_items_normal_value
        FROM lab_items
        WHERE lab_items_name LIKE %s
        ORDER BY lab_items_name ASC
        LIMIT %s
    """
    term = f"%{keyword.strip()}%"
    return execute_raw_query(sql, (term, limit))
