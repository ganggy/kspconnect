"""SQL Query Validator and Sanitizer for Safe Hospital Database Access."""

import re
from typing import Tuple
from src.config import DEFAULT_QUERY_LIMIT, MAX_QUERY_LIMIT

# Dangerous SQL keywords that are strictly prohibited
DISALLOWED_KEYWORDS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bTRUNCATE\b",
    r"\bREPLACE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bLOCK\b",
    r"\bUNLOCK\b",
    r"\bSHUTDOWN\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bCALL\b",
    r"\bINTO\s+OUTFILE\b",
    r"\bINTO\s+DUMPFILE\b",
    r"\bLOAD_FILE\b",
    r"\bLOAD\s+DATA\b",
]

DISALLOWED_PATTERN = re.compile("|".join(DISALLOWED_KEYWORDS), re.IGNORECASE)


def validate_and_sanitize_sql(query: str) -> Tuple[bool, str, str]:
    """
    Validate SQL query to ensure it is strictly read-only and safe.
    
    Returns:
        (is_valid, sanitized_sql, error_message)
    """
    cleaned = query.strip()
    
    # Remove trailing semicolon if present
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()
        
    # Check for multiple statements (prevent stacked queries SQL injection)
    if ";" in cleaned:
        return False, "", "ไม่อนุญาตให้รันคำสั่งหลายคิวรีพร้อมกัน (ห้ามมีเครื่องหมาย ; คั่นคำสั่ง)"

    # Must start with SELECT, SHOW, or EXPLAIN
    if not re.match(r"^(SELECT|SHOW|EXPLAIN|DESC|DESCRIBE)\b", cleaned, re.IGNORECASE):
        return False, "", "อนุญาตเฉพาะคำสั่ง SELECT, SHOW หรือ EXPLAIN เพื่ออ่านข้อมูลเท่านั้น"

    # Check for disallowed modification keywords
    match = DISALLOWED_PATTERN.search(cleaned)
    if match:
        return False, "", f"ตรวจพบคำสั่งที่อาจเปลี่ยนแปลงข้อมูลหรือระบบ: '{match.group(0)}' (ระบบไม่อนุญาต)"

    # Handle LIMIT clause
    limit_match = re.search(r"\bLIMIT\s+(\d+)(?:\s*,\s*(\d+))?", cleaned, re.IGNORECASE)
    if limit_match:
        # Check limit size
        limit_val = int(limit_match.group(2) if limit_match.group(2) else limit_match.group(1))
        if limit_val > MAX_QUERY_LIMIT:
            # Clamp limit to MAX_QUERY_LIMIT
            if limit_match.group(2):
                offset = limit_match.group(1)
                cleaned = re.sub(
                    r"\bLIMIT\s+\d+\s*,\s*\d+",
                    f"LIMIT {offset}, {MAX_QUERY_LIMIT}",
                    cleaned,
                    flags=re.IGNORECASE
                )
            else:
                cleaned = re.sub(
                    r"\bLIMIT\s+\d+",
                    f"LIMIT {MAX_QUERY_LIMIT}",
                    cleaned,
                    flags=re.IGNORECASE
                )
    else:
        # Append default limit to protect server memory and performance
        cleaned = f"{cleaned} LIMIT {DEFAULT_QUERY_LIMIT}"

    return True, cleaned, ""
