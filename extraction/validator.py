import re
from extraction.dataset_index import get_dataset_index
from extraction.knowledge_base import PORT_KEYWORDS, VESSEL_DWT_RULES

_NOISE_ONLY = re.compile(
    r"(?is)^\s*(?:dear\s+(?:all|sir|sirs|team)[,\s]*|good\s+day[,\s]*|"
    r"best\s+regards[,\s]*|kind\s+regards[,\s]*|thanks(?:\s+and\s+regards)?[,\s]*)+$"
)

_GARBAGE_VALUES = {"allowed", "hold", "holds", "terms", "group", "type", "period", "adcom"}


def validate_record(data):

    issues = []
    email_type = (data.get("email_type") or "").upper()


    require_cargo_route = email_type in {"VC", "UNKNOWN", ""}
    require_tc_fields = email_type == "TC"
    require_tonnage_fields = email_type == "TONNAGE"

    if require_cargo_route and not data.get("cargo"):

        issues.append("Cargo Missing")


    if require_cargo_route and not data.get("load_port"):

        issues.append("Load Port Missing")


    if require_cargo_route and not data.get("discharge_port"):

        issues.append("Discharge Port Missing")


    if require_cargo_route and not data.get("quantity"):

        issues.append("Quantity Missing")

    if require_tc_fields and not data.get("delivery"):
        issues.append("Delivery Missing")

    if require_tonnage_fields and not (data.get("vessel_name") or data.get("dwt")):
        issues.append("Vessel Position Missing")


    dwt = data.get("dwt")
    if dwt:
        try:
            dwt_text = str(dwt).replace(",", "")
            if "-" in dwt_text:
                dwt_value = max(int(p) for p in re.findall(r"\d{4,6}", dwt_text))
            else:
                dwt_value = int(dwt_text)
            if dwt_value < 1000 or dwt_value > 250000:
                issues.append("DWT Out Of Range")
            vessel_type = (data.get("vessel_type") or "").upper()
            if vessel_type in VESSEL_DWT_RULES:
                lower, upper = VESSEL_DWT_RULES[vessel_type]
                if dwt_value < lower or dwt_value > upper:
                    issues.append("Vessel Type and DWT Mismatch")
        except ValueError:
            issues.append("DWT Invalid Format")

    imo = data.get("imo")
    if imo and not re.fullmatch(r"\d{7}", str(imo)):
        issues.append("IMO Invalid Format")

    commission = str(data.get("commission") or "").strip()
    if commission:
        percent_match = re.search(r"(\d+(?:\.\d+)?)\s*%", commission)
        if percent_match and float(percent_match.group(1)) > 10:
            issues.append("Commission Too High")

    idx = get_dataset_index()
    for field in ("load_port", "discharge_port", "open_port"):
        port_val = data.get(field)
        if not port_val:
            continue
        if not idx.is_plausible_port(str(port_val)):
            issues.append(f"{field.replace('_', ' ').title()} Unverified")

    vn = data.get("vessel_name")
    if vn and not idx.is_plausible_vessel_name(str(vn)):
        issues.append("Vessel Name Implausible")

    if require_cargo_route and data.get("load_port") and data.get("discharge_port"):
        lp = str(data.get("load_port") or "").strip().lower()
        dp = str(data.get("discharge_port") or "").strip().lower()
        if lp and dp and lp == dp:
            issues.append("Load And Discharge Port Identical")

    laycan_start = data.get("laycan_start")
    laycan_end = data.get("laycan_end")
    laycan_raw = data.get("laycan")
    if (laycan_start and not laycan_end) or (laycan_end and not laycan_start):
        if not laycan_raw:
            issues.append("Laycan Range Incomplete")

    if laycan_start and laycan_end:
        m1 = re.search(r"(\d{1,2})", str(laycan_start))
        m2 = re.search(r"(\d{1,2})", str(laycan_end))
        mo1 = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)", str(laycan_start), re.I)
        mo2 = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)", str(laycan_end), re.I)
        if m1 and m2 and mo1 and mo2 and mo1.group(1).lower() == mo2.group(1).lower():
            if int(m1.group(1)) > int(m2.group(1)):
                issues.append("Laycan Start After End Same Month")

    vessels = data.get("vessel_data") or []
    vseen = set()
    for v in vessels:
        fp = ((v.get("vessel_name") or "").strip().lower(), str(v.get("dwt") or "").strip())
        if fp in vseen and fp != ("", ""):
            issues.append("Duplicate Vessel Entry")
        vseen.add(fp)

    quantity = data.get("quantity")
    if quantity is not None:
        try:
            qty_value = int(str(quantity).replace(",", ""))
            if qty_value < 1000 or qty_value > 500000:
                issues.append("Quantity Out Of Range")
        except ValueError:
            issues.append("Quantity Invalid Format")

    legs = data.get("cargo_legs") or []
    seen = set()
    for leg in legs:
        fingerprint = (
            (leg.get("cargo_name") or "").lower(),
            str(leg.get("quantity") or ""),
            (leg.get("load_port") or "").lower(),
            (leg.get("discharge_port") or "").lower(),
        )
        if any(fingerprint):
            if fingerprint in seen:
                issues.append("Duplicate Cargo Leg")
            seen.add(fingerprint)

    return sorted(set(issues))


