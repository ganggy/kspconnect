"""Configuration settings for KSP Connect Universal Hospital AI Gateway."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Database Configuration (HOSxP MySQL)
HOS_DB_HOST = os.getenv("HOS_DB_HOST", "192.168.2.254")
HOS_DB_PORT = int(os.getenv("HOS_DB_PORT", "3306"))
HOS_DB_USER = os.getenv("HOS_DB_USER", "opd")
HOS_DB_PASSWORD = os.getenv("HOS_DB_PASSWORD", "opd")
HOS_DB_NAME = os.getenv("HOS_DB_NAME", "hos")
HOS_DB_TIMEOUT = int(os.getenv("HOS_DB_TIMEOUT", "10"))

# Hospital Metadata (KSP)
HOSPITAL_NAME = os.getenv("HOSPITAL_NAME", "โรงพยาบาลเกษตรสมบูรณ์ (KSP)")
HOSPITAL_CODE = os.getenv("HOSPITAL_CODE", "10714")
HOSPITAL_BED_CAPACITY = int(os.getenv("HOSPITAL_BED_CAPACITY", "90"))

# Security & Governance
ENABLE_PDPA_MASKING = os.getenv("ENABLE_PDPA_MASKING", "true").lower() in ("true", "1", "yes")
DEFAULT_QUERY_LIMIT = int(os.getenv("DEFAULT_QUERY_LIMIT", "100"))
MAX_QUERY_LIMIT = int(os.getenv("MAX_QUERY_LIMIT", "500"))
API_KEY = os.getenv("KSP_API_KEY", "")

# Server Settings
REST_HOST = os.getenv("REST_HOST", "0.0.0.0")
REST_PORT = int(os.getenv("REST_PORT", "8000"))
MCP_PORT = int(os.getenv("MCP_PORT", "8001"))

# Paths
KNOWLEDGE_BASE_DIR = ROOT_DIR / "knowledge_base"
