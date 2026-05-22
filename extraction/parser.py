from extraction.vessel_specs import *
from extraction.email_classifier import classify_email_type
from extraction.llm_fallback import send_to_llm
from extraction.preprocessing import clean_text
from models.spacy_extractor import extract_entities
from extraction.classifier import classify_cargo, classify_vessel
from extraction.normalization import *
from extraction.intelligence import expand_maritime_terms
from extraction.confidence import calculate_confidence
from extraction.regex_engine import *
from extraction.regex_engine_v2 import *
from extraction.knowledge_engine import *
from extraction.signature_parser import extract_signature
from extraction.segmentation import split_email_blocks
from extraction.validator import final_record_validation, validate_record
from extraction.template_engine import detect_template
from extraction.schema_contract import order_vessel_entry
from extraction.block_classifier import should_extract_block
from extraction.field_filters import (
    extract_phone_strict,
    sanitize_port_value,
    sanitize_quantity_value,
    sanitize_vessel_name,
)
from extraction.maritime_parse import enrich_block_parse, expand_cargo_synonym
from extraction.entity_filter import filter_maritime_entities
from extraction.semantic_rules import (
    choose_email_and_template,
    has_invalid_cargo_context,
    has_valid_quantity_context,
    is_blacklisted_cargo,
    is_vessel_spec_text,
    normalize_vessel_type,
)
from extraction.entity_linker import (
    build_cargo_legs,
    build_trade_flow,
)
import json
import os


import re


def _extract_tc_fields(text):
    def _tc_place(raw):

        if not raw:
            return ""

        raw = raw.strip()

    # =====================================
    # REMOVE BROKER NOISE
    # =====================================

        raw = re.sub(
        r'(?i)\b(?:wog|abt|about|duration|laycan)\b',
        '',
        raw
         )

    # =====================================
    # REMOVE EXCESS SYMBOLS
    # =====================================

        raw = re.sub(
            r'[\(\)\[\]\{\}]',
            ' ',
             raw
        )

        raw = re.sub(
             r'\s+',
             ' ',
             raw
        ).strip()

    # =====================================
    # KEEP IMPORTANT TRANSIT ROUTES
    # =====================================

        important_routes = [

        "PASS GIB",
        "SKAW",
        "BSEA",
        "EMED",
        "WMED",
        "GOA",
        "COGH",
        "WCCA",
        "ARAG",
        "PG",
        "ECI",
        "WCI",

        ]

        upper_raw = raw.upper()

        for route in important_routes:

            if route in upper_raw:

               return route

    # =====================================
    # PORT SANITIZATION
    # =====================================

        cleaned = sanitize_port_value(raw)

        if cleaned:
            return cleaned

        return raw.title()

    def _tc_duration(raw):
        val = re.sub(r"(?i)\bwog\b", "", raw or "")
        val = re.sub(r"(?i)\b(?:abt|about)\b", "", val)
        val = re.sub(r"\s+", " ", val).strip()
        m = re.search(r"(?i)(\d{1,3})\s*[-/]\s*(\d{1,3})\s*days?", val)
        if m:
            return f"{m.group(1)}-{m.group(2)} Days"
        return val

    delivery = re.search(r"(?i)\b(?:delivery|dely)\s*[:\-]?\s*([^\n;]+)", text)
    redelivery = re.search(r"(?i)\b(?:redelivery|redely|redel)\s*[:\-]?\s*([^\n;]+)", text)
    duration = re.search(r"(?i)\b(?:duration|period)\s*[:\-]?\s*([^\n;]+)", text)
    if not duration:
        duration = re.search(r"(?i)\b((?:abt|about)?\s*\d{1,3}\s*[-/]\s*\d{1,3}\s*days?(?:\s+wog)?)\b", text)
    commission = re.search(r"(?i)\b(\d+(?:\.\d+)?)\s*%\s*(?:ttl|adc|adcom|commission)?", text)
    return {
        "delivery": _tc_place(delivery.group(1)) if delivery else "",
        "redelivery": _tc_place(redelivery.group(1)) if redelivery else "",
        "duration": _tc_duration(duration.group(1)) if duration else "",
        "commission": f"{commission.group(1)}%" if commission else "",
    }


