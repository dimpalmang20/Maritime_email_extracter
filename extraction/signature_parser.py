import re


def extract_signature(text):

    email_pattern = r'[\w\.-]+@[\w\.-]+'
    phone_pattern = r'\+?\d[\d\s\-]{8,15}'

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    # Extract possible names
    lines = text.splitlines()

    names = []

    for line in lines:
        line = line.strip()

        if (
            len(line.split()) <= 3
            and line.isascii()
            and not any(char.isdigit() for char in line)
            and "@" not in line
            and len(line) > 2
        ):
            names.append(line)

    return {
        "emails": emails,
        "phones": phones,
        "names": names
    }