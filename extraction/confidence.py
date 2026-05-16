def calculate_confidence(data):

    score = 0

    total_fields = 5

    if data.get("cargo"):
        score += 1

    if data.get("load_port"):
        score += 1

    if data.get("discharge_port"):
        score += 1

    if data.get("quantity"):
        score += 1

    if data.get("laycan"):
        score += 1

    confidence = (score / total_fields) * 100

    return round(confidence, 2)