def final_record_validation(data, block_text="", threshold=80):
    """
    Last precision gate before appending/API output.
    Returns (ok, issues). This intentionally drops partial/noisy records.
    """
    issues = list(validate_record(data))
    idx = get_dataset_index()
    text = str(block_text or "").strip()
    email_type = (data.get("email_type") or "").upper()

    if not text or _NOISE_ONLY.fullmatch(text):
        issues.append("Noise Only Block")

    cargo = data.get("cargo")
    if isinstance(cargo, list):
        cargo_values = [str(c).strip() for c in cargo if str(c).strip()]
    else:
        cargo_values = [str(cargo).strip()] if cargo else []
    if any(c.lower() in _GARBAGE_VALUES for c in cargo_values):
        issues.append("Garbage Cargo")

    for field in ("load_port", "discharge_port", "open_port"):
        val = data.get(field)
        if not val:
            continue
        parts = str(val).split(",")
        valid_parts = [p.strip() for p in parts if idx.is_plausible_port(p.strip())]
        if not valid_parts:
            issues.append(f"{field.replace('_', ' ').title()} Invalid")
        if any(len(p.strip()) < 3 for p in parts):
            issues.append(f"{field.replace('_', ' ').title()} Too Short")
    for field in ("delivery", "redelivery"):
        val = data.get(field)
        if val and len(str(val).strip()) < 3:
            issues.append(f"{field.title()} Too Short")

    if data.get("vessel_name") and not idx.is_plausible_vessel_name(str(data.get("vessel_name"))):
        issues.append("Vessel Name Invalid")

    if email_type == "TC":
        required_tc = {
            "delivery": data.get("delivery"),
            "redelivery": data.get("redelivery"),
            "duration": data.get("duration"),
            "cargo": cargo_values,
        }
        for key, value in required_tc.items():
            if not value:
                issues.append(f"TC {key.title()} Missing")
        if not (data.get("dwt") or (data.get("vessel_type") and data.get("vessel_type") != "Unknown Vessel")):
            issues.append("TC Vessel Requirement Missing")
        if not (data.get("laycan") or (data.get("laycan_start") and data.get("laycan_end"))):
            issues.append("TC Laycan Missing")
    elif email_type == "TONNAGE":
        if not (data.get("vessel_name") or data.get("dwt")):
            issues.append("Tonnage Vessel Missing")
        if not (data.get("open_port") or data.get("open_date")):
            issues.append("Tonnage Open Position Missing")
    else:
        if not cargo_values:
            issues.append("Cargo Missing")
        if not data.get("quantity"):
            issues.append("Quantity Missing")
        if not data.get("load_port"):
            issues.append("Load Port Missing")
        if not data.get("discharge_port"):
            issues.append("Discharge Port Missing")

    score = data.get("confidence_score") or 0
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0
    if score < threshold:
        issues.append("Confidence Below Threshold")

    issues = sorted(set(issues))
    return not issues, issues
