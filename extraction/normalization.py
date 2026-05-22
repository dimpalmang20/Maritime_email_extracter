# convert dates ,quatities , formats
import re
from datetime import datetime

from extraction.schema_contract import STRUCTURED_RECORD_FIELDS, order_cargo_leg


def normalize_quantity(quantity):

    if not quantity:
        return None

    from extraction.maritime_parse import normalize_maritime_number

    parsed = normalize_maritime_number(str(quantity))
    if parsed is not None:
        return parsed
    quantity = str(quantity).replace(",", "")
    return int(quantity) if quantity.isdigit() else None


def normalize_date(date_text):

    if not date_text:
        return date_text
    text = str(date_text).strip()
    default_year = 2025
    text = re.sub(r"(?i)(\d{1,2})(st|nd|rd|th)", r"\1", text)
    months = {
        "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
        "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7,
        "july": 7, "aug": 8, "august": 8, "sep": 9, "sept": 9,
        "september": 9, "oct": 10, "october": 10, "nov": 11, "november": 11,
        "dec": 12, "december": 12,
    }
    m = re.search(r"(?i)\b(end|mid|early)\s+([a-z]{3,9})(?:\s+(\d{4}))?\b", text)
    if m:
        day = {"early": 5, "mid": 15, "end": 25}[m.group(1).lower()]
        month = months.get(m.group(2).lower()) or months.get(m.group(2).lower()[:3])
        if month:
            year = int(m.group(3)) if m.group(3) else default_year
            return datetime(year, month, day).strftime("%Y-%m-%d")
    if re.search(r"(?i)\b(?:spot|prompt)\s+dates?\b|\b(?:spot|prompt)\b", text):
        return "SPOT"
    for fmt in ("%d %B %Y", "%d %b %Y", "%d-%m %B", "%d %B", "%d-%m-%b", "%d %b", "%d-%m-%Y"):
        try:
            date_obj = datetime.strptime(text, fmt)
            if "%Y" not in fmt and date_obj.year < 2000:
                date_obj = date_obj.replace(year=default_year)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text
    



def clean_port(port):

    if not port:
        return None

    port = port.strip()

    if "," in port:
        from extraction.field_filters import sanitize_port_value

        parts = [sanitize_port_value(p.strip()) for p in port.split(",")]
        parts = [p for p in parts if p]
        return ", ".join(parts) if parts else None

    if len(port) < 3:
        return None

    port = re.sub(r"[^A-Za-z\s\-]", "", port)
    port = re.sub(r"\s+", " ", port).strip()

    from extraction.field_filters import sanitize_port_value

    return sanitize_port_value(port.title())


def clean_cargo(cargo):

    if not cargo:
        return None

    cargo = cargo.strip()
    if re.search(r"(?i)\bharmless\s+bulk\s+cargo\b", cargo):
        return "Harmless Bulk Cargo"

    cargo = re.sub(r"[^A-Za-z0-9\s\-]", "", cargo)
    cargo = re.sub(r"\s+", " ", cargo).strip()

    from extraction.maritime_parse import expand_cargo_synonym

    cargo = expand_cargo_synonym(cargo)
    cargo = cargo.title()

    return cargo


def clean_phone(phone):

    if not phone:
        return None

    # Keep digits only
    phone = re.sub(r'\\D', '', phone)

    return phone


def clean_email(email):

    if not email:
        return None

    email = email.strip().lower()

    return email


def normalize_cargo_legs(legs):
    normalized = []
    for leg in legs or []:
        qty = leg.get("quantity")
        try:
            qty = normalize_quantity(str(qty)) if qty is not None else None
        except Exception:
            qty = None

        normalized.append(
            {
                "cargo_name": clean_cargo(leg.get("cargo_name")),
                "cargo_type": leg.get("cargo_type") or "",
                "quantity": qty,
                "quantity_unit": (leg.get("quantity_unit") or "").upper() or "MT",
                "load_port": clean_port(leg.get("load_port")),
                "discharge_port": clean_port(leg.get("discharge_port")),
                "laycan_start": normalize_date(leg.get("laycan_start")) if leg.get("laycan_start") else None,
                "laycan_end": normalize_date(leg.get("laycan_end")) if leg.get("laycan_end") else None,
            }
        )
    return [order_cargo_leg(leg) for leg in normalized]


