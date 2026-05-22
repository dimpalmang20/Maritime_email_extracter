"""
Maritime-specific quantity, cargo, port, and rate parsing (precision-first).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from extraction.dataset_index import get_dataset_index
from extraction.knowledge_base import CARGO_KEYWORDS, CARGO_SYNONYMS, PORT_KEYWORDS
from extraction.semantic_rules import (
    has_invalid_cargo_context,
    has_valid_cargo_context,
    has_valid_quantity_context,
    is_blacklisted_cargo,
    is_vessel_spec_text,
)

_MT_CTX = re.compile(r"(?i)\b(?:mt|mts|tons?|tonnes?|metric\s*tons?|dwt)\b")
_QTY_RANGE = re.compile(
    r"(?i)(?:^|\s)(\d{1,3})[\s\-']*(\d{1,3}(?:[,\.'\s]\d{3})?)\s*(?:mt|mts|tons?|metric\s*tons?)\b"
)
_QTY_SINGLE = re.compile(
    r"(?<!\d)(?:^|\s)(\d{1,3}(?:[.,'\s]\d{3})+|\d{4,6})(?!\d)\s*(?:\+-?\s*\d+\s*%)?\s*(?:mt|mts|tons?|metric\s*tons?)\b|"
    r"(?<!\d)(\d{4,6})(?!\d)\s*MT\b",
    re.IGNORECASE,
)
_QTY_COMPACT_MT = re.compile(r"(?i)(?<!\d)(\d{3,6})MT(?!\w)")
_QTY_K_CARGO = re.compile(
    r"(?i)\b(\d{1,3})\s*k\s+([a-z][a-z0-9\s\-]{2,50})\b"
)
_CARGO_BEFORE_QTY_K = re.compile(
    r"(?i)\b([a-z][a-z0-9\s\-]{2,40}?)\s+(\d{1,3})\s*k\b"
)
_QTY_BEFORE_CARGO = re.compile(
    r"(?i)^\s*(\d{1,3}(?:[.,'\s]\d{3})*)\s*(?:mt|mts)?\s+([a-z][a-z0-9\s\-]{2,40})$"
)
_CARGO_AFTER_QTY_INLINE = re.compile(
    r"(?i)\b(\d{1,3}(?:[.,'\s]\d{3})*)\s*(?:mt|mts)?\s+([a-z][a-z0-9\s\-]{2,60})\b"
)
_COMMODITY_BLOCK = re.compile(
    r"(?i)commodity\s*:?\s*\n((?:[a-z][a-z0-9\s\-]{2,40}\n?)+)"
)
_RATE_SLASH = re.compile(r"(?i)\b(\d{3,6})\s*/\s*(\d{3,6})\b")
_TOLERANCE = re.compile(r"(?i)(\+-?\s*\d+\s*%)")
_LP_LINE = re.compile(
    r"(?im)^\s*(?:lp|pol|loading\s*port)\s*[:\-]?\s*(.+?)\s*$"
)
_DP_LINE = re.compile(
    r"(?im)^\s*(?:dp|pod|discharge\s*port|disch\s*port)\s*[:\-]?\s*(.+?)\s*$"
)
_LP_INLINE = re.compile(
    r"(?i)\b(?:lp|pol|loading\s*port)\s*[:\-]?\s*(.+?)(?=\s+\b(?:dp|pod|discharge\s*port|disch\s*port|laycan|qty|quantity|cargo)\b|\n|$)"
)
_DP_INLINE = re.compile(
    r"(?i)\b(?:dp|pod|discharge\s*port|disch\s*port)\s*[:\-]?\s*(.+?)(?=\s+\b(?:lp|pol|loading\s*port|laycan|qty|quantity|cargo)\b|\n|$)"
)

_ROUTE_FROM_TO = re.compile(
    r"(?i)\bfrom\s+([a-z][a-z\s\-]{2,40}?)\s+to\s+([a-z][a-z\s\-]{2,40}?)(?=\s|$|[.,;])"
)

_CARGO_STOP_WORDS = re.compile(
    r"(?i)\b(?:in\s+bulk|bulk|lp|pol|dp|pod|laycan|delivery|redelivery|duration|wog|ttl|adc|"
    r"loading|discharging|from|to|via|abt|about|metric\s*tons?|tons?|mts?|mt)\b.*$"
)


def normalize_maritime_number(raw: str) -> Optional[int]:
    if not raw:
        return None
    s = str(raw).strip().lower()
    s = s.replace("'", "").replace(" ", "")
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        return int(s.replace(".", ""))
    if "," in s and "." not in s:
        s = s.replace(",", "")
    elif "." in s and "," not in s:
        parts = s.split(".")
        if len(parts) == 2 and len(parts[1]) == 3:
            s = s.replace(".", "")
        elif len(parts) == 2 and len(parts[1]) <= 2:
            s = parts[0] + parts[1]
    s = re.sub(r"[^\d]", "", s)
    if not s.isdigit():
        return None
    v = int(s)
    return v if 1000 <= v <= 500000 else None


def expand_cargo_synonym(name: str) -> str:
    if not name:
        return name
    low = _CARGO_STOP_WORDS.sub("", name.lower().strip())
    low = re.sub(r"[^a-z0-9\s\-]", " ", low)
    low = re.sub(r"\s+", " ", low).strip()
    if low in CARGO_SYNONYMS:
        return CARGO_SYNONYMS[low].title()
    for key in sorted(CARGO_SYNONYMS, key=len, reverse=True):
        if len(key) < 2:
            continue
        pat = rf"(?i)\b{re.escape(key)}\b"
        if re.search(pat, low):
            low = re.sub(pat, CARGO_SYNONYMS[key], low, count=1)
            break
    return low.title()


def _clean_cargo_candidate(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    raw = re.sub(r"(?i)^(?:cargo|commodity|commodit)\s*[:\-]\s*", "", str(raw)).strip()
    if is_blacklisted_cargo(raw):
        return None
    cleaned = expand_cargo_synonym(raw)
    cleaned = re.sub(r"(?i)\b(?:In Bulk|Bulk)\b", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -")
    if len(cleaned) < 3:
        return None
    if has_invalid_cargo_context(raw, 0, len(raw)):
        return None
    if is_blacklisted_cargo(cleaned) or cleaned.lower() in {"cargo", "commodity", "lawfuls", "steels gens lawfuls"}:
        return None
    known = []
    low = cleaned.lower()
    for kw in sorted(CARGO_KEYWORDS, key=len, reverse=True):
        canonical = expand_cargo_synonym(kw)
        if re.search(rf"(?i)\b{re.escape(kw)}\b", low) or canonical.lower() in low:
            known.append(canonical)
    if known:
        return max(known, key=len)
    return cleaned


def _split_port_alternatives(raw: str) -> List[str]:
    raw = re.split(
        r"(?i)\b(?:lp|pol|dp|pod|loading\s*port|discharge\s*port|disch\s*port|laycan|qty|quantity|"
        r"cargo|commodity|dwt|open|delivery|redelivery|duration|ttl|adc|wog|shinc|shex)\b",
        raw or "",
        1,
    )[0]
    parts = re.split(r"(?i)\s+or\s+|/|,|&|\band\b", raw)
    out = []
    idx = get_dataset_index()
    for p in parts:
        p = p.strip()
        if len(p) < 3:
            continue
        resolved = idx.resolve_port(p)
        if resolved:
            out.append(resolved)
        else:
            for known in sorted(PORT_KEYWORDS, key=len, reverse=True):
                if known in p.lower():
                    out.append(known.title())
                    break
    return out


def extract_labeled_ports(text: str) -> Tuple[List[str], List[str]]:
    load_ports: List[str] = []
    discharge_ports: List[str] = []
    for pat in (_LP_LINE, _LP_INLINE):
        for m in pat.finditer(text):
            load_ports.extend(_split_port_alternatives(m.group(1)))
    for pat in (_DP_LINE, _DP_INLINE):
        for m in pat.finditer(text):
            discharge_ports.extend(_split_port_alternatives(m.group(1)))
    for m in _ROUTE_FROM_TO.finditer(text):
        load_ports.extend(_split_port_alternatives(m.group(1)))
        discharge_ports.extend(_split_port_alternatives(m.group(2)))
    seen_lp, seen_dp = set(), set()
    lp_u, dp_u = [], []
    for p in load_ports:
        k = p.lower()
        if k not in seen_lp:
            seen_lp.add(k)
            lp_u.append(p)
    for p in discharge_ports:
        k = p.lower()
        if k not in seen_dp:
            seen_dp.add(k)
            dp_u.append(p)
    return lp_u, dp_u


def extract_commodity_lines(text: str) -> List[str]:
    cargoes: List[str] = []
    m = _COMMODITY_BLOCK.search(text)
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            cargo = _clean_cargo_candidate(line)
            if cargo:
                cargoes.append(cargo)
        return cargoes
    for kw in sorted(CARGO_KEYWORDS, key=len, reverse=True):
        for m in re.finditer(rf"(?i)\b{re.escape(kw)}\b", text):
            if has_invalid_cargo_context(text, m.start(), m.end()):
                continue
            if not has_valid_cargo_context(text, m.start(), m.end()):
                continue
            cargo = _clean_cargo_candidate(kw)
            if cargo:
                cargoes.append(cargo)
            break
    return cargoes


def _dedupe_quantity_pairs(pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prefer highest quantity per cargo; drop bare duplicates."""
    by_cargo: Dict[Optional[str], Dict[str, Any]] = {}
    for p in pairs:
        cargo_key = (p.get("cargo_name") or "").lower() or None
        qty = p.get("quantity")
        if qty is None:
            continue
        prev = by_cargo.get(cargo_key)
        if not prev or qty > prev.get("quantity", 0):
            by_cargo[cargo_key] = p
    out = list(by_cargo.values())
    if None in by_cargo and len(out) > 1:
        out = [p for p in out if p.get("cargo_name")]
        if not out:
            out = [max(by_cargo.values(), key=lambda x: x.get("quantity") or 0)]
    return out


