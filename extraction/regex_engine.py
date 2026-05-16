import re


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
    pattern = r'(\d{2,3}K)'
    return re.findall(pattern, text)


def extract_lp(text):
    pattern = r'LP:\s*([A-Za-z]+)'
    return re.findall(pattern, text, re.IGNORECASE)


def extract_dp(text):
    pattern = r'DP:\s*([A-Za-z]+)'
    return re.findall(pattern, text, re.IGNORECASE)


def extract_quantity(text):
    pattern = r'(\d{1,3}[,\d]*)\s*mts'
    return re.findall(pattern, text, re.IGNORECASE)


def extract_cargo(text):
    pattern = r'Cargo:\s*([A-Za-z]+)'
    return re.findall(pattern, text, re.IGNORECASE)