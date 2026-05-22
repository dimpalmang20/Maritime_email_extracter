import re


MONTHS = (
    "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|"
    "january|february|march|april|june|july|august|september|october|november|december"
)


# =========================
# DWT EXTRACTION
# =========================

def extract_dwt_v2(text):

    patterns = [

        r'(?<!\d)(\d{2,3}[,\.]?\d{3})[ \t]*dwt\b',
        r'\bdwt\b[:\s]*(\d{2,3}[,\.]?\d{3}|\d{4,6})\b',
        r'(\d{2,3})k\s*dwt',
        r'dwt\s*(?:upto|about|abt|around)?\s*(\d{2,3})k',
        r'\((\d{2,3})k\)\s*(?:open|dwt|blt|built)',
        r'\b(\d{2,3})k\s*(?:open|dwt|blt|built)\b',
        r'\bopen\b[^\n]{0,40}\b(\d{2,3})k\b'

    ]

    for pattern in patterns:

        match = re.search(

            pattern,
            text,
            re.IGNORECASE

        )

        if match:

            value = match.group(1)

            value = value.replace(",", "")
            value = value.replace(".", "")

            if len(value) <= 3:

                value = str(int(value) * 1000)

            return value

    return None


# =========================
# IMO EXTRACTION
# =========================

def extract_imo_v2(text):

    pattern = r'imo[\s:\-]*(\d{7})'

    match = re.search(

        pattern,
        text,
        re.IGNORECASE

    )

    if match:

        return match.group(1)

    return None


# =========================
# VESSEL NAME EXTRACTION
# =========================

def extract_vessel_name_v2(text):

    patterns = [

        r'(?i)\bMV[ \t]+([A-Z0-9\-]+(?:[ \t]+[A-Z0-9\-]+){0,4})\b',
        r'(?i)\bM/T[ \t]+([A-Z0-9\-]+(?:[ \t]+[A-Z0-9\-]+){0,4})\b',
        r'(?i)\bVESSEL\s+NAME[: \t]*([A-Z0-9\-]+(?:[ \t]+[A-Z0-9\-]+){0,4})\b'

    ]

    for pattern in patterns:

        match = re.search(

            pattern,
            text,
            re.IGNORECASE

        )

        if match:

            vessel = match.group(1)

            vessel = vessel.strip()
            vessel = re.sub(r'(?i)\btype\b$', '', vessel).strip()
            vessel = re.sub(r'(?i)\b(open|dwt|imo|built)\b.*$', '', vessel).strip()
            vessel = re.sub(r'(?i)\b\d{2,3}k\b$', '', vessel).strip()
            if len(vessel) > 52 or "\n" in vessel or len(vessel.split()) > 8:
                return None
            if re.search(
                r"(?i)\b(?:and|or|which|subject|pursuant|hereunder|laycan|grabber|"
                r"fitted|type|cargo|delivery|redelivery|duration|terms)\b",
                vessel,
            ):
                return None

            return vessel

    from extraction.semantic_rules import is_vessel_spec_text

   


# =========================
# OPEN PORT EXTRACTION
# =========================

def extract_open_port_v2(text):
    def _clean_open(raw):
        from extraction.field_filters import sanitize_port_value

        port = (raw or "").strip()
        port = re.split(r"\s+\d{1,2}", port, 1)[0].strip()
        port = re.sub(r"[,\s]+$", "", port)
        if "," in port:
            for part in port.split(","):
                resolved = sanitize_port_value(part.strip())
                if resolved:
                    return resolved
        resolved = sanitize_port_value(port)
        return resolved or (port if len(port) >= 3 else None)

    match = re.search(
        r"(?i)\bopen\b[:\s\-]*([A-Za-z][A-Za-z,\s\-]{2,60})",
        text or "",
    )
    if match:
        port = _clean_open(match.group(1))
        if port:
            return port

    match = re.search(
        r"(?i)\bopn\b[:\s\-]*([A-Za-z][A-Za-z,\s\-]{2,60})",
        text or "",
    )
    if match:
        port = _clean_open(match.group(1))
        if port:
            return port

    match = re.search(
        r"(?i)\bposition\b[:\s\-]*([A-Za-z][A-Za-z,\s\-]{2,60})",
        text or "",
    )
    if match:
        port = _clean_open(match.group(1))
        if port:
            return port

    from extraction.semantic_rules import is_vessel_spec_text

    if is_vessel_spec_text(text):
        for line in (text or "").splitlines()[:8]:
            candidate = line.strip()
            candidate = re.sub(r"(?i)^(?:mv|m/v|m\.v\.|vessel\s*name)\s*[:\-]?\s*", "", candidate).strip()
            if not candidate:
                continue
            if re.search(r"(?i)\b(?:imo|dwt|grt|nrt|loa|beam|built|flag|class|open|capacity)\b", candidate):
                continue
            if re.fullmatch(r"[A-Z0-9][A-Z0-9\-\s]{2,45}", candidate) and len(candidate.split()) <= 6:
                return candidate

    return None


