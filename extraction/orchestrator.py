from extraction.hybrid_extractor import hybrid_extract

from extraction.llm_fallback import send_to_llm


def orchestrate_extraction(text):

    result = hybrid_extract(text)

    regex_data = result["regex_extraction"]

    ml_entities = result["ml_entities"]

    confidence_score = 0


    # REGEX CONFIDENCE

    if regex_data["cargo"]:
        confidence_score += 20

    if regex_data["load_port"]:
        confidence_score += 20

    if regex_data["discharge_port"]:
        confidence_score += 20

    if regex_data["dwt"]:
        confidence_score += 20

    if regex_data["laycan"]:
        confidence_score += 20


    # ML BONUS

    if len(ml_entities) > 0:
        confidence_score += 10


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