def _extract_tc_cargo(text):

    text_low = (text or "").lower()

    tc_patterns = [

        r'(?i)tct\s+with\s+([^\n]+)',
        r'(?i)trip\s+with\s+([^\n]+)',
        r'(?i)with\s+([^\n]+?)\s+abt',
        r'(?i)with\s+([^\n]+?)\s+wog',
        r'(?i)cargo\s*[:\-]\s*([^\n]+)',

    ]

    maritime_noise = [

        "wog",
        "abt",
        "about",
        "days",
        "duration",
        "delivery",
        "redelivery",
        "period",
        "trip",
        "tct",
        "time charter",
        "lawful",
        "lawfuls",
        "gens",
        "cargo",
        "with",

    ]

    for pattern in tc_patterns:

        matches = re.finditer(pattern, text)

        for match in matches:

            raw = match.group(1)

            raw = raw.replace("/", " ")

            raw = raw.replace("+", " ")

            raw = re.sub(
                r'[^A-Za-z0-9\s\-]',
                ' ',
                raw
            )

            raw = re.sub(
                r'\s+',
                ' ',
                raw
            )

            tokens = raw.split()

            filtered = []

            for token in tokens:

                if token.lower() in maritime_noise:
                    continue

                filtered.append(token)

            cleaned = " ".join(filtered).strip()

            cleaned = expand_cargo_synonym(cleaned)

            cleaned = clean_cargo(cleaned)

            if not cleaned:
                continue

            if is_blacklisted_cargo(cleaned):
                continue

            if len(cleaned) < 3:
                continue

            # =========================
            # ENTERPRISE CARGO MAPPING
            # =========================

            lower_clean = cleaned.lower()

            if "grain" in lower_clean:
                return "Grain"

            if "steel" in lower_clean:
                return "Steel Products"

            if "clinker" in lower_clean:
                return "Clinker"

            if "slag" in lower_clean:
                return "Slag"

            if "bulk" in lower_clean:
                return "Harmless Bulk Cargo"

            return cleaned.title()

    return None


def _extract_dwt_range(text):
    match = re.search(r"(?i)\b(\d{2,3})\s*k\s*dwt\s*(?:upto|up\s*to|-|to)?\s*([a-z]*max)?", text or "")
    if match:
        low = int(match.group(1)) * 1000
        size_hint = (match.group(2) or "").lower()
        if size_hint in {"umax", "ultramax"} and 55000 <= low <= 60000:
            return f"{low}-60000"
        return str(low)
    match = re.search(r"(?i)\b(\d{2,3})\s*[-/]\s*(\d{2,3})\s*k\s*dwt\b", text or "")
    if match:
        return f"{int(match.group(1)) * 1000}-{int(match.group(2)) * 1000}"
    return None


def _unique_list(values):
    seen = set()
    out = []
    for value in values or []:
        if not value:
            continue
        key = str(value).strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(value)
    return out


def _sanitize_port_list(values):
    cleaned = []
    for value in values or []:
        port = sanitize_port_value(value)
        if port:
            cleaned.append(port)
    return _unique_list(cleaned)


def _join_ports(values):
    values = _unique_list(values or [])
    return ", ".join(values) if values else None


def _passes_precision_gate(data, block_class, block_text):
    """Drop weak blocks: precision over recall."""
    bc = block_class or ""
    if bc == "CARGO_FIXTURE":
        signals = (
            data.get("cargo"),
            data.get("quantity"),
            data.get("load_port"),
            data.get("discharge_port"),
            data.get("load_rate"),
            data.get("discharge_rate"),
            data.get("tolerance"),
        )
        n = sum(1 for s in signals if s)
        if len(data.get("cargo_legs") or []) >= 2:
            n = max(n, 2)
        return n >= 1
    if bc in ("VESSEL_OPEN", "VESSEL_HEADER"):
        return bool(data.get("dwt") or data.get("imo") or data.get("vessel_name"))
    if bc == "CHARTER_FIXTURE":
        return bool(data.get("delivery") or data.get("dwt") or data.get("duration"))
    return False


