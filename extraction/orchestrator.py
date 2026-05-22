from extraction.hybrid_extractor import hybrid_extract

from extraction.llm_fallback import send_to_llm
from extraction.confidence import calculate_confidence


def orchestrate_extraction(text):

    result = hybrid_extract(text)

    regex_data = result["regex_extraction"]

    ml_entities = result["ml_entities"]

    orchestration_payload = {
        "cargo": regex_data.get("cargo"),
        "load_port": regex_data.get("load_port"),
        "discharge_port": regex_data.get("discharge_port"),
        "dwt": regex_data.get("dwt"),
        "laycan": regex_data.get("laycan"),
        "vessel_type": "Unknown Vessel",
        "imo": None,
        "cargo_legs": [
            {
                "cargo_name": item.get("cargo_name"),
                "quantity": (regex_data.get("quantity_entries") or [{}])[idx].get("quantity")
                if idx < len(regex_data.get("quantity_entries") or [])
                else None,
                "load_port": (regex_data.get("port_pairs") or [{}])[idx].get("load_port")
                if idx < len(regex_data.get("port_pairs") or [])
                else None,
                "discharge_port": (regex_data.get("port_pairs") or [{}])[idx].get("discharge_port")
                if idx < len(regex_data.get("port_pairs") or [])
                else None,
            }
            for idx, item in enumerate(regex_data.get("cargo_entries") or [])
        ],
        "validation_issues": [],
    }
    confidence_score = calculate_confidence(orchestration_payload)
    if len(ml_entities) > 0:
        confidence_score = min(100, confidence_score + 5)


    # FINAL DECISION

    if confidence_score >= 80:

        status = "HIGH_CONFIDENCE"

        final_result = regex_data

    elif confidence_score >= 50:

        status = "MEDIUM_CONFIDENCE"

        final_result = {

            "regex_data": regex_data,

            "ml_entities": ml_entities
        }

    else:

        status = "LOW_CONFIDENCE"

        llm_result = send_to_llm(text)

        final_result = {

            "fallback_ai": llm_result
        }


    return {

        "confidence_score": confidence_score,

        "status": status,

        "final_result": final_result
    }