def classify_cargo(cargo_name):

    if not cargo_name:
        return "Unknown"

    cargo_name = cargo_name.lower().strip()

    agricultural = ["corn", "maize", "soybean meal", "soyabean meal", "rice", "grain", "bagged rice"]
    fertilizer = ["urea", "fertilizers", "npk", "fertilizer"]
    steel = ["steel coils", "steel products"]
    dry_bulk = [
        "coal",
        "iron ore",
        "iron slag",
        "slag",
        "clinker",
        "limestone",
        "bulk harmless cargo",
        "harmless bulk cargo",
        "calcium carbonate",
        "minerals",
        "petcoke",
        "sulphur",
        "bauxite",
        "nickel ore",
        "cement",
    ]
    chemical = ["methanol", "chemical"]
    gas = ["lng", "lpg", "gas"]
    crude = ["crude oil", "oil"]

    if cargo_name in agricultural:
        return "Agricultural Bulk"

    elif cargo_name in fertilizer:
        return "Fertilizer"

    elif cargo_name in steel:
        return "Steel Products"

    elif cargo_name in dry_bulk:
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
