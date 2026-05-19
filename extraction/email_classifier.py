def classify_email_type(text):

    text = text.lower()


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