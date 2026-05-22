"""Post-filter spaCy / ML entities for maritime extraction payloads."""
from __future__ import annotations

import re
from typing import Any, Dict, List

from extraction.dataset_index import get_dataset_index
from extraction.knowledge_base import CARGO_KEYWORDS
from extraction.semantic_rules import INVALID_ENTITY_WORDS
from extraction.semantic_rules import normalize_vessel_type

BAD_ORG_WORDS = {

    "mt",
    "mts",
    "abt",
    "wog",
    "ttl",
    "grabs",
    "grab",
    "cqd",
    "fio",
    "fiost",
    "shex",
    "shinc",
    "dwt",
    "grt",
    "nrt",
    "loa",
    "beam",
    "cbm",
    "lsfo",
    "lsmgo",
    "ifo",
    "bss",
    "ada",

}


def filter_maritime_entities(entities: List[Dict[str, Any]], source_text: str = "") -> List[Dict[str, Any]]:
    if not entities:
        return []
    idx = get_dataset_index()
    out: List[Dict[str, Any]] = []

    for ent in entities:
        label = str(ent.get("label") or "")
        text = str(ent.get("text") or "").strip()
        if not text or len(text) > 120:
            continue
        tlow = text.lower().strip()
        if tlow in INVALID_ENTITY_WORDS:
            continue
        # =========================
# HARD MARITIME NOISE FILTER
# =========================

        if re.fullmatch(
             r"(wog|ttl|abt|mts?|dwt|grt|nrt|fiost|fio|cqd|shex|shinc|molco|adc|iac|filo)",
             tlow,
            re.I,
        ):
            continue

# Remove tiny uppercase junk
        if text.isupper() and len(text) <= 4:
            continue

# Remove date fragments
        if re.fullmatch(r"\d{1,2}[-/]\d{1,2}", text):
            continue

# Remove tiny fake orgs
        if label == "ORG" and len(text) <= 4:
            continue

# Remove fake cardinal entities
        if label == "CARDINAL":
            pure_digits = re.sub(r"\D", "", text)

            if pure_digits:

               val = int(pure_digits)

        # Remove tiny useless numbers
               if val < 1000:
                    continue

        # Remove impossible quantities
               if val > 500000:
                    continue

        if text.isupper() and len(text) <= 7 and tlow not in {"mv", "m/v", "dwt", "imo"}:
            if not idx.is_plausible_port(text) and not any(c == tlow for c in CARGO_KEYWORDS):
                continue

        if label in ("PERSON", "NORP"):
            continue

        if label in ("CARGO", "COMMODITY"):
            if not any(re.search(rf"\b{re.escape(c)}\b", tlow) for c in CARGO_KEYWORDS):
                continue

        if label in ("LOAD_PORT", "DISCHARGE_PORT", "PORT"):
            if not idx.is_plausible_port(text):
                continue

        if label in ("VESSEL_TYPE", "VESSEL"):
            if label == "VESSEL_TYPE" and normalize_vessel_type(text) == "Unknown Vessel":
                continue
            if label == "VESSEL" and len(text) < 3:
                continue

        if label in ("ORG", "GPE", "LOC"):
            if len(text) > 45:
                continue
            if any(bad in tlow for bad in BAD_ORG_WORDS):
                continue
            if tlow in {"npk", "ferts", "ttl", "adc", "wog", "eci", "wci", "wafr"}:
                continue
            if not idx.is_plausible_port(text) and not any(
                c in tlow for c in CARGO_KEYWORDS if len(c) > 3
            ):
                continue

        if label == "CARDINAL":
            td = text.replace(",", "").replace(" ", "")
            if not (td.isdigit() and 1000 <= int(td) <= 500000):
                continue

        out.append({"text": text, "label": label})

    return out
