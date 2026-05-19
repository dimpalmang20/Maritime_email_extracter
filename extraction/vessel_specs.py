import re


def extract_imo(text):

    pattern = r"IMO[:\s\-]*([0-9]{7})"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1) if match else None


def extract_grt(text):

    pattern = r"GRT[:\s\-]*([0-9,\.]+)"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1) if match else None


def extract_nrt(text):

    pattern = r"NRT[:\s\-]*([0-9,\.]+)"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1) if match else None


def extract_loa(text):

    pattern = r"LOA[:\s\-]*([0-9,\.]+)"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1) if match else None


def extract_beam(text):

    pattern = r"BEAM[:\s\-]*([0-9,\.]+)"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1) if match else None


def extract_grain_capacity(text):

    pattern = r"GRAIN CAPACITY[:\s\-]*([0-9,\.]+)"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1) if match else None


def extract_bale_capacity(text):

    pattern = r"BALE CAPACITY[:\s\-]*([0-9,\.]+)"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(1) if match else None