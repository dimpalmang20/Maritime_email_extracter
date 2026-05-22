import re


def detect_email_type(block: str):

    text = block.lower()

    score = {
        "VC": 0,
        "TC": 0,
        "TONNAGE": 0,
        "VESSEL_SPEC": 0
    }

    # =========================
    # VOYAGE CHARTER SIGNALS
    # =========================

    vc_patterns = [
        r'\bcargo\b',
        r'\bcommodity\b',
        r'\blp\b',
        r'\bdp\b',
        r'\bpol\b',
        r'\bpod\b',
        r'\blaycan\b',
        r'\bqty\b',
        r'\bquantity\b',
        r'\bmts\b',
        r'\bmt\b'
    ]

    # =========================
    # TIME CHARTER SIGNALS
    # =========================

    tc_patterns = [
        r'\btct\b',
        r'\btime charter\b',
        r'\bdelivery\b',
        r'\bredelivery\b',
        r'\bduration\b',
        r'\bperiod\b',
        r'\btrip\b'
    ]

    # =========================
    # TONNAGE SIGNALS
    # =========================

    tonnage_patterns = [
        r'\bopen\b',
        r'\bmv\b',
        r'\bm/v\b',
        r'\bvessel\b',
        r'\bdwt\b',
        r'\bimo\b',
        r'\bblt\b',
        r'\bopen position\b'
    ]

    # =========================
    # VESSEL SPEC SIGNALS
    # =========================

    vessel_spec_patterns = [
        r'\bgrain capacity\b',
        r'\bbale capacity\b',
        r'\bloa\b',
        r'\bbeam\b',
        r'\bgrt\b',
        r'\bnrt\b',
        r'\bholds\b',
        r'\bhatches\b',
        r'\bcranes\b',
        r'\bgrabs\b'
    ]

    for pattern in vc_patterns:
        if re.search(pattern, text):
            score["VC"] += 2

    for pattern in tc_patterns:
        if re.search(pattern, text):
            score["TC"] += 3

    for pattern in tonnage_patterns:
        if re.search(pattern, text):
            score["TONNAGE"] += 2

    for pattern in vessel_spec_patterns:
        if re.search(pattern, text):
            score["VESSEL_SPEC"] += 3

    # =========================
    # PRIORITY DECISION
    # =========================

    if score["VESSEL_SPEC"] >= 8:
        return "VESSEL_SPEC"

    if score["TC"] >= 6:
        return "TC"

    if score["TONNAGE"] >= 6:
        return "TONNAGE"

    if score["VC"] >= 5:
        return "VC"

    return "UNKNOWN"