def detect_template(text):

    text = text.lower()


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

    return detected