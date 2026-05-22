import re
from extraction.knowledge_base import CARGO_KEYWORDS
from extraction.knowledge_base import PORT_KEYWORDS

def extract_email(text):
    pattern = r'[\w\.-]+@[\w\.-]+'
    return re.findall(pattern, text)


def extract_phone(text):
    from extraction.field_filters import extract_phone_strict
    return extract_phone_strict(text)


def extract_laycan(text):
    pattern = r'Laycan:\s*([\d\-]+\s*[A-Za-z]+)'
    return re.findall(pattern, text, re.IGNORECASE)


def extract_dwt(text):

    pattern = r'(\\d{4,6})\\s*DWT'

    result = re.findall(pattern, text, re.IGNORECASE)

    return result

def extract_lp(text):
    from extraction.maritime_parse import extract_labeled_ports

    lp_list, _ = extract_labeled_ports(text)
    if lp_list:
        return [p.title() for p in lp_list]
    lowered = text.lower()
    for port in PORT_KEYWORDS:
        if re.search(rf'(?i)\bfrom\s+{re.escape(port)}\b', lowered):
            return port.title()
    return None




def extract_dp(text):
    from extraction.maritime_parse import extract_labeled_ports

    _, dp_list = extract_labeled_ports(text)
    if dp_list:
        return [p.title() for p in dp_list]
    lowered = text.lower()
    for port in PORT_KEYWORDS:
        if re.search(rf'(?i)\bto\s+{re.escape(port)}\b', lowered):
            return port.title()
    return None


def extract_quantity(text):
    pattern = r'(\d{1,3}[,\d]*)\s*mts'
    return re.findall(pattern, text, re.IGNORECASE)


def extract_cargo(text):

    text = text.lower()

    found_cargo = []


    for cargo in CARGO_KEYWORDS:

        if cargo in text:

            found_cargo.append(cargo)

    return found_cargo