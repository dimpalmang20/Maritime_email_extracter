"""
Pre-classify email segments before extraction.

Precision-first: only EXTRACTABLE_LABELS proceed to the parser pipeline.
"""
from __future__ import annotations

import re
from typing import Final, Tuple

from extraction.knowledge_base import CARGO_KEYWORDS
from extraction.semantic_rules import has_invalid_cargo_context, is_vessel_spec_text

# Business-relevant blocks only (TC/charter is not pure vessel/cargo but must extract).
EXTRACTABLE_LABELS: Final[frozenset[str]] = frozenset(
    {"VESSEL_OPEN", "CARGO_FIXTURE", "CHARTER_FIXTURE"}
)

_TECHNICAL_LINE = re.compile(
    r"(?im)^.*\b(?:"
    r"speed\s*(?:and|&)?\s*consumption|laden\s*consumption|ballast\s*consumption|"
    r"eco\s*speed|service\s*speed|main\s*engine|aux\s*engine|"
    r"bunker|hsfo|vlsfo|lsmgo|mgo|ifo|"
    r"ballast\s*water|bwts|tpc|tpi|draft|trim|"
    r"weather\s*working|weather\s*clause|"
    r"boiler\s*plate|boiler\s*clause|"
    r"without\s*prejudice|subject\s*to|wog\b|as\s*is|"
    r"disclaimer|indemnity|liability|governing\s*law|"
    r"cp\s*proforma|gencon|nype|"
    r"hold\s*\d|no\.?\s*\d\s*hold"
    r")\b.*$"
)

_NOISE_BOILER = re.compile(
    r"(?is)\b(?:"
    r"this\s+message\s+is\s+confidential|privileged\s+communication|"
    r"virus\s+free|intended\s+recipient|unauthorised\s+use|"
    r"please\s+consider\s+the\s+environment|"
    r"scanned\s+by|automatically\s+generated"
    r")\b"
)

_CARGO_SIGNAL = re.compile(
    r"(?i)\b(?:"
    r"cargo|commodity|parcel|qty|quantity|mts?\b|"
    r"\blp\b|\bpol\b|\bdp\b|\bpod\b|load\s*port|disch(?:arge)?\s*port|"
    r"freight|lumpsum|ws\b|l\/d\b|loading|discharging"
    r")\b"
)

_VESSEL_OPEN_SIGNAL = re.compile(
    r"(?i)\b(?:"
    r"\bmv\b|\bm/t\b|\bm\.v\.|vessel\s+name|vsl\b|"
    r"\bopen\b|\bopn\b|position\b|"
    r"\bdwt\b|\bbuilt\b|\bimo\b|\bgrt\b|\bnrt\b"
    r")\b"
)

_CHARTER_SIGNAL = re.compile(
    r"(?i)\b(?:"
    r"\btct\b|time\s*charter|delivery|redelivery|redel\b|duration|"
    r"wog\b|address\s*commission|\bttl\b|\badc\b"
    r")\b"
)


def classify_block(text: str) -> str:
    """
    Return one of:
      VESSEL_HEADER, CARGO_FIXTURE, CHARTER_FIXTURE,
      TECHNICAL_SPEC, SPEED_CONSUMPTION, BUNKER_CLAUSE, LEGAL_DISCLAIMER,
      SIGNATURE, CONTACT_SECTION, NOISE
    """
    if not text or not str(text).strip():
        return "NOISE"

    t = str(text).strip()
    low = t.lower()
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    n_lines = max(len(lines), 1)

    if _NOISE_BOILER.search(t):
        return "LEGAL_DISCLAIMER"

    # Signature / contact (short trailing blocks)
    if n_lines <= 4 and re.search(r"(?i)\b(mobile|tel|fax|skype|whatsapp)\b", low):
        if not _CARGO_SIGNAL.search(t) and not _VESSEL_OPEN_SIGNAL.search(t):
            return "CONTACT_SECTION"

    tech_line_hits = sum(1 for ln in lines if _TECHNICAL_LINE.search(ln))
    cargo_hits = len(_CARGO_SIGNAL.findall(t))
    for ck in CARGO_KEYWORDS:
        m = re.search(rf"(?i)\b{re.escape(ck)}\b", t)
        if m and not has_invalid_cargo_context(t, m.start(), m.end()):
            cargo_hits += 2
            break
    vessel_hits = len(_VESSEL_OPEN_SIGNAL.findall(t))
    charter_hits = len(_CHARTER_SIGNAL.findall(t))

    # Vessel specifications can contain words like cargo/grain/holds; vessel identity wins.
    if is_vessel_spec_text(t):
        return "VESSEL_OPEN"

    # Strong technical paragraph: many technical lines, no fixture anchors
    if tech_line_hits >= 2 and cargo_hits == 0 and charter_hits == 0 and vessel_hits <= 1:
        if re.search(r"(?i)\b(?:speed|consumption|laden|ballast)\b", low):
            return "SPEED_CONSUMPTION"
        if re.search(r"(?i)\b(?:bunker|hsfo|vlsfo|lsmgo|mgo)\b", low):
            return "BUNKER_CLAUSE"
        return "TECHNICAL_SPEC"

    if tech_line_hits >= max(3, n_lines // 2) and cargo_hits == 0 and charter_hits == 0 and vessel_hits == 0:
        return "TECHNICAL_SPEC"

    # Voyage / cargo fixture BEFORE charter (avoid ttl/wog in footers misrouting VC)
    if cargo_hits >= 1:
        return "CARGO_FIXTURE"
    if re.search(r"(?i)\b\d[\d,\s]{2,}\s*(?:mt|mts)\b", t):
        return "CARGO_FIXTURE"

    # Charter fixture (TC / trip)
    if charter_hits >= 2 or (
        charter_hits >= 1
        and re.search(r"(?i)\b(?:delivery|redelivery|duration)\s*[:]", low)
    ):
        return "CHARTER_FIXTURE"

    # Open tonnage / vessel offer
    if vessel_hits >= 2 or (vessel_hits >= 1 and re.search(r"(?i)\b(?:mv|m/t|open)\b", low)):
        return "VESSEL_OPEN"

    if re.search(r"(?i)\b\d{3,6}\s*/\s*\d{3,6}\b", t):
        return "CARGO_FIXTURE"
    if re.search(
        r"(?i)\d{1,3}(?:[.,'\s]\d{3})*\s*(?:\+-?\s*\d+\s*%)?\s*(?:mt|mts|metric\s*tons?)\b",
        t,
    ):
        return "CARGO_FIXTURE"

    # Long prose without maritime anchors → noise
    if len(t) > 500 and cargo_hits == 0 and vessel_hits == 0 and charter_hits == 0:
        return "NOISE"

    if tech_line_hits >= 1 and cargo_hits == 0 and vessel_hits == 0 and charter_hits == 0:
        return "TECHNICAL_SPEC"

    return "NOISE"


def should_extract_block(text: str) -> Tuple[bool, str]:
    label = classify_block(text)
    return (label in EXTRACTABLE_LABELS, label)
