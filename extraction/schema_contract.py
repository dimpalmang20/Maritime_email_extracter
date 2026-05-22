# Enterprise output contract: key ordering and validation helpers.
# Keeps API/JSON shape stable without changing extraction logic.

from typing import Any, Dict, List, Tuple

STRUCTURED_RECORD_FIELDS: Tuple[str, ...] = (
    "email_type",
    "cargo",
    "cargo_type",
    "quantity",
    "quantity_unit",
    "tolerance",
    "load_port",
    "discharge_port",
    "delivery",
    "redelivery",
    "duration",
    "load_rate",
    "discharge_rate",
    "laycan_start",
    "laycan_end",
    "commission",
    "vessel_name",
    "vessel_type",
    "dwt",
    "imo",
    "matching_region",
    "restrictions",
    "confidence_score",
)

CARGO_LEG_FIELDS: Tuple[str, ...] = (
    "cargo_name",
    "cargo_type",
    "quantity",
    "quantity_unit",
    "load_port",
    "discharge_port",
    "laycan_start",
    "laycan_end",
)

VESSEL_DATA_FIELDS: Tuple[str, ...] = (
    "vessel_name",
    "vessel_type",
    "dwt",
    "imo_number",
    "open_location",
    "open_date",
    "vessel_status",
)


def validate_enterprise_block(block: Dict[str, Any]) -> List[str]:
    """Return human-readable issues if block violates contract (empty list if OK)."""
    issues: List[str] = []
    for key in ("cargo_legs", "vessel_data", "structured_record"):
        if key not in block:
            issues.append(f"missing_top_level:{key}")
    if "structured_record" in block:
        sr = block["structured_record"]
        missing = [f for f in STRUCTURED_RECORD_FIELDS if f not in sr]
        if missing:
            issues.append(f"structured_record_missing:{','.join(missing)}")
        extras = [k for k in sr if k not in STRUCTURED_RECORD_FIELDS]
        if extras:
            issues.append(f"structured_record_extra:{','.join(sorted(extras))}")
    if "cargo_legs" in block:
        for i, leg in enumerate(block["cargo_legs"]):
            if not isinstance(leg, dict):
                issues.append(f"cargo_leg_{i}_not_dict")
                continue
            bad = [f for f in CARGO_LEG_FIELDS if f not in leg]
            if bad:
                issues.append(f"cargo_leg_{i}_missing:{','.join(bad)}")
    if "vessel_data" in block:
        for i, v in enumerate(block["vessel_data"]):
            if not isinstance(v, dict):
                issues.append(f"vessel_data_{i}_not_dict")
                continue
            bad = [f for f in VESSEL_DATA_FIELDS if f not in v]
            if bad:
                issues.append(f"vessel_data_{i}_missing:{','.join(bad)}")
    return issues


def order_cargo_leg(leg: Dict[str, Any]) -> Dict[str, Any]:
    return {k: leg.get(k) for k in CARGO_LEG_FIELDS}


def order_vessel_entry(v: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v.get(k) for k in VESSEL_DATA_FIELDS}
def build_enterprise_record(data=None):

    if data is None:
        data = {}

    return {

        "email_type": data.get("email_type", "UNKNOWN"),

        "cargo": data.get("cargo", ""),

        "cargo_type": data.get("cargo_type", ""),

        "quantity": data.get("quantity", ""),

        "quantity_unit": data.get("quantity_unit", "MT"),

        "load_port": data.get("load_port", ""),

        "discharge_port": data.get("discharge_port", ""),

        "delivery": data.get("delivery", ""),

        "redelivery": data.get("redelivery", ""),

        "duration": data.get("duration", ""),

        "laycan_start": data.get("laycan_start", ""),

        "laycan_end": data.get("laycan_end", ""),

        "commission": data.get("commission", ""),

        "vessel_name": data.get("vessel_name", ""),

        "vessel_type": data.get("vessel_type", ""),

        "dwt": data.get("dwt", ""),

        "imo": data.get("imo", ""),

        "open_port": data.get("open_port", ""),

        "open_date": data.get("open_date", ""),

        "grain_capacity": data.get("grain_capacity", ""),

        "grabs": data.get("grabs", ""),

        "cranes": data.get("cranes", ""),

        "speed": data.get("speed", ""),

        "consumption": data.get("consumption", ""),

        "bunkers": data.get("bunkers", ""),

        "matching_region": data.get("matching_region", ""),

        "restrictions": data.get("restrictions", []),

        "confidence_score": data.get("confidence_score", 0),

        "llm_used": data.get("llm_used", False)
    }