def extract_open_date_v2(text):
    from extraction.semantic_rules import normalize_open_date

    t = text or ""
    patterns = [

    # 25/30,000 mts
    r'(?i)\b(\d{1,3})\s*[/\-]\s*(\d{1,3}(?:[,\.\'\s]\d{3})?)\s*(mt|mts|tons?|metric\s*tons?)\b',

    # 30,000 mts +/-10%
    r'(?i)\b(\d{1,3}(?:[.,\'\s]\d{3})+)\s*(?:\+/?-?\s*\d+\s*%)?\s*(?:mt|mts|tons?|metric\s*tons?)\b',

    # 58000 mt
    r'(?i)\b(\d{4,6})\s*(?:mt|mts|tons?|metric\s*tons?)\b',

    # quantity: 30,000
    r'(?i)\b(?:qty|quantity|cargo)\s*[:\-]?\s*(\d{1,3}(?:[,\.\'\s]\d{3})+)\b',

    # abt 58k mts
    r'(?i)\babt\.?\s*(\d{2,3})k\s*(?:mt|mts|tons?)\b',

    # 58k cargo
    r'(?i)\b(\d{2,3})k\s*(?:mt|mts|tons?)\b',

]
    for pattern in patterns:
        match = re.search(pattern, t)
        if match:
            raw = match.group(match.lastindex or 1)
            value = normalize_open_date(raw)
            if value:
                return value
    return ""


# =========================
# LAYCAN EXTRACTION
# =========================

def extract_laycan_v2(text):

    def _cap(val: str) -> str:
        val = (val or "").strip()
        if len(val) > 80:
            val = val[:80].rsplit(" ", 1)[0]
        return val

    strict = r"laycan[:\s]*(\d{1,2}[-/]\d{1,2}\s*[a-zA-Z]+)"
    loose_month = r"\b(\d{1,2}[-/]\d{1,2}\s*[a-zA-Z]{3,})\b"
    ordinal_range = r"(\d{1,2}(?:st|nd|rd|th)?\s*[-to/]+\s*\d{1,2}(?:st|nd|rd|th)?\s*[a-zA-Z]{3,})"

    laycan_lines = [
        line[:200] for line in (text or "").splitlines() if re.search(r"(?i)laycan", line)
    ]
    search_space = laycan_lines if laycan_lines else [(text or "")[:450]]

    for segment in search_space:
        m = re.search(strict, segment, re.IGNORECASE)
        if m:
            return _cap(m.group(1))
        m = re.search(ordinal_range, segment, re.IGNORECASE)
        if m:
            return _cap(m.group(1))
        m = re.search(loose_month, segment, re.IGNORECASE)
        if m:
            return _cap(m.group(1))

    return None


