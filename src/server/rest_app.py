"""FastAPI REST & OpenAPI Application for Hospital Intelligence Gateway."""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from src.config import (
    HOSPITAL_NAME,
    HOSPITAL_CODE,
    HOSPITAL_BED_CAPACITY,
    API_KEY,
)
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

# Initialize FastAPI App
app = FastAPI(
    title="KSP Hospital Intelligence Gateway API",
    description="Universal AI Skill and REST Gateway for KSP Hospital (HOSxP Database & Knowledge Base)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Optional API key verification if configured."""
    if API_KEY:
        if not credentials or credentials.credentials != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API Bearer Token")
    return True


# Models
class QueryRequest(BaseModel):
    sql_query: str = Field(..., description="Read-only SELECT SQL statement to execute", example="SELECT COUNT(*) FROM ovst WHERE vstdate = CURDATE()")


@app.get("/", tags=["General"])
def root():
    """Service status and greeting."""
    return {
        "service": "KSP Hospital Intelligence Gateway",
        "hospital": HOSPITAL_NAME,
        "status": "online",
        "docs": "/docs",
        "openapi_schema": "/openapi.json",
    }


@app.get("/api/v1/overview", tags=["Hospital Profile"], dependencies=[Depends(verify_api_key)])
def get_overview():
    """Get hospital profile, bed capacity, and live database health."""
    return {
        "hospital_name": HOSPITAL_NAME,
        "hospital_code": HOSPITAL_CODE,
        "bed_capacity": HOSPITAL_BED_CAPACITY,
        "his_system": "HOSxP (MySQL)",
        "database_health": check_db_health(),
    }


@app.get("/api/v1/knowledge/search", tags=["Knowledge Base"], dependencies=[Depends(verify_api_key)])
def search_knowledge(
    q: str = Query(..., description="Keywords to search in HOSxP documentation"),
    top_k: int = Query(3, ge=1, le=10, description="Max results"),
):
    """Search HOSxP tables, dictionary, and hospital guides."""
    return retriever.search(query=q, top_k=top_k)


@app.get("/api/v1/knowledge/schema/{table_name}", tags=["Knowledge Base"], dependencies=[Depends(verify_api_key)])
def get_table_schema(table_name: str):
    """Get comprehensive schema documentation for a HOSxP table."""
    res = retriever.get_table_schema(table_name)
    if not res["found"]:
        raise HTTPException(status_code=404, detail=res["message"])
    return res


@app.get("/api/v1/knowledge/relationships", tags=["Knowledge Base"], dependencies=[Depends(verify_api_key)])
def get_relationships():
    """Get Entity-Relationship notes between patient, OPD, IPD, and charges."""
    return retriever.get_relationships()


@app.get("/api/v1/reports/daily-summary", tags=["Live Reports"], dependencies=[Depends(verify_api_key)])
def daily_summary(date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (defaults to today)")):
    """Get daily hospital operations summary (OPD visits, IPD admits/discharges, active in-patients)."""
    return _get_daily_summary(date)


@app.get("/api/v1/reports/bed-occupancy", tags=["Live Reports"], dependencies=[Depends(verify_api_key)])
def bed_occupancy():
    """Get real-time inpatient bed occupancy breakdown by ward."""
    return _get_bed_occupancy()


@app.get("/api/v1/reports/top-diagnoses", tags=["Live Reports"], dependencies=[Depends(verify_api_key)])
def top_diagnoses(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(10, ge=1, le=50),
):
    """Get top OPD ICD-10 primary diagnoses."""
    return _get_top_diagnoses(start_date, end_date, limit)


@app.get("/api/v1/catalog/drugs", tags=["Catalogs"], dependencies=[Depends(verify_api_key)])
def search_drugs(
    keyword: str = Query(..., description="Medicine brand name or generic name"),
    limit: int = Query(20, ge=1, le=50),
):
    """Search hospital formulary catalog."""
    return _search_drugs(keyword, limit)


@app.get("/api/v1/catalog/labs", tags=["Catalogs"], dependencies=[Depends(verify_api_key)])
def search_labs(
    keyword: str = Query(..., description="Lab test name"),
    limit: int = Query(20, ge=1, le=50),
):
    """Search hospital lab test catalog."""
    return _search_labs(keyword, limit)


@app.post("/api/v1/query/execute", tags=["Safe SQL Execution"], dependencies=[Depends(verify_api_key)])
def execute_query(req: QueryRequest):
    """Execute custom read-only SQL query with automatic PDPA masking."""
    res = _execute_safe_query(req.sql_query)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["error"])
    return res
