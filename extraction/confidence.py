def _email_type_upper(data):
    raw = data.get("email_type")
    if isinstance(raw, dict):
        raw = raw.get("email_type")
    return str(raw or "").strip().upper()


def calculate_confidence(data):
    """Weighted confidence by fixture type with semantic penalties."""
    et = _email_type_upper(data)
    score = 0

    laycan_signal = bool(
        data.get("laycan")
        or (data.get("laycan_start") and data.get("laycan_end"))
    )

    # --- Core enterprise signals requested by the extraction contract ---
    if data.get("vessel_name"):
        score += 20
    if data.get("dwt"):
        score += 20
    if data.get("imo"):
        score += 15
    if data.get("open_port"):
        score += 15
    if data.get("cargo"):
        score += 15
    if data.get("quantity"):
        score += 15

    if laycan_signal:
        score += 10

    # --- VC / default voyage cargo ---
    if et in ("VC", "", "UNKNOWN"):
        if data.get("load_port"):
            score += 15
        if data.get("discharge_port"):
            score += 15
        if data.get("cargo") and data.get("quantity") and data.get("load_port") and data.get("discharge_port"):
            score += 15
        if data.get("vessel_type") and data.get("vessel_type") != "Unknown Vessel":
            score += 10

        legs = data.get("cargo_legs") or []
        if legs:
            complete_legs = 0
            partial_legs = 0
            for leg in legs:
                present = sum(
                    [
                        bool(leg.get("cargo_name")),
                        bool(leg.get("quantity")),
                        bool(leg.get("load_port")),
                        bool(leg.get("discharge_port")),
                    ]
                )
                if present >= 3:
                    complete_legs += 1
                elif present > 0:
                    partial_legs += 1

            score += min(20, complete_legs * 8)
            score -= min(10, partial_legs * 3)

    # --- Time charter ---
    elif et == "TC":
        if data.get("delivery"):
            score += 16
        if data.get("redelivery"):
            score += 12
        if data.get("duration"):
            score += 10
        if data.get("commission"):
            score += 6
        if data.get("vessel_type") and data.get("vessel_type") != "Unknown Vessel":
            score += 12
        if data.get("cargo") and data.get("delivery") and data.get("redelivery") and data.get("duration"):
            score += 10

        legs = data.get("cargo_legs") or []
        if legs:
            cargo_hints = sum(1 for leg in legs if leg.get("cargo_name"))
            score += min(12, cargo_hints * 6)

    # --- Open tonnage / vessel offer ---
    elif et == "TONNAGE":
        if data.get("vessel_type") and data.get("vessel_type") != "Unknown Vessel":
            score += 12
        if data.get("open_date"):
            score += 10
        if data.get("vessel_name") and data.get("dwt") and (data.get("open_port") or data.get("open_date")):
            score += 15

    else:
        # Unknown classifier bucket: blend VC weights lightly
        if data.get("cargo"):
            score += 15
        if data.get("load_port"):
            score += 10
        if data.get("discharge_port"):
            score += 10
        if data.get("quantity"):
            score += 10
        if data.get("dwt"):
            score += 10

    issues = data.get("validation_issues") or []
    score -= min(18, len(issues) * 3)
    noisy_entities = len(data.get("entities") or [])
    if noisy_entities > 8:
        score -= min(15, (noisy_entities - 8) * 2)
    for issue in issues:
        low = str(issue).lower()
        if "fake" in low or "invalid" in low or "unverified" in low or "impossible" in low:
            score -= 5

    return max(0, min(score, 100))