def dedupe_port_pairs(pairs):
    seen = set()
    out = []
    for p in pairs or []:
        key = (
            (p.get("load_port") or "").strip().lower(),
            (p.get("discharge_port") or "").strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def dedupe_cargo_legs(legs):
    seen = set()
    out = []
    for leg in legs or []:
        key = (
            (leg.get("cargo_name") or "").strip().lower(),
            leg.get("quantity"),
            (leg.get("load_port") or "").strip().lower(),
            (leg.get("discharge_port") or "").strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(leg)
    compact = []
    for leg in out:
        name = (leg.get("cargo_name") or "").strip().lower()
        if not name:
            compact.append(leg)
            continue
        is_subsumed = False
        for other in out:
            other_name = (other.get("cargo_name") or "").strip().lower()
            if other is leg or not other_name:
                continue
            same_context = (
                leg.get("quantity") == other.get("quantity")
                and (leg.get("load_port") or "") == (other.get("load_port") or "")
                and (leg.get("discharge_port") or "") == (other.get("discharge_port") or "")
            )
            if same_context and name != other_name and name in other_name:
                is_subsumed = True
                break
        if not is_subsumed:
            compact.append(leg)
    return compact if compact else list(legs or [])


def dedupe_vessel_entries(vessels):
    seen = set()
    out = []
    for v in vessels or []:
        key = (
            (v.get("vessel_name") or "").strip().lower(),
            str(v.get("dwt") or "").strip(),
        )
        if key in seen and key != ("", ""):
            continue
        seen.add(key)
        out.append(v)
    return out


def _coerce_schema_quantity(q):
    if q is None or q == "":
        return ""
    try:
        return int(str(q).replace(",", ""))
    except ValueError:
        return ""


def _coerce_schema_dwt(d):
    if d is None or d == "":
        return ""
    s = str(d).strip().replace(",", "")
    if s.isdigit():
        return s
    return s


def build_enterprise_record(base_data):
    # Fixed field order and stable types for API/JSON consumers.
    def _safe_str(value):
        if isinstance(value, dict):
            value = value.get("email_type") or value.get("value") or ""
        return "" if value is None else str(value)

    def _port_array(*values):
        parts = []
        for value in values:
            if not value:
                continue
            if isinstance(value, list):
                raw_parts = value
            else:
                raw_parts = str(value).split(",")
            for part in raw_parts:
                cleaned = clean_port(str(part))
                if cleaned and cleaned not in parts:
                    parts.append(cleaned)
        return parts

    def _cargo_value(value):
        if isinstance(value, list):
            cleaned = [clean_cargo(v) for v in value if clean_cargo(v)]
            return ", ".join(dict.fromkeys(cleaned))
        return _safe_str(clean_cargo(value) or value or "")

    def _matching_region(load_ports, discharge_ports, open_port):
        from extraction.knowledge_base import PORT_REGION_MAP

        regions = []
        for port in list(load_ports or []) + list(discharge_ports or []) + ([open_port] if open_port else []):
            key = str(port or "").strip().lower()
            region = PORT_REGION_MAP.get(key)
            if region and region not in regions:
                regions.append(region)
        return ", ".join(regions)

    qty = _coerce_schema_quantity(base_data.get("quantity"))
    conf = base_data.get("confidence_score", 0)
    try:
        conf = float(conf)
    except (TypeError, ValueError):
        conf = 0.0
    if conf > 1:
        conf = round(conf / 100, 4)

    load_ports = _port_array(base_data.get("load_ports"), base_data.get("load_port"))
    discharge_ports = _port_array(base_data.get("discharge_ports"), base_data.get("discharge_port"))
    restrictions = base_data.get("restrictions") or []
    if isinstance(restrictions, str):
        restrictions = [restrictions] if restrictions.strip() else []

    def _port_value(*values):
        return ", ".join(_port_array(*values))

    record = {
        "email_type": _safe_str(base_data.get("email_type", "")),
        "cargo": _cargo_value(base_data.get("cargo")),
        "cargo_type": _safe_str(base_data.get("cargo_type", "")),
        "quantity": qty,
        "quantity_unit": _safe_str(base_data.get("quantity_unit", "") or "MT"),
        "tolerance": _safe_str(base_data.get("tolerance", "")),
        "load_port": _port_value(base_data.get("load_ports"), base_data.get("load_port")),
        "discharge_port": _port_value(base_data.get("discharge_ports"), base_data.get("discharge_port")),
        "delivery": _safe_str(base_data.get("delivery", "")),
        "redelivery": _safe_str(base_data.get("redelivery", "")),
        "duration": _safe_str(base_data.get("duration", "")),
        "load_rate": _safe_str(base_data.get("load_rate", "")),
        "discharge_rate": _safe_str(base_data.get("discharge_rate", "")),
        "laycan_start": _safe_str(base_data.get("laycan_start", "")),
        "laycan_end": _safe_str(base_data.get("laycan_end", "")),
        "commission": _safe_str(base_data.get("commission", "")),
        "vessel_name": _safe_str(base_data.get("vessel_name", "")),
        "vessel_type": _safe_str(base_data.get("vessel_type", "")),
        "dwt": _coerce_schema_dwt(base_data.get("dwt")),
        "imo": _safe_str(base_data.get("imo", "")),
        "matching_region": _matching_region(load_ports, discharge_ports, base_data.get("open_port")),
        "restrictions": restrictions,
        "confidence_score": conf,
    }
    return {k: record[k] for k in STRUCTURED_RECORD_FIELDS}
