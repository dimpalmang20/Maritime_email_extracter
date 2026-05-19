# convert dates ,quatities , formats
import re
from datetime import datetime


def normalize_quantity(quantity):

    if not quantity:
        return None

    quantity = quantity.replace(",", "")

    return int(quantity)


def normalize_date(date_text):

    try:
        date_obj = datetime.strptime(date_text, "%d-%m %B")
        return date_obj.strftime("%Y-%m-%d")

    except:
        return date_text
    



def clean_port(port):

    if not port:
        return None

    port = port.strip()

    # Remove extra symbols
    port = re.sub(r'[^A-Za-z\\s]', '', port)

    # Title case
    port = port.title()

    return port


def clean_cargo(cargo):

    if not cargo:
        return None

    cargo = cargo.strip()

    cargo = re.sub(r'[^A-Za-z\\s]', '', cargo)

    cargo = cargo.title()

    return cargo


def clean_phone(phone):

    if not phone:
        return None

    # Keep digits only
    phone = re.sub(r'\\D', '', phone)

    return phone


def clean_email(email):

    if not email:
        return None

    email = email.strip().lower()

    return email