def _build_rescue_record(block):
    """Last structured-output guardrail for maritime blocks that miss strict gates."""
    block = clean_text(block or "")
    if not block.strip():
        return None

    maritime = enrich_block_parse(block)
    cargo_entries = extract_cargo_entries_v2(block, CARGO_KEYWORDS)
    quantity_entries = extract_quantities_v2(block)
    port_entries = dedupe_port_pairs(extract_port_pairs_v2(block))
    laycan_range = extract_laycan_range_v2(block)

    first_cargo = cargo_entries[0].get("cargo_name") if cargo_entries else None
    first_qty = quantity_entries[0].get("quantity") if quantity_entries else None
    first_ports = port_entries[0] if port_entries else {}
    first_hint = (maritime.get("cargo_legs_hint") or [{}])[0]
    cargo_name = first_cargo or first_hint.get("cargo_name")
    quantity = sanitize_quantity_value(first_qty or first_hint.get("quantity"))

    load_ports = _sanitize_port_list(
        first_ports.get("load_ports")
        or maritime.get("load_ports")
        or ([first_hint.get("load_port")] if first_hint.get("load_port") else [])
    )
    discharge_ports = _sanitize_port_list(
        first_ports.get("discharge_ports")
        or maritime.get("discharge_ports")
        or ([first_hint.get("discharge_port")] if first_hint.get("discharge_port") else [])
    )
    vessel_name = sanitize_vessel_name(extract_vessel_name_v2(block))
    vessel_type = normalize_vessel_type(block, detect_vessel_type(block))
    dwt = _extract_dwt_range(block) or extract_dwt_v2(block)
    tc_fields = _extract_tc_fields(block)
    tc_cargo = _extract_tc_cargo(block)

    cargo_legs = []
    for hint in maritime.get("cargo_legs_hint") or []:
        cargo_legs.append(
            {
                "cargo_name": hint.get("cargo_name") or cargo_name,
                "cargo_type": classify_cargo(clean_cargo(hint.get("cargo_name") or cargo_name)) if (hint.get("cargo_name") or cargo_name) else "Unknown",
                "quantity": sanitize_quantity_value(hint.get("quantity")) or quantity,
                "quantity_unit": hint.get("quantity_unit") or "MT",
                "load_port": hint.get("load_port") or (load_ports[0] if load_ports else None),
                "discharge_port": hint.get("discharge_port") or (discharge_ports[0] if discharge_ports else None),
                "laycan_start": normalize_date(laycan_range.get("start")),
                "laycan_end": normalize_date(laycan_range.get("end")),
            }
        )
    if not cargo_legs and any([cargo_name, quantity, load_ports, discharge_ports]):
        cargo_legs.append(
            {
                "cargo_name": cargo_name,
                "cargo_type": classify_cargo(clean_cargo(cargo_name)) if cargo_name else "Unknown",
                "quantity": quantity,
                "quantity_unit": "MT",
                "load_port": load_ports[0] if load_ports else None,
                "discharge_port": discharge_ports[0] if discharge_ports else None,
                "laycan_start": normalize_date(laycan_range.get("start")),
                "laycan_end": normalize_date(laycan_range.get("end")),
            }
        )
    cargo_legs = dedupe_cargo_legs(normalize_cargo_legs(cargo_legs))
    
    # =====================================
