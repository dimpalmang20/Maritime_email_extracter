from extraction.knowledge_base import *


# =========================
# DETECT CARGO
# =========================

def detect_cargo(text):

    detected = []

    for cargo in CARGO_KEYWORDS:

        if cargo.lower() in text.lower():

            detected.append(cargo)

    return detected


# =========================
# DETECT PORTS
# =========================

def detect_ports(text):

    detected = []

    for port in PORT_KEYWORDS:

        if port.lower() in text.lower():

            detected.append(port)

    return detected


# =========================
# DETECT VESSEL TYPE
# =========================

def detect_vessel_type(text):

    for short_form, full_form in VESSEL_TYPES.items():

        if short_form.lower() in text.lower():

            return full_form

    return "Unknown Vessel"


# =========================
# EXPAND ABBREVIATIONS
# =========================

def expand_abbreviations(text):

    expanded = []

    for short, full in MARITIME_ABBREVIATIONS.items():

        if short.lower() in text.lower():

            expanded.append({

                "short_form": short,

                "meaning": full

            })

    return expanded