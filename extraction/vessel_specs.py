import re


# =========================================
# GENERIC NUMBER NORMALIZER
# =========================================

def normalize_spec_number(value):

    if not value:
        return None

    value = str(value)

    value = value.replace(",", "")
    value = value.replace("'", "")
    value = value.strip()

    try:

        if "." in value:
            return float(value)

        return int(value)

    except:
        return value


# =========================================
# IMO EXTRACTION
# =========================================

def extract_imo(text):

    patterns = [

        r'(?i)\bimo(?:\s*no)?[\s:\-#]*([0-9]{7})\b',

        r'(?i)\bimo[\s]+([0-9]{7})\b',

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            imo = match.group(1)

            if len(imo) == 7:
                return imo

    return None


# =========================================
# GRT EXTRACTION
# =========================================

def extract_grt(text):

    patterns = [

        r'(?i)\bgrt[\s:\-]*([0-9,\.]+)\b',

        r'(?i)\bgross\s*registered\s*tonnage[\s:\-]*([0-9,\.]+)\b',

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            return normalize_spec_number(match.group(1))

    return None


# =========================================
# NRT EXTRACTION
# =========================================

def extract_nrt(text):

    patterns = [

        r'(?i)\bnrt[\s:\-]*([0-9,\.]+)\b',

        r'(?i)\bnet\s*registered\s*tonnage[\s:\-]*([0-9,\.]+)\b',

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            return normalize_spec_number(match.group(1))

    return None


# =========================================
# LOA EXTRACTION
# =========================================

def extract_loa(text):

    patterns = [

        r'(?i)\bloa[\s:\-]*([0-9,\.]+)\s*(?:m|meter|meters)?\b',

        r'(?i)\blength\s*overall[\s:\-]*([0-9,\.]+)\b',

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            loa = normalize_spec_number(match.group(1))

            try:

                if float(loa) < 50:
                    continue

                if float(loa) > 400:
                    continue

            except:
                pass

            return loa

    return None


# =========================================
# BEAM EXTRACTION
# =========================================

def extract_beam(text):

    patterns = [

        r'(?i)\bbeam[\s:\-]*([0-9,\.]+)\s*(?:m|meter|meters)?\b',

        r'(?i)\bmoulded\s*beam[\s:\-]*([0-9,\.]+)\b',

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            beam = normalize_spec_number(match.group(1))

            try:

                if float(beam) < 5:
                    continue

                if float(beam) > 80:
                    continue

            except:
                pass

            return beam

    return None


# =========================================
# GRAIN CAPACITY
# =========================================

def extract_grain_capacity(text):

    patterns = [

        r'(?i)\bgrain\s*capacity[\s:\-]*([0-9,\.]+)\s*(?:cbm|cbft)?\b',

        r'(?i)\bgrain[\s:\-]*([0-9,\.]+)\s*(?:cbm|cbft)?\b',

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            val = normalize_spec_number(match.group(1))

            try:

                if float(val) < 1000:
                    continue

            except:
                pass

            return val

    return None


# =========================================
# BALE CAPACITY
# =========================================

def extract_bale_capacity(text):

    patterns = [

        r'(?i)\bbale\s*capacity[\s:\-]*([0-9,\.]+)\s*(?:cbm|cbft)?\b',

        r'(?i)\bbale[\s:\-]*([0-9,\.]+)\s*(?:cbm|cbft)?\b',

    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            val = normalize_spec_number(match.group(1))

            try:

                if float(val) < 1000:
                    continue

            except:
                pass

            return val

    return None


# =========================================
# FULL VESSEL SPEC EXTRACTION
# =========================================

def extract_vessel_specs(text):

    return {

        "imo": extract_imo(text),

        "grt": extract_grt(text),

        "nrt": extract_nrt(text),

        "loa": extract_loa(text),

        "beam": extract_beam(text),

        "grain_capacity": extract_grain_capacity(text),

        "bale_capacity": extract_bale_capacity(text),

    }