"""Semantic validation rules for enterprise maritime extraction."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Optional

from extraction.knowledge_base import STRICT_CARGO_BLACKLIST

INVALID_CARGO_CONTEXT = (
    "grain capacity",
    "bale capacity",
    "hold",
    "holds",
    "cbm",
    "hatch",
    "ho/ha",
    "capacity",
    "gear",
    "grab",
    "crane",
    "specification",
    "adcom",
    "address commission",
    "period",
    "vessel type",
)

VALID_QUANTITY_CONTEXT = (
    "mt",
    "mts",
    "metric tons",
    "quantity",
    "qty",
    "cargo",
    "shipment",
    "lot",
    "parcel",
)

INVALID_QUANTITY_CONTEXT = (
    "grt",
    "nrt",
    "loa",
    "beam",
    "draft",
    "cbm",
    "grain capacity",
    "bale capacity",
)

INVALID_ENTITY_WORDS = {
    "the",
    "which",
    "good",
    "safe",
    "weather",
    "apply",
    "master",
    "speed",
    "about",
    "details",
    "conditions",
}

VESSEL_TYPE_MAP = {
    "bulk carrier": "Bulk Carrier",
    "geared bulk carrier": "Bulk Carrier",
    "single deck bulk carrier": "Bulk Carrier",
    "logger": "Logger Bulk Carrier",
    "supramax": "Supramax",
    "supra": "Supramax",
    "smx": "Supramax",
    "ultramax": "Ultramax",
    "umx": "Ultramax",
    "umax": "Ultramax",
    "handysize": "Handysize",
    "handymax": "Handymax",
    "hmax": "Handymax",
    "panamax": "Panamax",
    "kamsarmax": "Kamsarmax",
    "capesize": "Capesize",
}

_VESSEL_SPEC_SIGNAL = re.compile(
    r"(?i)\b(?:imo|dwt|grt|nrt|loa|beam|built|flag|class|gear|grabs?|cranes?|"
    r"grain\s+capacity|bale\s+capacity|ho/ha|hatch|holds?|bulk\s+carrier)\b"
)

_MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def window(text: str, start: int, end: int, size: int = 45) -> str:
    return (text or "")[max(0, start - size) : min(len(text or ""), end + size)].lower()


def has_invalid_cargo_context(text: str, start: int = 0, end: int = 0) -> bool:
    ctx = window(text, start, end, 55)
    return any(term in ctx for term in INVALID_CARGO_CONTEXT)


def is_blacklisted_cargo(value: str) -> bool:
    cleaned = re.sub(r"[^a-z\s]", " ", str(value or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned in STRICT_CARGO_BLACKLIST


def has_valid_cargo_context(text: str, start: int = 0, end: int = 0) -> bool:
    ctx = window(text, start, end, 80)
    if any(term in ctx for term in INVALID_CARGO_CONTEXT):
        return False
    return bool(
        re.search(
            r"(?i)\b(?:cargo|commodity|bulk|shipment|parcel|lot|qty|quantity|mt|mts|"
            r"metric\s+tons?|pol|pod|lp|dp|load(?:ing)?|discharge|from|to|"
            r"tct|trip|time\s+charter)\b",
            ctx,
        )
    )


def has_valid_quantity_context(text: str, start: int = 0, end: int = 0) -> bool:
    ctx = window(text, start, end, 45)
    if any(term in ctx for term in INVALID_QUANTITY_CONTEXT):
        return False
    return any(term in ctx for term in VALID_QUANTITY_CONTEXT)


def is_vessel_spec_text(text: str) -> bool:
    t = text or ""
    hits = len(_VESSEL_SPEC_SIGNAL.findall(t))
    has_identity = bool(re.search(r"(?i)\b(?:mv|m/v|vessel\s+name|imo|dwt)\b", t))
    has_dimensions = bool(re.search(r"(?i)\b(?:grt|nrt|loa|beam|grain\s+capacity|bale\s+capacity)\b", t))
    return hits >= 3 and (has_identity or has_dimensions)


def normalize_vessel_type(text: str, current: Optional[str] = None) -> str:
    raw = f"{current or ''} {text or ''}".lower()
    for key, value in sorted(VESSEL_TYPE_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"\b{re.escape(key)}\b", raw):
            return value
    return current or "Unknown Vessel"


def _iso_date(day: int, month: int, year: Optional[int] = None) -> str:
    now = datetime.now()
    y = year or now.year
    try:
        return datetime(y, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return ""


def normalize_open_date(raw: str) -> str:
    text = (raw or "").strip().lower()
    if not text:
        return ""
    now = datetime.now()
    if re.search(r"\b(?:prompt|spot)\b", text):
        return "PROMPT"
    m = re.search(r"\b(end|mid|early)\s+([a-z]{3,9})(?:\s+(\d{4}))?\b", text)
    if m:
        anchor = {"early": 5, "mid": 15, "end": 28}[m.group(1)]
        month = _MONTHS.get(m.group(2)[:3]) or _MONTHS.get(m.group(2))
        if month:
            return _iso_date(anchor, month, int(m.group(3)) if m.group(3) else None)
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s*([a-z]{3,9})(?:[,\s]+(\d{4}))?\b", text)
    if m:
        month = _MONTHS.get(m.group(2)[:3]) or _MONTHS.get(m.group(2))
        if month:
            return _iso_date(int(m.group(1)), month, int(m.group(3)) if m.group(3) else None)
    return raw.strip()


def choose_email_and_template(data: Dict[str, Any], block_text: str = "") -> Dict[str, str]:
    

    """Priority classifier: TONNAGE/VESSEL first, then TC, then VC."""
    has_vessel = bool(data.get("vessel_name") or data.get("imo"))
    has_dwt = bool(data.get("dwt"))
    has_open = bool(data.get("open_port") or data.get("open_date") or re.search(r"(?i)\b(?:open|spot|prompt)\b", block_text or ""))
    has_tc = bool(data.get("delivery") or data.get("redelivery") or data.get("duration"))
    has_vc = bool(data.get("cargo") and data.get("quantity") and (data.get("load_port") or data.get("discharge_port")))

    if (has_vessel and has_dwt and has_open) or (has_dwt and is_vessel_spec_text(block_text)):
        return {"email_type": "TONNAGE", "template_type": "TONNAGE"}
    
    tc_signals = len(re.findall(
    r"(?i)\b(tct|time charter|delivery|redelivery|duration|trip|period)\b",
    block_text or "",
     ))

    vc_signals = len(re.findall(
    r"(?i)\b(cargo|quantity|qty|load port|discharge|pol|pod)\b",
    block_text or "",
     ))

    if tc_signals >= 2:
       return {"email_type": "TC", "template_type": "TC"}

    if vc_signals >= 2:
        return {"email_type": "VC", "template_type": "VC"}
    if has_tc:
        return {"email_type": "TC", "template_type": "TC"}
    if has_vc:
        return {"email_type": "VC", "template_type": "VC"}
    if data.get("cargo") and not (data.get("quantity") or data.get("load_port") or data.get("discharge_port")):
        return {"email_type": "UNKNOWN", "template_type": "UNKNOWN"}
    return {
        "email_type": str(data.get("email_type") or "UNKNOWN"),
        "template_type": str(data.get("template_type") or "UNKNOWN"),
    }