# REMOVE EMPTY / FAKE LEGS
# =====================================

    cleaned_legs = []

    for leg in cargo_legs:

        filled = 0

        if leg.get("cargo_name"):
            filled += 1

        if leg.get("quantity"):
            filled += 1

        if leg.get("load_port"):
            filled += 1

        if leg.get("discharge_port"):
            filled += 1

    # minimum semantic completeness
        if filled >= 2:

           cleaned_legs.append(leg)

    cargo_legs = cleaned_legs

    vessel_data = []
    if vessel_name or dwt or vessel_type != "Unknown Vessel":
        vessel_data.append(
            order_vessel_entry(
                {
                    "vessel_name": vessel_name or "",
                    "vessel_type": vessel_type or "",
                    "dwt": dwt or "",
                    "imo_number": extract_imo_v2(block) or "",
                    "open_location": extract_open_port_v2(block) or "",
                    "open_date": extract_open_date_v2(block),
                    "vessel_status": "OPEN" if re.search(r"(?i)\bopen\b", block) else "",
                }
            )
        )

    data = {
        "email_type": "UNKNOWN",
        "template_type": detect_template(block),
        "emails": extract_email(block),
        "phones": extract_phone_strict(block),
        "laycan": extract_laycan_v2(block),
        "dwt": dwt,
        "cargo": tc_cargo or cargo_name,
        "cargo_type": classify_cargo(clean_cargo(tc_cargo or cargo_name)) if (tc_cargo or cargo_name) else "Unknown",
        "vessel_name": vessel_name,
        "vessel_type": vessel_type,
        "imo": extract_imo_v2(block) or extract_imo(block),
        "open_port": extract_open_port_v2(block),
        "open_date": extract_open_date_v2(block),
        "load_port": _join_ports(load_ports),
        "discharge_port": _join_ports(discharge_ports),
        "load_ports": load_ports,
        "discharge_ports": discharge_ports,
        "quantity": quantity,
        "quantity_unit": "MT",
        "laycan_start": normalize_date(laycan_range.get("start")),
        "laycan_end": normalize_date(laycan_range.get("end")),
        "cargo_legs": cargo_legs,
        "vessel_data": vessel_data,
        "delivery": tc_fields.get("delivery"),
        "redelivery": tc_fields.get("redelivery"),
        "duration": tc_fields.get("duration"),
        "commission": tc_fields.get("commission"),
        "load_rate": maritime.get("load_rate"),
        "discharge_rate": maritime.get("discharge_rate"),
        "tolerance": maritime.get("tolerance"),
        "restrictions": [],
        "entities": filter_maritime_entities(extract_entities(block), block),
        "partial_extraction": True,
    }
    priority_type = choose_email_and_template(data, block)
    data["email_type"] = priority_type["email_type"]
    data["template_type"] = priority_type["template_type"]

    has_signal = any(
        [
            data.get("cargo"),
            data.get("quantity"),
            data.get("load_port"),
            data.get("discharge_port"),
            data.get("dwt"),
            data.get("vessel_name"),
            data.get("imo"),
            data.get("delivery"),
            data.get("redelivery"),
            data.get("duration"),
            data.get("load_rate"),
            data.get("discharge_rate"),
        ]
    )
    if not has_signal:
        return None

    data["validation_issues"] = final_record_validation(data, block, threshold=0)[1]
    data["confidence_score"] = calculate_confidence(data)
    data["extraction_status"] = (
        "HIGH_CONFIDENCE"
        if data["confidence_score"] >= 80
        else "MEDIUM_CONFIDENCE"
        if data["confidence_score"] >= 50
        else "LOW_CONFIDENCE"
    )
    if data["confidence_score"] < 20:
        data["llm_fallback"] = send_to_llm(block)
    data["structured_record"] = build_enterprise_record(data)
    return data


def extract_vessel_name(text):

    pattern = r"(MV\s+[A-Z\s0-9\-]+)"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1).strip() if match else None


def extract_imo(text):

    pattern = r"IMO[:\s\-]*([0-9]{7})"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1) if match else None


def extract_open_port(text):

    pattern = r"OPEN[:\s\-]*([A-Z\s]+)"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1).strip() if match else None


def extract_grain_capacity(text):

    pattern = r"GRAIN(?:\s+CAPACITY)?[:\s\-]*([0-9,\.]+)"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1) if match else None


def extract_vessel_type(text):

    vessel_types = [

        "SUPRAMAX",
        "ULTRAMAX",
        "HANDYSIZE",
        "HANDYMAX",
        "PANAMAX",
        "SMX",
        "UMX"

    ]

    for vessel in vessel_types:

        if vessel.lower() in text.lower():

            return vessel

    return "Unknown Vessel"


from extraction.router import detect_email_type

from extraction.vc_parser import parse_voyage_charter

from extraction.tc_parser import parse_tc

from extraction.tonnage_parser import parse_tonnage

from extraction.segmentation import split_email_blocks

from extraction.confidence import calculate_confidence

from extraction.validator import final_record_validation

from extraction.llm_fallback import send_to_llm

from extraction.schema_contract import build_enterprise_record

import json
import os


def process_email(text):

    blocks = split_email_blocks(text)

    results = []

    for block in blocks:

        block = clean_text(block)

        if len(block.strip()) < 20:
            continue

        email_type = detect_email_type(block)

        parsed = {}

        # =====================================
        # ROUTING
        # =====================================

        if email_type == "VC":

            parsed = parse_voyage_charter(block)

        elif email_type == "TC":

            parsed = parse_tc(block)

        elif email_type == "TONNAGE":

            parsed = parse_tonnage(block)

        else:

            continue

        # =====================================
        # VALIDATION
        # =====================================

        parsed["validation_issues"] = final_record_validation(
            parsed,
            block,
            threshold=0
        )[1]

        # =====================================
        # CONFIDENCE
        # =====================================

        # =====================================
