import re


def clean_text(text):

    # Remove extra spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Keep maritime tonnage/rate/tolerance punctuation (/ + % ')
    text = re.sub(r"[^\w\s@:\-\.\n/+%',&]", "", text)

    # Keep original line structure
    text = text.strip()

    return text
