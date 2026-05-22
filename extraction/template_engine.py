def detect_template(text):

    text = text.lower()
    from extraction.semantic_rules import is_vessel_spec_text

    # Priority classifier: vessel spec/open evidence overrides cargo words.
    if is_vessel_spec_text(text) or (
        ("dwt" in text or "deadweight" in text)
        and ("open" in text or "prompt" in text or "spot" in text or "built" in text or "imo" in text)
    ):
        return "TONNAGE"

    if any(k in text for k in ("delivery", "redelivery", "redel", "duration", "time charter", "tct")):
        return "TC"


    # =========================
    # VC CARGO
    # =========================

    vc_keywords = [

        "cargo",
        "commodity",
        "lp:",
        "dp:",
        "pol:",
        "pod:",
        "mts",
        "mt",
        "fios",
       "fiost",
       "load port",
    "discharge port",
     "cargo readiness",
       " shipment"

    ]


    # =========================
    # TC CARGO
    # =========================

    tc_keywords = [

        "delivery",
        "redelivery",
        "duration",
        "tct",
        "trip",
        "wog",
        "time charter",
        "days wog"

    ]


    # =========================
    # TONNAGE
    # =========================

    tonnage_keywords = [

        "open",
        "position",
        "mv",
        "m/t",
        "ballast",
        "prompt",
        "open kandla",
        "open busan",
        "position open",
        "spot vessel",
        "can lift"

    ]


    vc_score = 0
    tc_score = 0
    tonnage_score = 0


    # VC SCORE

    for keyword in vc_keywords:

        if keyword in text:

            vc_score += 1


    # TC SCORE

    for keyword in tc_keywords:

        if keyword in text:

            tc_score += 1


    # TONNAGE SCORE

    for keyword in tonnage_keywords:

        if keyword in text:

            tonnage_score += 1


    scores = {

        "VC_CARGO": vc_score,

        "TC_CARGO": tc_score,

        "TONNAGE": tonnage_score

    }


    detected = max(scores, key=scores.get)
    if detected == "VC_CARGO":
        return "VC"
    if detected == "TC_CARGO":
        return "TC"

    return detected
