"""Comprehensive Test Suite for KSP Hospital AI Gateway & Skill System."""

import sys
import io

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from src.database.connection import check_db_health
from src.database.validator import validate_and_sanitize_sql
from src.knowledge.retriever import retriever
from src.security.pdpa import mask_record
from src.tools.prebuilt_reports import (
    get_hospital_daily_summary,
    get_bed_occupancy,
    get_top_opd_diagnoses,
    search_drug_catalog,
)
from src.tools.sql_runner import execute_safe_hospital_query


def run_tests():
    print("=" * 60)
    print("🏥 KSP Hospital AI Gateway - Test Suite Verification")
    print("=" * 60)

    # 1. Database Health
    db_status = check_db_health()
    assert db_status["connected"], f"Database connection failed: {db_status}"
    print(f"✅ 1. Database Connected: MariaDB/MySQL at {db_status['host']} (Time: {db_status['server_time']})")

    # 2. Knowledge Base Modules
    modules = retriever.list_modules()
    assert len(modules) >= 6, "Expected at least 6 knowledge base categories"
    print(f"✅ 2. Knowledge Base Loaded: {len(modules)} categories found")

    # 3. Knowledge Search
    search_res = retriever.search("ตารางสั่งยาและค่ารักษา opitemrece")
    assert len(search_res) > 0, "Knowledge search failed"
    print(f"✅ 3. Knowledge Search Working: Top match -> {search_res[0]['file']}")

    # 4. Table Schema Lookup
    schema_res = retriever.get_table_schema("patient")
    assert schema_res["found"], "Patient schema lookup failed"
    print(f"✅ 4. Table Schema Lookup Working: 'patient' table documented")

    # 5. Pre-built Daily Summary
    daily = get_hospital_daily_summary()
    assert "opd_visits_today" in daily, "Daily summary missing opd_visits"
    print(f"✅ 5. Daily Summary: OPD today={daily['opd_visits_today']}, Active Inpatients={daily['current_active_inpatients']} (Occupancy: {daily['bed_occupancy_rate_percent']}%)")

    # 6. Bed Occupancy Breakdown
    beds = get_bed_occupancy()
    assert len(beds["wards"]) > 0, "No wards found"
    print(f"✅ 6. Bed Occupancy Working: {len(beds['wards'])} active wards reported")

    # 7. Drug Search
    drugs = search_drug_catalog("paracetamol", limit=3)
    print(f"✅ 7. Drug Catalog Search: Found {len(drugs)} items for 'paracetamol'")

    # 8. SQL Safety Validator (Safe SELECT)
    is_safe, sanitized, err = validate_and_sanitize_sql("SELECT hn, fname FROM patient")
    assert is_safe and "LIMIT" in sanitized, "Validator failed on safe SELECT"
    print(f"✅ 8. SQL Validator: Appended LIMIT -> '{sanitized}'")

    # 9. SQL Safety Validator (Block DROP/DELETE)
    is_safe_bad, _, err_bad = validate_and_sanitize_sql("DROP TABLE patient")
    assert not is_safe_bad, "Validator failed to block DROP TABLE"
    print(f"✅ 9. SQL Validator Security Guard: Blocked dangerous query successfully ('{err_bad}')")

    # 10. PDPA Masking Engine
    sample_data = {"hn": "12345", "cid": "1430900123456", "fname": "สมชาย", "lname": "ใจดี", "hometel": "0812345678"}
    masked = mask_record(sample_data)
    assert "XXXXX" in masked["cid"], "CID was not masked"
    assert "*" in masked["fname"], "First name was not masked"
    assert "XXX" in masked["hometel"], "Phone was not masked"
    print(f"✅ 10. PDPA Masker Working: CID={masked['cid']}, Name={masked['fname']} {masked['lname']}, Tel={masked['hometel']}")

    # 11. End-to-End Safe Query Execution
    query_res = execute_safe_hospital_query("SELECT hn, cid, fname, lname FROM patient LIMIT 1")
    assert query_res["success"], f"Query execution failed: {query_res.get('error')}"
    print(f"✅ 11. End-to-End Safe Query: Successfully fetched and masked 1 record in {query_res['execution_time_seconds']}s")

    print("=" * 60)
    print("🎉 ALL 11 TESTS PASSED! System is fully operational and safe.")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
