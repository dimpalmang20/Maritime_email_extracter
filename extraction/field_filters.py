"""Strict filtering for phones, ports, quantities, vessel names (precision-first)."""
from __future__ import annotations

import re
from typing import List, Optional

from extraction.dataset_index import get_dataset_index

# Patterns that must NEVER be treated as phone numbers
_NOT_PHONE = re.compile(
    r"(?i)(?:"
    r"^\d{1,3}[\s\-']+\d{3,6}$|"
    r"^\d{4,6}\s*/\s*\d{4,6}$|"
    r"^\d{1,3}(?:[.,'\s]\d{3})+\s*(?:\+-|\+\/-)?\s*\d+\s*%|"
    r"^\d{4,6}\s*\+-?\s*\d+|"
    r"mt|mts|tons?|metric|ferts?|dwt|laycan"
    r")"
)

_PHONE_STRICT = re.compile(
    r"""
    (?:
        (?<!\d)
        (?:\+\d{1,3}[\s\-]?)?
        (?:\(?\d{2,4}\)?[\s\-]?)?
        \d{3,5}[\s\-]?\d{4,8}
        (?!\d)
    )
    """,
    re.VERBOSE,
)


def is_phone_candidate(s: str, block_text: str = "") -> bool:

    raw = (s or "").strip()

    if not raw:
        return False

    if "\n" in raw:
        return False

    if len(raw) > 25:
        return False

    if re.search(r"(?i)(mt|mts|tons|dwt|laycan|qty|quantity)", raw):
        return False

    if "/" in raw and not raw.startswith("+"):
        return False

    if re.search(r"\d{1,2}\-\d{1,3}[,' ]?\d{3}", raw):
        return False

    digits = re.sub(r"\D", "", raw)

    if re.search(r"\d{1,2}:\d{2}", raw):
        return False

    if re.search(r"\b20\d{2}\b", raw):
        return False

    if len(digits) < 10:
        return False

    if len(digits) < 10:
        return False

    if len(set(digits)) <= 3:
        return False

    if re.search(r"(?i)\b(?:imo|dwt|grt|nrt)\b", block_text):
        nearby = block_text.lower().find(raw.lower())

        if nearby >= 0:
            ctx = block_text[max(0, nearby - 40): nearby + 40].lower()

            if re.search(r"(imo|dwt|grt|nrt)", ctx):
                return False

    return True


def extract_phone_strict(text: str) -> List[str]:
    """Extract only realistic phone strings; never tonnage/rates."""
    if not text:
        return []
    candidates: List[str] = []
    for line in text.splitlines():
        if re.search(r"(?i)\b(?:tel|mobile|phone|fax|mob|contact)\b", line) or "+" in line:
            candidates.extend(_PHONE_STRICT.findall(line))
    candidates.extend(_PHONE_STRICT.findall(text))
    return filter_phone_numbers(candidates, text)


def filter_phone_numbers(candidates: List[str], block_text: str) -> List[str]:
    if not candidates:
        return []
    idx = get_dataset_index()
    imo_digits = set()
    for m in re.finditer(r"imo[\s:\-]*(\d{7})\b", block_text or "", re.I):
        imo_digits.add(m.group(1))

    out: List[str] = []
    seen = set()
    for raw in candidates:
        if not is_phone_candidate(raw, block_text):
            continue
        s = raw.strip()
        digits = re.sub(r"\D", "", s)
        # reject dates/timestamps
        if re.search(
            r"\b(?:19|20)\d{2}\b",
            raw,
        ):
          return False

        if ":" in raw:
           return False

        if re.search(r"\b(?:am|pm)\b", raw, re.I):
           return False
        if digits in imo_digits or idx.digits_are_imo_context(digits, block_text):
            continue
        if re.search(r"(?i)\b(?:grain|capacity|cbft|dwt|imo|laycan|mts|mt)\b", s):
            continue
        pos = (block_text or "").lower().find(s.lower()[:10])
        if pos >= 0:
            line_start = (block_text or "").rfind("\n", 0, pos) + 1
            line_end = (block_text or "").find("\n", pos)
            if line_end < 0:
                line_end = len(block_text or "")
            ctx = (block_text or "")[line_start:line_end]
            if re.search(r"(?i)\b(?:mt|mts|tons?|metric|ferts|quantity|cargo)\b", ctx):
                continue
        key = digits[:15]
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out


def sanitize_port_value(port: Optional[str]) -> Optional[str]:
    if not port:
        return None
    if len(str(port).strip()) < 4:
     return None

    if re.fullmatch(r"[A-Z]", str(port).strip()):
     return None
    idx = get_dataset_index()
    if "," in str(port):
        parts = [idx.resolve_port(p.strip()) for p in str(port).split(",")]
        parts = [p for p in parts if p]
        return ", ".join(parts) if parts else None
    return idx.resolve_port(str(port))


def sanitize_vessel_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    idx = get_dataset_index()
    n = str(name).strip()
    if idx.is_plausible_vessel_name(n):
        return n
    return None


def sanitize_quantity_value(qty) -> Optional[int]:
    if qty is None or qty == "":
        return None
    idx = get_dataset_index()
    try:
        v = int(str(qty).replace(",", ""))
    except (TypeError, ValueError):
        return None
    if idx.is_plausible_cargo_quantity(v):
        return v
    return None
