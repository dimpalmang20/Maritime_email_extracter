import re
from extraction.knowledge_base import CARGO_KEYWORDS
from extraction.knowledge_base import PORT_KEYWORDS

def extract_email(text):
    pattern = r'[\w\.-]+@[\w\.-]+'
    return re.findall(pattern, text)


def extract_phone(text):
    pattern = r'\+?\d[\d\s\-]{8,15}'
    return re.findall(pattern, text)


def extract_laycan(text):
    pattern = r'Laycan:\s*([\d\-]+\s*[A-Za-z]+)'
    return re.findall(pattern, text, re.IGNORECASE)


def extract_dwt(text):

    pattern = r'(\\d{4,6})\\s*DWT'

    result = re.findall(pattern, text, re.IGNORECASE)

    return result

def extract_lp(text):

    text = text.lower()

    for port in PORT_KEYWORDS:

        if port in text:

            return port.title()

    return None




def extract_dp(text):

    text = text.lower()

    for port in PORT_KEYWORDS:

        if port in text:

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