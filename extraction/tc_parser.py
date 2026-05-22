import re


def parse_tc(block):

    delivery = None
    redelivery = None
    duration = None

    delivery_match = re.search(
        r'(?i)delivery\s*[:\-]?\s*([^\n]+)',
        block
    )

    if delivery_match:
        delivery = delivery_match.group(1).strip()

    redelivery_match = re.search(
        r'(?i)redelivery\s*[:\-]?\s*([^\n]+)',
        block
    )

    if redelivery_match:
        redelivery = redelivery_match.group(1).strip()

    duration_match = re.search(
        r'(?i)(\d+\s*-\s*\d+\s*days)',
        block
    )

    if duration_match:
        duration = duration_match.group(1)
    # =========================================
# ENTERPRISE TC SEMANTIC EXTRACTION
# =========================================

    delivery = None
    redelivery = None
    duration = None

# DELIVERY
    delivery_patterns = [

        r'(?i)\bdely(?:ivery)?\s*[:\-]?\s*([^\n]+)',
        r'(?i)\bdelivery\s*[:\-]?\s*([^\n]+)',

    ]

    for pattern in delivery_patterns:

        match = re.search(pattern, block)

        if match:

            delivery = match.group(1).strip()

            delivery = re.sub(
                r'(?i)\bwog\b',
                '',
                delivery
           )

            delivery = delivery.strip(" -:/")

            break

# REDELIVERY
    redelivery_patterns = [

        r'(?i)\bredely(?:ivery)?\s*[:\-]?\s*([^\n]+)',
        r'(?i)\bredelivery\s*[:\-]?\s*([^\n]+)',

     ]

    for pattern in redelivery_patterns:

        match = re.search(pattern, block)

        if match:

            redelivery = match.group(1).strip()

            redelivery = re.sub(
               r'(?i)\bwog\b',
               '',
               redelivery
           )

            redelivery = redelivery.strip(" -:/")

            break

# DURATION
    duration_patterns = [

        r'(?i)\b(?:abt|about)?\s*(\d{1,3}\s*(?:days?|dys|months?|mos))\s*wog',

        r'(?i)\bduration\s*[:\-]?\s*([^\n]+)',

    ]

    for pattern in duration_patterns:

        match = re.search(pattern, block)

        if match:

           duration = match.group(1).strip()

           duration = duration.strip(" -:/")

           break
    return {

        "email_type": "TC",

        "delivery": delivery,

        "redelivery": redelivery,

        "duration": duration
    }