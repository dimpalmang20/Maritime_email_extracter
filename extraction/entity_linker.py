def build_cargo_legs(
    cargo_entries,
    quantity_entries,
    port_entries,
    laycan_data
):

    cargo_legs = []

    max_len = max(
        len(cargo_entries),
        len(quantity_entries),
        len(port_entries),
        1
    )

    for i in range(max_len):

        cargo = None
        qty = None
        lp = None
        dp = None

        if i < len(cargo_entries):
            cargo = cargo_entries[i].get("cargo_name")

        if i < len(quantity_entries):
            qty = quantity_entries[i].get("quantity")

        if i < len(port_entries):
            lp = port_entries[i].get("load_port")
            dp = port_entries[i].get("discharge_port")

        leg = {
            "cargo_name": cargo,
            "quantity": qty,
            "load_port": lp,
            "discharge_port": dp,
            "laycan_start": laycan_data.get("start"),
            "laycan_end": laycan_data.get("end")
        }

        cargo_legs.append(leg)

    return cargo_legs

import re


# =========================================================
# ENTERPRISE TRADE FLOW LINKER
# =========================================================

def build_trade_flow(block_text, extracted):

    trade = {

        "cargo": extracted.get("cargo"),
        "quantity": extracted.get("quantity"),
        "load_port": extracted.get("load_port"),
        "discharge_port": extracted.get("discharge_port"),
        "delivery": extracted.get("delivery"),
        "redelivery": extracted.get("redelivery"),
        "duration": extracted.get("duration"),
        "vessel_type": extracted.get("vessel_type"),
        "open_port": extracted.get("open_port"),
        "open_date": extracted.get("open_date"),

        "confidence_boost": 0,
        "email_type": "UNKNOWN",

    }

    text = (block_text or "").lower()

    # =========================================================
    # TC FLOW VALIDATION
    # =========================================================

    tc_hits = 0

    if trade["delivery"]:
        tc_hits += 1

    if trade["redelivery"]:
        tc_hits += 1

    if trade["duration"]:
        tc_hits += 1

    if re.search(
        r"\b(tct|time charter|period|trip|delivery|redelivery)\b",
        text,
        re.I,
    ):
        tc_hits += 1

    if tc_hits >= 3:

        trade["confidence_boost"] += 25
        trade["email_type"] = "TC"

    # =========================================================
    # VC FLOW VALIDATION
    # =========================================================

    vc_hits = 0

    if trade["cargo"]:
        vc_hits += 1

    if trade["quantity"]:
        vc_hits += 1

    if trade["load_port"]:
        vc_hits += 1

    if trade["discharge_port"]:
        vc_hits += 1

    if re.search(
        r"\b(cargo|commodity|qty|quantity|lp|dp|pol|pod)\b",
        text,
        re.I,
    ):
        vc_hits += 1

    if vc_hits >= 3:

        trade["confidence_boost"] += 25

        if trade["email_type"] == "UNKNOWN":
            trade["email_type"] = "VC"

    # =========================================================
    # TONNAGE FLOW VALIDATION
    # =========================================================

    tonnage_hits = 0

    if trade["open_port"]:
        tonnage_hits += 1

    if trade["open_date"]:
        tonnage_hits += 1

    if extracted.get("vessel_name"):
        tonnage_hits += 1

    if extracted.get("dwt"):
        tonnage_hits += 1

    if re.search(
        r"\b(open|spot|prompt|position|tonnage)\b",
        text,
        re.I,
    ):
        tonnage_hits += 1

    if tonnage_hits >= 3:

        trade["confidence_boost"] += 30
        trade["email_type"] = "TONNAGE"

    # =========================================================
    # VESSEL SPEC FLOW
    # =========================================================

    spec_hits = 0

    if extracted.get("grt"):
        spec_hits += 1

    if extracted.get("nrt"):
        spec_hits += 1

    if extracted.get("loa"):
        spec_hits += 1

    if extracted.get("beam"):
        spec_hits += 1

    if re.search(
        r"\b(speed|consumption|bunkers|lsfo|ifo|mgo|grabs|cranes)\b",
        text,
        re.I,
    ):
        spec_hits += 1

    if spec_hits >= 3:

        trade["confidence_boost"] += 15

    # =========================================================
    # FINAL VALIDATION
    # =========================================================

    # impossible VC without ports
    if trade["email_type"] == "VC":

        if not trade["load_port"] and not trade["discharge_port"]:

            trade["confidence_boost"] -= 20

    # impossible TC without duration
    if trade["email_type"] == "TC":

        if not trade["duration"]:

            trade["confidence_boost"] -= 20

    return trade