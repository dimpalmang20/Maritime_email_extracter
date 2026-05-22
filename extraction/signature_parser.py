import re
from extraction.normalization import clean_phone, clean_email
from extraction.field_filters import extract_phone_strict

def extract_signature(text):

    email_pattern = r'[\w\.-]+@[\w\.-]+'

    emails = re.findall(email_pattern, text)
    phones = extract_phone_strict(text)

    # Extract possible names
    lines = text.splitlines()

    names = []

    for line in lines:
        line = line.strip()
        low = line.lower()

        if any(x in low for x in [

    "mob:",
    "mobile:",
    "whatsapp",
    "email:",
    "website:",
    "skype:",
    "teams",
    ".com",
    "@",

]):
           continue

        if re.search(r"\+?\d[\d\s\-]{7,}", line):
            continue

        if (

           len(line.split()) <= 5
           and line.isascii()
           and not any(char.isdigit() for char in line)
           and "@" not in line
           and len(line) > 2

    # =====================================
    # ENTERPRISE MARITIME FILTERS
    # =====================================

           and not re.search(

               r'(?i)\b(?:'

               r'dely|delivery|redely|redelivery|'

               r'duration|laycan|cargo|quantity|'

               r'lp|dp|pol|pod|'

               r'open|dwt|imt|umt|'

               r'tct|trip|period|'

               r'goa|gib|emed|wmed|bsea|'

               r'cogh|arag|wcca|eci|wci'

               r')\b',

               line

    )

):

         names.append(line)

    cleaned_emails = [clean_email(email) for email in emails]

    cleaned_phones = [clean_phone(phone) for phone in phones if clean_phone(phone)]

    return {
    "emails": cleaned_emails,
    "phones": cleaned_phones,
    "names": names
    }