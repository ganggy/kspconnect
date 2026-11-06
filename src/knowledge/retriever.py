"""Local Knowledge Base Retriever for HOSxP and Hospital Documentation."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import KNOWLEDGE_BASE_DIR

# Known primary tables and their corresponding file paths
TABLE_FILE_MAP = {
    "patient": "01-patient/patient.md",
    "patient_address": "01-patient/patient-address.md",
    "thaiaddress": "01-patient/patient-address.md",
    "pttype": "01-patient/patient-pttype.md",
    "ovst": "02-opd/ovst.md",
    "opdscreen": "02-opd/opdscreen.md",
    "ovstdiag": "02-opd/ovstdiag.md",
    "ipt": "03-ipd/ipt.md",
    "iptdiag": "03-ipd/iptdiag.md",
    "iptbedmove": "03-ipd/iptbedmove.md",
    "drugitems": "04-drug/drugitems.md",
    "opitemrece": "04-drug/opitemrece.md",
    "lab_head": "06-lab/lab-head.md",
    "lab_items": "06-lab/lab-items.md",
    "lab_order": "06-lab/lab-order.md",
    "finance": "05-finance/finance-deposit.md",
}


class KnowledgeRetriever:
    """Retriever for HOSxP schemas, dictionaries, and common queries."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or KNOWLEDGE_BASE_DIR
        self._cache: Dict[str, str] = {}
        self._load_all_files()

    def _load_all_files(self):
        if not self.base_dir.exists():
            return
        for path in self.base_dir.rglob("*.md"):
            try:
                rel_path = path.relative_to(self.base_dir).as_posix()
                content = path.read_text(encoding="utf-8", errors="replace")
                self._cache[rel_path] = content
            except Exception:
                pass

    def list_modules(self) -> List[Dict[str, Any]]:
        """List all available knowledge categories and files."""
        categories: Dict[str, List[str]] = {}
        for rel_path in sorted(self._cache.keys()):
            parts = rel_path.split("/")
            category = parts[0] if len(parts) > 1 else "root"
            categories.setdefault(category, []).append(rel_path)

        return [{"category": k, "files": v} for k, v in categories.items()]

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema and documentation for a specific HOSxP table."""
        name_clean = table_name.lower().strip()
        matched_file = TABLE_FILE_MAP.get(name_clean)

        if not matched_file:
            # Fallback search by filename
            for rel_path in self._cache.keys():
                if f"/{name_clean}.md" in rel_path or rel_path == f"{name_clean}.md":
                    matched_file = rel_path
                    break

        if matched_file and matched_file in self._cache:
            return {
                "found": True,
                "table_name": name_clean,
                "file": matched_file,
                "content": self._cache[matched_file],
            }

        return {
            "found": False,
            "table_name": name_clean,
            "message": f"ไม่พบเอกสาร Schema สำหรับตาราง '{table_name}' ใน Knowledge Base",
            "available_tables": list(TABLE_FILE_MAP.keys()),
        }

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search markdown files using token-based keyword relevance scoring."""
        query_tokens = [t.lower() for t in query.split() if len(t) > 1]
        if not query_tokens:
            return []

        scored_results = []
        for rel_path, content in self._cache.items():
            content_lower = content.lower()
            score = 0
            
            # Match tokens
            for token in query_tokens:
                count = content_lower.count(token)
                if token in rel_path.lower():
                    score += 15  # Path or filename hit is high signal
                if f"# {token}" in content_lower or f"## {token}" in content_lower:
                    score += 10
                score += min(count, 10)  # Frequency capped at 10

            if score > 0:
                # Extract first matching snippet
                snippet = ""
                for line in content.splitlines():
                    if any(t in line.lower() for t in query_tokens):
                        snippet = line.strip()
                        break
                if not snippet and content:
                    snippet = content.splitlines()[0]

                scored_results.append({
                    "file": rel_path,
                    "score": score,
                    "snippet": snippet[:200],
                    "content": content,
                })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]

    def get_relationships(self) -> Dict[str, Any]:
        """Get ER relationship documentation between patient, OPD, IPD, and opitemrece."""
        overview = self._cache.get("relationships/opitemrece-overview.md", "")
        patient_flow = self._cache.get("relationships/patient-opd-ipd.md", "")
        return {
            "opitemrece_overview": overview,
            "patient_flow": patient_flow,
        }


# Global singleton instance
retriever = KnowledgeRetriever()
