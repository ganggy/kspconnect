"""Safe Ad-hoc SQL Query Runner with PDPA Protection."""

import time
from typing import Any, Dict
from src.database.connection import execute_raw_query
from src.database.validator import validate_and_sanitize_sql
from src.security.pdpa import mask_dataset
from src.config import ENABLE_PDPA_MASKING


def execute_safe_hospital_query(sql_query: str, bypass_masking: bool = False) -> Dict[str, Any]:
    """
    Validate, execute, and sanitize an ad-hoc SQL query on the HOSxP database.
    
    Args:
        sql_query: The SQL SELECT statement to execute.
        bypass_masking: Whether to skip PDPA masking (only allowed for authorized audits).
        
    Returns:
        Dict with success status, row count, execution time, sanitized SQL, and results.
    """
    is_valid, sanitized_sql, err = validate_and_sanitize_sql(sql_query)
    if not is_valid:
        return {
            "success": False,
            "error": err,
            "executed_sql": None,
            "row_count": 0,
            "data": [],
        }

    start_time = time.time()
    try:
        raw_rows = execute_raw_query(sanitized_sql)
        elapsed_sec = round(time.time() - start_time, 3)

        # Apply PDPA Masking if enabled
        should_mask = ENABLE_PDPA_MASKING and not bypass_masking
        final_data = mask_dataset(raw_rows) if should_mask else raw_rows

        return {
            "success": True,
            "executed_sql": sanitized_sql,
            "row_count": len(final_data),
            "execution_time_seconds": elapsed_sec,
            "pdpa_masked": should_mask,
            "data": final_data,
        }
    except Exception as e:
        elapsed_sec = round(time.time() - start_time, 3)
        return {
            "success": False,
            "error": f"MySQL Database Error: {str(e)}",
            "executed_sql": sanitized_sql,
            "execution_time_seconds": elapsed_sec,
            "row_count": 0,
            "data": [],
        }
