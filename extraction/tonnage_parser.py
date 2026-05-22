from extraction.regex_engine_v2 import *
from extraction.semantic_rules import normalize_vessel_type


def parse_tonnage(block):

    vessel_name = extract_vessel_name_v2(block)

    imo = extract_imo_v2(block)

    dwt = extract_dwt_v2(block)

    open_port = extract_open_port_v2(block)

    open_date = extract_open_date_v2(block)

    vessel_type = normalize_vessel_type(block)

    return {

        "email_type": "TONNAGE",

        "vessel_name": vessel_name,

        "imo": imo,

        "dwt": dwt,

        "open_port": open_port,

        "open_date": open_date,

        "vessel_type": vessel_type
    }