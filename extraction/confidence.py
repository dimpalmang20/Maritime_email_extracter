def calculate_confidence(data):

    score = 0


    # =========================
    # Cargo
    # =========================

    if data.get("cargo"):

        score += 20


    # =========================
    # Ports
    # =========================

    if data.get("load_port"):

        score += 15

    if data.get("discharge_port"):

        score += 15


    # =========================
    # Quantity
    # =========================

    if data.get("quantity"):

        score += 15


    # =========================
    # Laycan
    # =========================

    if data.get("laycan"):

        score += 10


    # =========================
    # Vessel Type
    # =========================

    if data.get("vessel_type") != "Unknown Vessel":

        score += 10


    # =========================
    # DWT
    # =========================

    if data.get("dwt"):

        score += 10


    # =========================
    # IMO
    # =========================

    if data.get("imo"):

        score += 5


    return min(score, 100)