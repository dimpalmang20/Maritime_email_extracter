"""
Lazy-loaded maritime reference data from datasets/ (validation + lookup only).

- datasets/maritime_ports.csv: AIS open-vessel feed (ports, IMO, vessel names, DWT)
- datasets/vessel_data.txt: human-readable vessel report (names, IMO lines)

Used for REFERENCE + VALIDATION + FILTERING — not blind replacement of extraction.
"""
from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path
from typing import FrozenSet, Optional, Set

_ROOT = Path(__file__).resolve().parent.parent
_CSV_PATH = _ROOT / "datasets" / "maritime_ports.csv"
_TXT_PATH = _ROOT / "datasets" / "vessel_data.txt"

# Region / route codes valid in charter emails (short tokens).
_REGION_CODES: FrozenSet[str] = frozenset(
    {"eci", "wci", "pg", "wafr", "eafr", "usg", "ecsa", "med", "fe", "cont"}
)

_INVALID_PORT_TOKENS: FrozenSet[str] = frozenset(
    {"g", "e", "a", "lp", "dp", "pol", "pod", "mv", "vsl", "tbn", "na", "n/a", "unknown", "tba"}
)


def _norm_port(name: str) -> str:
    s = re.sub(r"[^a-z\s\-]", "", (name or "").lower())
    return re.sub(r"\s+", " ", s).strip()


def _norm_vessel(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").upper()).strip()


@lru_cache(maxsize=1)
def get_dataset_index() -> "MaritimeDatasetIndex":
    return MaritimeDatasetIndex()


class MaritimeDatasetIndex:
    def __init__(self) -> None:
        self.ports: Set[str] = set()
        self.imo_numbers: Set[str] = set()
        self.vessel_names: Set[str] = set()
        self.dwt_samples: Set[int] = set()
        self._load_csv()
        self._load_vessel_txt()
        self._merge_knowledge_base()

    def _load_csv(self) -> None:
        if not _CSV_PATH.is_file():
            return
        with _CSV_PATH.open(encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for col in ("open_port", "current_location", "last_port", "next_destination"):
                    val = _norm_port(row.get(col) or "")
                    if len(val) >= 3 and val not in _INVALID_PORT_TOKENS:
                        self.ports.add(val)
                imo = str(row.get("imo") or "").strip()
                if imo.isdigit() and len(imo) == 7:
                    self.imo_numbers.add(imo)
                vn = _norm_vessel(row.get("vessel_name") or "")
                if len(vn) >= 3:
                    self.vessel_names.add(vn)
                try:
                    dwt = int(float(row.get("dwt") or 0))
                    if 1000 <= dwt <= 250000:
                        self.dwt_samples.add(dwt)
                except (TypeError, ValueError):
                    pass

    def _load_vessel_txt(self) -> None:
        if not _TXT_PATH.is_file():
            return
        text = _TXT_PATH.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"(?im)^\s*\d+\.\s+([A-Z0-9\-\s]{3,60})\s*\[", text):
            self.vessel_names.add(_norm_vessel(m.group(1)))
        for m in re.finditer(r"(?im)IMO\s*:\s*(\d{7})\b", text):
            self.imo_numbers.add(m.group(1))

    def _merge_knowledge_base(self) -> None:
        from extraction.knowledge_base import PORT_ALIASES, PORT_KEYWORDS

        for p in PORT_KEYWORDS:
            self.ports.add(_norm_port(p))
        for alias, canonical in PORT_ALIASES.items():
            self.ports.add(_norm_port(canonical))
            self.ports.add(_norm_port(alias))

    def is_valid_imo(self, value: str) -> bool:
        s = re.sub(r"\D", "", str(value or ""))
        return len(s) == 7 and s.isdigit()

    def is_known_imo(self, value: str) -> bool:
        s = re.sub(r"\D", "", str(value or ""))
        if not self.is_valid_imo(s):
            return False
        if s in self.imo_numbers:
            return True
        return self.is_valid_imo(s)

    def is_plausible_port(self, port: str) -> bool:
        p = _norm_port(port)
        if not p or len(p) < 3:
            return False
        if p in _INVALID_PORT_TOKENS:
            return False
        if p in _REGION_CODES:
            return True
        if p in self.ports:
            return True
        for known in self.ports:
            if len(known) >= 4 and (known in p or p in known):
                return True
        return False

    def resolve_port(self, port: str) -> Optional[str]:
        """Return title-cased canonical port if plausible, else None."""
        p = _norm_port(port)
        if not p:
            return None
        if p in _INVALID_PORT_TOKENS or len(p) < 3:
            return None
        if p in _REGION_CODES:
            return p.upper()
        if p in self.ports:
            return p.title()
        best = None
        for known in self.ports:
            if known == p:
                return known.title()
            if len(known) >= 4 and known in p:
                best = known
            elif len(p) >= 4 and p in known:
                best = known
        if best:
            return best.title()
        return None

    def is_plausible_vessel_name(self, name: str) -> bool:
        n = _norm_vessel(name)
        if not n or len(n) < 3:
            return False
        if len(n) > 48 or len(n.split()) > 7:
            return False
        if re.search(
            r"(?i)\b(?:consumption|bunker|ballast|clause|pursuant|hereunder|laden|trim|"
            r"laycan|grabber|fitted|cargo|delivery|redelivery|duration|period|type|terms)\b",
            n,
        ):
            return False
        if n in self.vessel_names:
            return True
        for vn in self.vessel_names:
            if vn in n or n in vn:
                return True
        if re.match(r"^[A-Z0-9][A-Z0-9\-\s]{2,40}$", n) and not re.search(r"\d{5,}", n):
            return True
        return False

    def is_plausible_cargo_quantity(self, qty) -> bool:
        try:
            v = int(str(qty).replace(",", ""))
        except (TypeError, ValueError):
            return False
        return 1000 <= v <= 500000

    def digits_are_imo_context(self, digits: str, block_text: str) -> bool:
        if len(digits) == 7 and digits.isdigit():
            if digits in self.imo_numbers:
                return True
            if re.search(rf"(?i)\bimo[\s:\-]*{re.escape(digits)}\b", block_text or ""):
                return True
        return False
