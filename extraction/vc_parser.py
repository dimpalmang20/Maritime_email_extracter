from extraction.regex_engine_v2 import *
from extraction.entity_linker import build_cargo_legs
from extraction.classifier import classify_cargo


def parse_voyage_charter(block):

    cargo_entries = extract_cargo_entries_v2(block)

    quantity_entries = extract_quantities_v2(block)

    port_entries = extract_port_pairs_v2(block)

    laycan = extract_laycan_range_v2(block)

    cargo_legs = build_cargo_legs(
        cargo_entries,
        quantity_entries,
        port_entries,
        laycan
    )

    cargo = None
    cargo_type = "Unknown"

    if cargo_legs:

        cargo = cargo_legs[0].get("cargo_name")

        cargo_type = classify_cargo(cargo)

    quantity = None

    if cargo_legs:
        quantity = cargo_legs[0].get("quantity")

    load_port = None
    discharge_port = None

    if cargo_legs:

        load_port = cargo_legs[0].get("load_port")

        discharge_port = cargo_legs[0].get("discharge_port")

    return {

        "email_type": "VC",

        "cargo": cargo,

        "cargo_type": cargo_type,

        "quantity": quantity,

        "load_port": load_port,

        "discharge_port": discharge_port,

        "cargo_legs": cargo_legs
    }