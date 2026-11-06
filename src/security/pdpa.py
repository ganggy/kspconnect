"""PDPA & Healthcare Privacy Data Masking Engine."""

import re
from typing import Any, Dict, List, Union

CID_KEYS = {"cid", "idcard", "card_id", "passport_no", "id_card"}
NAME_KEYS = {"fname", "lname", "full_name", "patient_name", "informname", "fathername", "mathername", "spsname"}
PHONE_KEYS = {"tel", "phone", "hometel", "informtel", "worktel", "mobile_phone_number"}
ADDR_KEYS = {"informaddr", "workaddr"}


def mask_cid(val: str) -> str:
    """Mask citizen identification number (e.g. 1-2345-XXXXX-89-0)."""
    if not val:
        return ""
    digits = re.sub(r"\D", "", str(val))
    if len(digits) == 13:
        return f"{digits[:1]}-{digits[1:5]}-XXXXX-{digits[10:12]}-{digits[12]}"
    elif len(digits) > 4:
        return f"{digits[:2]}XXXXX{digits[-2:]}"
    return "****"


def mask_name(val: str) -> str:
    """Mask personal name preserving first and last char."""
    if not val:
        return ""
    val_str = str(val).strip()
    if len(val_str) <= 2:
        return f"{val_str[:1]}*"
    return f"{val_str[0]}{'*' * (len(val_str) - 2)}{val_str[-1]}"


def mask_phone(val: str) -> str:
    """Mask telephone number (e.g. 081-XXX-5678)."""
    if not val:
        return ""
    digits = re.sub(r"\D", "", str(val))
    if len(digits) >= 9:
        return f"{digits[:3]}-XXX-{digits[-4:]}"
    return "***-****"


def mask_address(val: str) -> str:
    """Mask specific street / house numbers in address text."""
    if not val:
        return ""
    return "[ที่อยู่ถูกระงับการแสดงผลเพื่อความคุ้มครองข้อมูลส่วนบุคคล]"


def mask_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Mask a single dictionary record containing patient data."""
    masked: Dict[str, Any] = {}
    for k, v in record.items():
        k_lower = k.lower()
        if v is None:
            masked[k] = None
        elif any(cid_k in k_lower for cid_k in CID_KEYS):
            masked[k] = mask_cid(str(v))
        elif any(name_k in k_lower for name_k in NAME_KEYS):
            masked[k] = mask_name(str(v))
        elif any(phone_k in k_lower for phone_k in PHONE_KEYS):
            masked[k] = mask_phone(str(v))
        elif any(addr_k in k_lower for addr_k in ADDR_KEYS):
            masked[k] = mask_address(str(v))
        else:
            masked[k] = v
    return masked


def mask_dataset(data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Recursively mask datasets for PDPA compliance."""
    if isinstance(data, list):
        return [mask_record(r) if isinstance(r, dict) else r for r in data]
    elif isinstance(data, dict):
        return mask_record(data)
    return data