def extract_laycan_range_v2(text):
    head = (text or "")[:700]
    patterns = [
        rf'(?i)\bbetween\s+(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTHS})(?:\s+(\d{{4}}))?\s+and\s+(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTHS})(?:\s+(\d{{4}}))?\b',
        rf'(?i)\b(?:laycan|lc|dates?)[:\s\-]*(?:about\s+)?(end|mid|early)\s+({MONTHS})(?:\s+(\d{{4}}))?\b',
        rf'(?i)\b(?:spot\s+dates?|spot|prompt)\b',
        rf'(?i)\b(\d{{1,2}})(?:st|nd|rd|th)?\s*[-/]\s*(\d{{1,2}})(?:st|nd|rd|th)?\s*/\s*({MONTHS})(?:\s+(\d{{4}}))?\b',
        rf'(?i)\blaycan[:\s\-]*(\d{{1,2}})\s*[-/to]+\s*(\d{{1,2}})\s*({MONTHS})\b',
        rf'(?i)\b(\d{{1,2}})\s*[-/to]+\s*(\d{{1,2}})\s*({MONTHS})\b',
        rf'(?i)\bprompt\s+onwards?\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, head)
        if match:
            if "prompt" in match.group(0).lower():
                return {"start": "PROMPT", "end": "ONWARDS"}
            if "spot" in match.group(0).lower():
                return {"start": "SPOT", "end": "SPOT"}
            if "between" in match.group(0).lower():
                start_day, start_month = match.group(1), match.group(2)
                end_day, end_month = match.group(4), match.group(5)
                start_year = match.group(3)
                end_year = match.group(6) or start_year
                return {
                    "start": " ".join(x for x in [start_day, start_month, start_year] if x),
                    "end": " ".join(x for x in [end_day, end_month, end_year] if x),
                }
            if match.group(1).lower() in {"early", "mid", "end"}:
                anchor = {"early": ("1", "10"), "mid": ("11", "20"), "end": ("25", "31")}[match.group(1).lower()]
                month = match.group(2)
                year = match.group(3) if match.lastindex and match.lastindex >= 3 else None
                return {
                    "start": " ".join(x for x in [anchor[0], month, year] if x),
                    "end": " ".join(x for x in [anchor[1], month, year] if x),
                }
            if "/" in match.group(0) and match.lastindex and match.lastindex >= 3:
                start_day, end_day, month = match.group(1), match.group(2), match.group(3)
                year = match.group(4) if match.lastindex >= 4 else None
                return {
                    "start": " ".join(x for x in [start_day, month, year] if x),
                    "end": " ".join(x for x in [end_day, month, year] if x),
                }
            start_day, end_day, month = match.group(1), match.group(2), match.group(3)
            return {"start": f"{start_day} {month}", "end": f"{end_day} {month}"}
    return {"start": None, "end": None}


# =========================
# QUANTITY EXTRACTION
# =========================

def extract_quantity_v2(text):

    patterns = [

        r'(\d{1,3}[,\.]?\d{3})\s*mt',
        r'(\d{1,3}[,\.]?\d{3})\s*mts',
        r'quantity[:\s]*(\d{1,3}[,\.]?\d{3})'

    ]

    for pattern in patterns:

        match = re.search(

            pattern,
            text,
            re.IGNORECASE

        )

        if match:

            qty = match.group(1)

            qty = qty.replace(",", "")
            qty = qty.replace(".", "")

            return qty

    return None


def extract_quantities_v2(text):

    from extraction.maritime_parse import (
        extract_quantity_cargo_pairs,
        normalize_maritime_number,
    )

    results = []

    seen = set()

    # =========================================
    # FIRST PRIORITY:
    # SEMANTIC QUANTITY-CARGO PAIRS
    # =========================================

    for pair in extract_quantity_cargo_pairs(text):

        q = pair.get("quantity")

        if not q:
            continue

        try:
            q_int = int(str(q).replace(",", ""))
        except:
            continue

        # enterprise cargo quantity limits
        if q_int < 1000 or q_int > 500000:
            continue

        key = str(q_int)

        if key in seen:
            continue

        seen.add(key)

        results.append(
            {
                "quantity": str(q_int),
                "quantity_unit": "MT",
                "cargo_name": pair.get("cargo_name"),
                "span": [0, 0],
                "source": "semantic_pair"
            }
        )

    if results:
        return results

    # =========================================
    # ENTERPRISE REGEX
    # =========================================

    patterns = [

        # 58,000 mts
        r'(?i)\b(\d{1,3}(?:[,\.\'\s]\d{3})+)\s*(?:\+/-\s*\d+\s*%)?\s*(?:mt|mts|metric\s*tons?)\b',

        # 58000 mt
        r'(?i)\b(\d{4,6})\s*(?:mt|mts|metric\s*tons?)\b',

        # quantity: 58000
        r'(?i)\bquantity\s*[:\-]?\s*(\d{1,3}(?:[,\.\'\s]\d{3})+|\d{4,6})\b',

        # cargo 30,000 mts
        r'(?i)\bcargo\b.{0,30}?\b(\d{1,3}(?:[,\.\'\s]\d{3})+|\d{4,6})\s*(?:mt|mts)\b',

    ]

    for pattern in patterns:

        for m in re.finditer(pattern, text):

            raw_match = m.group(0)

            raw_qty = m.group(1)

            # =====================================
            # LINE EXTRACTION
            # =====================================

            line_start = text.rfind("\n", 0, m.start()) + 1

            line_end = text.find("\n", m.end())

            if line_end == -1:
                line_end = len(text)

            line = text[line_start:line_end].strip()

            line_low = line.lower()

            # =====================================
            # HARD FALSE POSITIVE REJECTION
            # =====================================

            reject_patterns = [

                r'\bload\s*/\s*discharge\b',
                r'\bl/?d\s*rate',
                r'\brate',
                r'\bper\s*day',
                r'\bknots?\b',
                r'\bspeed\b',
                r'\bconsumption\b',
                r'\bifo\b',
                r'\bvlsfo\b',
                r'\blsmgo\b',
                r'\bbunkers?\b',
                r'\bcranes?\b',
                r'\bgrabs?\b',
                r'\bballast\b',
                r'\bladen\b',
                r'\bmt/day\b',
                r'\bday\b',
                r'\bdays\b',
                r'\bduration\b',
                r'\bperiod\b',
                r'\bcommission\b',
                r'\badcom\b',
                r'\badc\b',
                r'\bttl\b',
                r'\bimo\b',
                r'\bdwt\b',
                r'\bgrt\b',
                r'\bnrt\b',
                r'\bloa\b',
                r'\bbeam\b',
                r'\btpc\b',
                r'\bhatch\b',
                r'\bhold\b',
                r'\bcbm\b',
                r'\bcbft\b',
                r'\bmt\s*cr\b',
                r'\bx\s*\d+\s*mt\b',
                r'\bdoc[\-\s]*no\b',
                r'\bphone\b',
                r'\bmobile\b',

            ]

            reject = False

            for rp in reject_patterns:

                if re.search(rp, line_low):
                    reject = True
                    break

            if reject:
                continue

            # =====================================
            # ENUMERATION REJECTION
            # =====================================

            if re.match(r'^\s*\d+\.', line):
                continue

            if re.match(r'^\s*[A-Z]+\)', line):
                continue

            # =====================================
            # DATE/TIME REJECTION
            # =====================================

            if re.search(r'\d{1,2}:\d{1,2}', line):
                continue

            if re.search(r'\b(?:am|pm)\b', line_low):
                continue

            if re.search(r'\b(?:19|20)\d{2}\b', line):
                continue

            # =====================================
            # NORMALIZE
            # =====================================

            qty_val = normalize_maritime_number(raw_qty)

            if not qty_val:
                continue

            # =====================================
            # ENTERPRISE LIMITS
            # =====================================

            if qty_val < 1000:
                continue

            if qty_val > 500000:
                continue

            # =====================================
            # DUPLICATE CONTROL
            # =====================================

            key = str(qty_val)

            if key in seen:
                continue

            seen.add(key)

            results.append(
                {
                    "quantity": str(qty_val),
                    "quantity_unit": "MT",
                    "span": [m.start(), m.end()],
                    "source": "regex_enterprise"
                }
            )

    return results


def extract_cargo_entries_v2(text, cargo_keywords):
    from extraction.maritime_parse import expand_cargo_synonym, extract_commodity_lines, extract_quantity_cargo_pairs
    from extraction.semantic_rules import has_valid_cargo_context, is_blacklisted_cargo

    entries = []
    seen = set()
    labeled = re.finditer(r"(?im)^\s*(?:cargo|commodity|commodit)\s*[:\-]\s*([^\n]+)", text or "")
    for match in labeled:
        candidate = expand_cargo_synonym(match.group(1))
        if is_blacklisted_cargo(candidate):
            continue
        if not has_valid_cargo_context(text, match.start(1), match.end(1)):
            continue
        key = candidate.lower()
        if key not in seen:
            seen.add(key)
            entries.append({"cargo_name": candidate, "span": [match.start(1), match.end(1)]})
    for line in extract_commodity_lines(text):
        key = line.lower()
        if key not in seen:
            seen.add(key)
            entries.append({"cargo_name": line, "span": [0, 0]})
    for pair in extract_quantity_cargo_pairs(text):
        c = pair.get("cargo_name")
        if c:
            c = expand_cargo_synonym(c)
            key = c.lower()
            if key not in seen:
                seen.add(key)
                entries.append({"cargo_name": c, "span": [0, 0]})

    keyword_pattern = "|".join(sorted([re.escape(c) for c in cargo_keywords], key=len, reverse=True))
    if keyword_pattern:
        for match in re.finditer(rf"(?i)\b({keyword_pattern})\b", text):
            if not has_valid_cargo_context(text, match.start(), match.end()):
                continue
            cargo = expand_cargo_synonym(match.group(1).strip())
            if is_blacklisted_cargo(cargo):
                continue
            key = cargo.lower()
            if key not in seen:
                seen.add(key)
                entries.append({"cargo_name": cargo, "span": [match.start(), match.end()]})
    return entries


def extract_port_pairs_v2(text):

    from extraction.maritime_parse import extract_labeled_ports

    lp_list, dp_list = extract_labeled_ports(text)

    pairs = []

    if lp_list or dp_list:

        clean_lp = []
        clean_dp = []

        for p in lp_list:
            p = p.strip().title()

            if len(p) > 2:
                clean_lp.append(p)

        for p in dp_list:
            p = p.strip().title()

            if len(p) > 2:
                clean_dp.append(p)

        pairs.append(
            {
                "load_port": clean_lp,
                "discharge_port": clean_dp,
                "load_ports": clean_lp,
                "discharge_ports": clean_dp,
                "span": [0, min(len(text), 120)],
            }
        )

    return pairs
