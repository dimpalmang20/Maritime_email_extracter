# convert dates ,quatities , formats

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