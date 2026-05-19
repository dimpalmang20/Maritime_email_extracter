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
from extraction.validator import validate_record
from extraction.template_engine import detect_template
import json


import re


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

    pattern = r"GRAIN[:\s\-]*([0-9,\.]+)"

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


def process_email(text):

    blocks = split_email_blocks(text)

    results = []

    for block in blocks:
        email_type = classify_email_type(block)
        template_type = detect_template(block)
                    # Clean email block
        block = clean_text(block)
        data = {

    "email_type": email_type,
    "template_type": template_type,
    "emails": extract_email(block),

    "phones": extract_phone(block),

    "laycan": extract_laycan_v2(block),

    "dwt": extract_dwt_v2(block),

    "cargo": clean_cargo(
        detect_cargo(block)[0]
    ) if detect_cargo(block) else None,

    "cargo_type": classify_cargo(
        clean_cargo(extract_cargo(block)[0])
    ) if extract_cargo(block) else "Unknown",

    "vessel_name": extract_vessel_name_v2(block),

    "vessel_type": detect_vessel_type(block),

    "imo": extract_imo(block),

    "open_port": extract_open_port_v2(block),

    "load_port": clean_port(
        extract_lp(block)[0]
    ) if extract_lp(block) else None,

    "discharge_port": clean_port(
        extract_dp(block)[0]
    ) if extract_dp(block) else None,

    "detected_ports": detect_ports(block),

    "quantity": normalize_quantity(
        extract_quantity_v2(block)[0]
    ) if extract_quantity_v2(block) else None,

    "grain_capacity": extract_grain_capacity(block),

    "grt": extract_grt(block),

    "nrt": extract_nrt(block),

    "loa": extract_loa(block),

    "beam": extract_beam(block),

    "bale_capacity": extract_bale_capacity(block),

    "signature": extract_signature(block),

    "maritime_terms": expand_maritime_terms(block),

    "entities": extract_entities(block)

  }     
        
        # Calculate confidence
        data["confidence_score"] = calculate_confidence(data)
        data["validation_issues"] = validate_record(data)

        # Decide extraction quality
        if data["confidence_score"] >= 80:
            data["extraction_status"] = "HIGH_CONFIDENCE"

        elif data["confidence_score"] >= 50:
            data["extraction_status"] = "MEDIUM_CONFIDENCE"

        else:
            data["extraction_status"] = "LOW_CONFIDENCE"
            llm_result = send_to_llm(block)
            data["llm_fallback"] = llm_result
        results.append(data)
        # Save into database
        from database.db import SessionLocal
        from database.models import MaritimeRecord

        db = SessionLocal()

        record = MaritimeRecord(

            cargo=str(data.get("cargo")),

            cargo_type=str(data.get("cargo_type")),

            vessel_name=str(data.get("vessel_name")),

            vessel_type=str(data.get("vessel_type")),

            imo=str(data.get("imo")),

            load_port=str(data.get("load_port")),

            discharge_port=str(data.get("discharge_port")),

            open_port=str(data.get("open_port")),

            quantity=str(data.get("quantity")),

            grain_capacity=str(data.get("grain_capacity")),

            dwt=str(data.get("dwt")),

            laycan=str(data.get("laycan")),

            confidence_score=float(data.get("confidence_score", 0)),

            extraction_status=str(data.get("extraction_status")),

            template_type=str(data.get("template_type"))

        )

        db.add(record)

        db.commit()

        db.close()
    # SAVE JSON FILE
    with open("output/results.json", "w") as f:
        json.dump(results, f, indent=4)

    return results