def classify_cargo(cargo_name):

    cargo_name = cargo_name.lower()

    dry_bulk = ["corn", "coal", "iron ore", "slag"]
    chemical = ["methanol", "chemical"]
    gas = ["lng", "lpg", "gas"]
    crude = ["crude oil", "oil"]

    if cargo_name in dry_bulk:
        return "Dry Bulk"

    elif cargo_name in chemical:
        return "Chemical"

    elif cargo_name in gas:
        return "Gas"

    elif cargo_name in crude:
        return "Crude Oil"

    return "Unknown"

def classify_vessel(dwt_value):

    try:

        dwt_value = int(dwt_value)

        if 20000 <= dwt_value < 40000:
            return "Handymax"

        elif 40000 <= dwt_value < 60000:
            return "Supramax"

        elif 60000 <= dwt_value < 65000:
            return "Ultramax"

        elif 65000 <= dwt_value < 85000:
            return "Panamax"

        else:
            return "Unknown Vessel Type"

    except:
        return "Unknown Vessel Type"