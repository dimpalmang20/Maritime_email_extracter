import re


def clean_text(text):

    # Remove extra spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove special unwanted symbols only
    text = re.sub(r'[^\w\s@:\-\.\n]', '', text)

    # Keep original line structure
    text = text.strip()

    return text