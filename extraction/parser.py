from extraction.llm_fallback import send_to_llm
from extraction.normalization import *
from extraction.intelligence import expand_maritime_terms
from extraction.confidence import calculate_confidence
from extraction.regex_engine import *
from extraction.signature_parser import extract_signature
from extraction.segmentation import split_email_blocks
import json


def process_email(text):

    blocks = split_email_blocks(text)

    results = []

    for block in blocks:

        data = {
            "emails": extract_email(block),
            "phones": extract_phone(block),
            "laycan": extract_laycan(block),
            "dwt": extract_dwt(block),
            "load_port": extract_lp(block),
            "discharge_port": extract_dp(block),
            "quantity": normalize_quantity(
                 extract_quantity(block)[0]
             ) if extract_quantity(block) else None,

            "cargo": extract_cargo(block),

            "signature": extract_signature(block),

            "maritime_terms": expand_maritime_terms(block)
        }

        # Calculate confidence
        data["confidence_score"] = calculate_confidence(data)

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
    # SAVE JSON FILE
    with open("output/results.json", "w") as f:
        json.dump(results, f, indent=4)

    return results