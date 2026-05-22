def classify_email_type(text):

    text = text.lower()
    from extraction.semantic_rules import is_vessel_spec_text

    if is_vessel_spec_text(text) or (
        ("dwt" in text or "deadweight" in text)
        and ("open" in text or "prompt" in text or "spot" in text or "built" in text or "imo" in text)
    ):
        return {"email_type": "TONNAGE", "scores": {"VC": 0, "TC": 0, "TONNAGE": 99}}

    if any(k in text for k in ("delivery", "redelivery", "redel", "duration", "time charter", "tct")):
        return {"email_type": "TC", "scores": {"VC": 0, "TC": 99, "TONNAGE": 0}}


    # VC patterns

    vc_keywords = [

        "cargo",
        "lp:",
        "dp:",
        "pol:",
        "pod:",
        "mts",
        "commodity"
    ]


    # TC patterns

    tc_keywords = [

        "tct",
        "delivery",
        "redelivery",
        "duration",
        "wog",
        "laycan"
    ]


    # TONNAGE patterns

    tonnage_keywords = [

        "mv ",
        "open ",
        "dwt",
        "built",
        "grt",
        "bulk carrier"
    ]


    vc_score = sum(
        keyword in text
        for keyword in vc_keywords
    )

    tc_score = sum(
        keyword in text
        for keyword in tc_keywords
    )

    tonnage_score = sum(
        keyword in text
        for keyword in tonnage_keywords
    )


    scores = {

        "VC": vc_score,

        "TC": tc_score,

        "TONNAGE": tonnage_score
    }


    detected_type = max(
        scores,
        key=scores.get
    )


    return {

        "email_type": detected_type,

        "scores": scores
    }
