import re


# =========================
# DWT EXTRACTION
# =========================

def extract_dwt_v2(text):

    patterns = [

        r'(\d{2,3}[,\.]?\d{3})\s*dwt',
        r'dwt[:\s]*(\d{2,3}[,\.]?\d{3})',
        r'(\d{2,3})k\s*dwt',
        r'(\d{2,3})\s*k'

    ]

    for pattern in patterns:

        match = re.search(

            pattern,
            text,
            re.IGNORECASE

        )

        if match:

            value = match.group(1)

            value = value.replace(",", "")
            value = value.replace(".", "")

            if len(value) <= 3:

                value = str(int(value) * 1000)

            return value

    return None


# =========================
# IMO EXTRACTION
# =========================

def extract_imo_v2(text):

    pattern = r'imo[\s:\-]*(\d{7})'

    match = re.search(

        pattern,
        text,
        re.IGNORECASE

    )

    if match:

        return match.group(1)

    return None


# =========================
# VESSEL NAME EXTRACTION
# =========================

def extract_vessel_name_v2(text):

    patterns = [

        r'MV\s+([A-Z0-9\-\s]+)',
        r'M/T\s+([A-Z0-9\-\s]+)',
        r'VESSEL[:\s]*([A-Z0-9\-\s]+)'

    ]

    for pattern in patterns:

        match = re.search(

            pattern,
            text,
            re.IGNORECASE

        )

        if match:

            vessel = match.group(1)

            vessel = vessel.split("IMO")[0]

            vessel = vessel.strip()

            return vessel

    return None


# =========================
# OPEN PORT EXTRACTION
# =========================

def extract_open_port_v2(text):

    patterns = [

        r'open[:\s\-]*([A-Z\s]+)',
        r'opn[:\s\-]*([A-Z\s]+)',
        r'position[:\s\-]*([A-Z\s]+)'

    ]

    for pattern in patterns:

        match = re.search(

            pattern,
            text,
            re.IGNORECASE

        )

        if match:

            port = match.group(1)

            port = port.strip()

            return port

    return None


# =========================
# LAYCAN EXTRACTION
# =========================

def extract_laycan_v2(text):

    patterns = [

        r'laycan[:\s]*(\d{1,2}[-/]\d{1,2}\s*[a-zA-Z]+)',

        r'(\d{1,2}[-/]\d{1,2}\s*[a-zA-Z]+)',

        r'(\d{1,2}(st|nd|rd|th)?\s*[-to]+\s*\d{1,2}(st|nd|rd|th)?\s*[a-zA-Z]+)',

    ]

    for pattern in patterns:

        match = re.search(

            pattern,
            text,
            re.IGNORECASE

        )

        if match:

            return match.group(1)

    return None


# =========================
# QUANTITY EXTRACTION
# =========================

def extract_quantity_v2(text):

    patterns = [

        r'(\d{1,3}[,\.]?\d{3})\s*mt',
        r'(\d{1,3}[,\.]?\d{3})\s*mts',
        r'quantity[:\s]*(\d{1,3}[,\.]?\d{3})'

    ]

    for pattern in patterns:

        match = re.search(

            pattern,
            text,
            re.IGNORECASE

        )

        if match:

            qty = match.group(1)

            qty = qty.replace(",", "")
            qty = qty.replace(".", "")

            return qty

    return None