def extract_quantity_cargo_pairs(text: str) -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []
    seen = set()
    vessel_spec = is_vessel_spec_text(text)

    for m in _QTY_COMPACT_MT.finditer(text):
        if vessel_spec and not has_valid_quantity_context(text, m.start(), m.end()):
            continue
        qty = normalize_maritime_number(m.group(1))
        tail = text[m.end() : m.end() + 60]
        cargo_m = re.search(r"(?i)\b([A-Z]{2,8}(?:\s+[A-Z]{2,8})*)\b", tail)
        cargo = _clean_cargo_candidate(cargo_m.group(1)) if cargo_m else None
        if qty:
            key = (qty, cargo)
            if key not in seen:
                seen.add(key)
                pairs.append({"quantity": qty, "cargo_name": cargo, "quantity_unit": "MT"})

    for m in _QTY_K_CARGO.finditer(text):
        if vessel_spec and not has_valid_quantity_context(text, m.start(), m.end()):
            continue
        tail = m.group(2)
        if re.search(r"(?i)\b(?:dwt|open|built|blt|vessel|mv|m/v|hmax|handy|max|supra|ultra|panamax)\b", tail):
            continue
        qty = int(m.group(1)) * 1000
        cargo = _clean_cargo_candidate(tail)
        if qty and cargo:
            key = (qty, cargo)
            if key not in seen:
                seen.add(key)
                pairs.append({"quantity": qty, "cargo_name": cargo, "quantity_unit": "MT"})

    for m in _CARGO_BEFORE_QTY_K.finditer(text):
        if vessel_spec and not has_valid_quantity_context(text, m.start(), m.end()):
            continue
        head = m.group(1)
        if re.search(r"(?i)\b(?:dwt|open|built|blt|vessel|mv|m/v|hmax|handy|max|supra|ultra|panamax)\b", head):
            continue
        qty = int(m.group(2)) * 1000
        cargo = _clean_cargo_candidate(head)
        if qty and cargo:
            key = (qty, cargo)
            if key not in seen:
                seen.add(key)
                pairs.append({"quantity": qty, "cargo_name": cargo, "quantity_unit": "MT"})

    for m in _QTY_RANGE.finditer(text):
        if vessel_spec and not has_valid_quantity_context(text, m.start(), m.end()):
            continue
        hi = normalize_maritime_number(m.group(2))
        cargo_tail = text[m.end() : m.end() + 80]
        cargo_m = re.search(r"(?i)\b([a-z][a-z0-9\s\-]{2,45})\b", cargo_tail)
        cargo = _clean_cargo_candidate(cargo_m.group(1)) if cargo_m else None
        if hi:
            key = (hi, cargo)
            if key not in seen:
                seen.add(key)
                pairs.append({"quantity": hi, "cargo_name": cargo, "quantity_unit": "MT"})

    for m in _QTY_SINGLE.finditer(text):
        line_start = text.rfind("\n", 0, m.start()) + 1
        line = text[line_start:m.end()+40]

        if re.match(r"^\s*\d+\.", line):
          continue

        if re.match(r"^\s*[A-Z]+\)", line):
           continue

        if m.group(1) and int(re.sub(r"\D", "", m.group(1))) < 1000:
           continue


        if not has_valid_quantity_context(text, m.start(), m.end()):
            continue
        qty = normalize_maritime_number(m.group(1))
        if qty:
            key = (qty, None)
            if key not in seen:
                seen.add(key)
                pairs.append({"quantity": qty, "cargo_name": None, "quantity_unit": "MT"})

    for m in _CARGO_AFTER_QTY_INLINE.finditer(text):
        if vessel_spec and not has_valid_quantity_context(text, m.start(), m.end()):
            continue
        qty = normalize_maritime_number(m.group(1))
        cargo = _clean_cargo_candidate(m.group(2).strip())
        if qty and cargo:
            key = (qty, cargo)
            if key not in seen:
                seen.add(key)
                pairs.append({"quantity": qty, "cargo_name": cargo, "quantity_unit": "MT"})

    m = re.search(r"(?i)^\s*(\d+)\s*MT\s+([A-Z][A-Z0-9\s]+)$", text.strip(), re.M)
    if m:
        qty = normalize_maritime_number(m.group(1))
        cargo = _clean_cargo_candidate(m.group(2))
        if qty:
            key = (qty, cargo)
            if key not in seen:
                seen.add(key)
                pairs.append({"quantity": qty, "cargo_name": cargo, "quantity_unit": "MT"})

    return _dedupe_quantity_pairs(pairs)


