"""MySQL Database Connection Manager for HOSxP."""

import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
import pymysql
import pymysql.cursors
from src.config import (
    HOS_DB_HOST,
    HOS_DB_PORT,
    HOS_DB_USER,
    HOS_DB_PASSWORD,
    HOS_DB_NAME,
    HOS_DB_TIMEOUT,
)


def _serialize_value(val: Any) -> Any:
    """Serialize database types to JSON-friendly primitives with robust Thai text handling."""
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.isoformat()
    elif isinstance(val, datetime.time):
        return str(val)
    elif isinstance(val, Decimal):
        return float(val)
    elif isinstance(val, bytes):
        try:
            return val.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return val.decode("cp874")
            except Exception:
                return val.decode("utf-8", errors="replace")
    return val


def get_db_connection() -> pymysql.Connection:
    """Establish and return a new MySQL connection with utf8mb4 charset."""
    return pymysql.connect(
        host=HOS_DB_HOST,
        port=HOS_DB_PORT,
        user=HOS_DB_USER,
        password=HOS_DB_PASSWORD,
        database=HOS_DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=HOS_DB_TIMEOUT,
        read_timeout=HOS_DB_TIMEOUT,
        autocommit=True,
    )


def check_db_health() -> Dict[str, Any]:
    """Check database connectivity status."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS status, NOW() AS server_time, VERSION() AS version")
            row = cursor.fetchone()
        conn.close()
        return {
            "connected": True,
            "host": HOS_DB_HOST,
            "database": HOS_DB_NAME,
            "server_time": _serialize_value(row["server_time"]),
            "mysql_version": row["version"],
        }
    except Exception as e:
        return {
            "connected": False,
            "host": HOS_DB_HOST,
            "database": HOS_DB_NAME,
            "error": str(e),
        }


def execute_raw_query(sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """Execute a validated read-only SQL query and return rows as list of dicts."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            serialized_rows = []
            for row in rows:
                serialized_rows.append({k: _serialize_value(v) for k, v in row.items()})
            return serialized_rows
    finally:
        conn.close()
