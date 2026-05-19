def validate_record(data):

    issues = []


    if not data.get("cargo"):

        issues.append("Cargo Missing")


    if not data.get("load_port"):

        issues.append("Load Port Missing")


    if not data.get("discharge_port"):

        issues.append("Discharge Port Missing")


    if not data.get("quantity"):

        issues.append("Quantity Missing")


    return issues