def extract_rates_and_tolerance(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"load_rate": None, "discharge_rate": None, "tolerance": None}
    m = _RATE_SLASH.search(text)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if 500 <= a <= 50000 and 500 <= b <= 50000:
            out["load_rate"] = a
            out["discharge_rate"] = b
    tol = _TOLERANCE.search(text)
    if tol:
        out["tolerance"] = tol.group(1).replace(" ", "")
    return out


def enrich_block_parse(block: str) -> Dict[str, Any]:
    """Single-pass maritime enrichment for one block."""
    text = block or ""
    qty_pairs = extract_quantity_cargo_pairs(text)
    lp_list, dp_list = extract_labeled_ports(text)
    commodities = extract_commodity_lines(text)
    rates = extract_rates_and_tolerance(text)

    legs: List[Dict[str, Any]] = []
    n = max(len(qty_pairs), len(commodities), 1)
    if not qty_pairs and not commodities and not lp_list:
        n = 0

    for i in range(n):
        qp = qty_pairs[i] if i < len(qty_pairs) else (qty_pairs[0] if qty_pairs else {})
        cargo = commodities[i] if i < len(commodities) else qp.get("cargo_name")
        if not cargo and commodities:
            cargo = commodities[0]
        legs.append(
            {
                "cargo_name": cargo,
                "quantity": qp.get("quantity"),
                "quantity_unit": "MT",
                "load_port": lp_list[i] if i < len(lp_list) else (lp_list[0] if lp_list else None),
                "discharge_port": dp_list[i] if i < len(dp_list) else (dp_list[0] if dp_list else None),
            }
        )

    if not legs and (lp_list or commodities):
        legs.append(
            {
                "cargo_name": commodities[0] if commodities else None,
                "quantity": qty_pairs[0]["quantity"] if qty_pairs else None,
                "quantity_unit": "MT",
                "load_port": ", ".join(lp_list) if len(lp_list) > 1 else (lp_list[0] if lp_list else None),
                "discharge_port": dp_list[0] if dp_list else None,
            }
        )

    return {
        "cargo_legs_hint": legs,
        "load_ports": lp_list,
        "discharge_ports": dp_list,
        "commodities": commodities,
        "quantity_pairs": qty_pairs,
        **rates,
    }