# TRADE FLOW LINKING
# =====================================

        trade_flow = build_trade_flow(block, parsed)

# =====================================
# EMAIL TYPE CORRECTION
# =====================================

        # =====================================
# SAFE EMAIL TYPE CORRECTION
# =====================================

        trade_email_type = trade_flow.get("email_type")

        current_email_type = parsed.get("email_type")

# only upgrade UNKNOWN
        if current_email_type in ["UNKNOWN", "", None]:

            if trade_email_type and trade_email_type != "UNKNOWN":

                parsed["email_type"] = trade_email_type

# semantic TC reinforcement
        elif current_email_type == "TC":

            tc_score = 0

            if parsed.get("delivery"):
                tc_score += 1

            if parsed.get("redelivery"):
                tc_score += 1

            if parsed.get("duration"):
                tc_score += 1

            if tc_score < 2:
               parsed["validation_issues"].append(
                     "Weak TC semantic structure"
                )

# semantic VC reinforcement
        elif current_email_type == "VC":

            vc_score = 0

            if parsed.get("cargo"):
               vc_score += 1

            if parsed.get("quantity"):
               vc_score += 1

            if parsed.get("load_port"):
               vc_score += 1

            if parsed.get("discharge_port"):
               vc_score += 1

            if vc_score < 2:

                parsed["validation_issues"].append(
            "Weak VC semantic structure"
                 )
# =====================================
# CONFIDENCE
# =====================================

        confidence = calculate_confidence(parsed)

# enterprise semantic boost
        confidence += trade_flow.get("confidence_boost", 0)

# prevent impossible overflow
        confidence = min(confidence, 100)

        parsed["confidence_score"] = confidence

        # =====================================
        # STATUS
        # =====================================

        if confidence >= 80:

            parsed["extraction_status"] = "HIGH_CONFIDENCE"

        elif confidence >= 50:

            parsed["extraction_status"] = "MEDIUM_CONFIDENCE"

        else:

            parsed["extraction_status"] = "LOW_CONFIDENCE"

            parsed["llm_fallback"] = send_to_llm(block)

        # =====================================
        # FINAL STRUCTURED RECORD
        # =====================================
                # =====================================
        # ENTERPRISE TC ENTITY MERGE
        # =====================================

        if parsed.get("delivery"):

            parsed["structured_record_delivery"] = parsed.get("delivery")

        if parsed.get("redelivery"):

            parsed["structured_record_redelivery"] = parsed.get("redelivery")

        if parsed.get("duration"):

            parsed["structured_record_duration"] = parsed.get("duration")

        # =====================================
        # TC SEMANTIC CONFIDENCE BOOST
        # =====================================

        tc_semantic_hits = 0

        if parsed.get("cargo"):
            tc_semantic_hits += 1

        if parsed.get("delivery"):
            tc_semantic_hits += 1

        if parsed.get("redelivery"):
            tc_semantic_hits += 1

        if parsed.get("duration"):
            tc_semantic_hits += 1

        if tc_semantic_hits >= 3:

            parsed["confidence_score"] += 45

            parsed["confidence_score"] = min(
                parsed["confidence_score"],
                100
            )

            parsed["extraction_status"] = "HIGH_CONFIDENCE"


        parsed["structured_record"] = build_enterprise_record(parsed)
                # =====================================
        # REMOVE TC LINES FROM SIGNATURE
        # =====================================

        if parsed.get("signature"):

            clean_names = []

            for n in parsed["signature"].get("names", []):

                if re.search(

                    r'(?i)\b('
                    r'dely|delivery|'
                    r'redely|redelivery|'
                    r'duration|laycan|'
                    r'cargo|quantity|'
                    r'goa|gib|emed|'
                    r'wmed|bsea|'
                    r'cogh|arag'
                    r')\b',

                    n

                ):

                    continue

                clean_names.append(n)

            parsed["signature"]["names"] = clean_names

        results.append(parsed)

    # =====================================
    # RESCUE LOGIC
    # =====================================

    if not results:

        for rescue_block in blocks:

            rescue_record = _build_rescue_record(rescue_block)

            if rescue_record:

                results.append(rescue_record)

    # =====================================
    # SAVE JSON
    # =====================================

    os.makedirs("output", exist_ok=True)

    with open(
        "output/results.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    return results



