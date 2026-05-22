# =========================
# MARITIME CARGO DATABASE
# =========================

CARGO_KEYWORDS = [

    "coal",
    "urea",
    "maize",
    "soybean meal",
    "slag",
    "clinker",
    "rice",
    "steel coils",
    "ferts",
    "iron ore",
    "iron slag",
    "limestone",
    "bulk harmless cargo",
    "calcium carbonate",
    "grain",
    "minerals",
    "bagged rice",
    "petcoke",
    "sulphur",
    "bauxite",
    "nickel ore",
    "cement",
    "corn",
    "npk",
    "fertilizers",
    "steel products",
    "soyabean meal",

]

# Abbreviation / synonym normalization (lowercase key -> canonical cargo name)
CARGO_SYNONYMS = {
    "stl": "steel",
    "stl coils": "steel coils",
    "steel coil": "steel coils",
    "ferts": "fertilizers",
    "fert": "fertilizers",
    "fertilizer": "fertilizers",
    "fertilisers": "fertilizers",
    "fertiliser": "fertilizers",
    "sbm": "soybean meal",
    "soybean meal": "soybean meal",
    "soyabean meal": "soybean meal",
    "iron slag": "iron slag",
    "slag": "iron slag",
    "maize": "maize",
    "corn": "corn",
    "urea": "urea",
}

STRICT_CARGO_BLACKLIST = {
    "allowed",
    "adcom",
    "group",
    "period",
    "type",
    "terms",
    "hold",
    "holds",
    "max",
    "min",
    "full",
    "sole",
    "ready",
    "option",
    "cargo ready",
}

PORT_REGION_MAP = {
    "bik": "Bandar Imam Khomeini",
    "bandar imam khomeini": "Bandar Imam Khomeini",
    "aqaba": "Red Sea",
    "doha": "Arabian Gulf",
    "bushehr": "Arabian Gulf",
    "kuwait": "Arabian Gulf",
    "fujairah": "Arabian Gulf",
    "jebel ali": "Arabian Gulf",
    "paranagua": "South America East Coast",
    "santos": "South America East Coast",
    "san lorenzo": "River Plate",
    "upriver": "River Plate",
    "iskenderun": "East Mediterranean",
    "durban": "South Africa",
    "hodeidah": "Red Sea",
    "pivdenniy": "Black Sea",
    "chittagong": "Bay of Bengal",
    "hazira": "West Coast India",
    "mumbai": "West Coast India",
    "kandla": "West Coast India",
    "lumut": "South East Asia",
    "surabaya": "South East Asia",
    "bahodopi": "South East Asia",
}


# =========================
# PORT DATABASE
# =========================

PORT_KEYWORDS = [

    "bushehr",
    "doha",
    "paranagua",
    "santos",
    "hazira",
    "mumbai",
    "kandla",
    "lumut",
    "iskenderun",
    "durban",
    "hodeidah",
    "upriver",
    "wafr",
    "eci",
    "pg",
    "wci",
    "aqaba",
    "pivdenniy",
    "surabaya",
    "bahodopi",
    "san lorenzo",
    "guangzhou",
    "kuwait",
    "singapore",
    "rotterdam",
    "jebel ali",
    "fujairah",
    "bik",
    "chittagong",

]


# =========================
# VESSEL TYPES
# =========================

VESSEL_TYPES = {

    "bulk carrier": "Bulk Carrier",
    "geared bulk carrier": "Bulk Carrier",
    "single deck bulk carrier": "Bulk Carrier",
    "logger": "Logger Bulk Carrier",

    "smx": "SUPRAMAX",
    "supra": "SUPRAMAX",
    "supramax": "SUPRAMAX",

    "umx": "ULTRAMAX",
    "umax": "ULTRAMAX",
    "ultramax": "ULTRAMAX",

    "panamax": "PANAMAX",

    "hmax": "HANDYMAX",
    "handymax": "HANDYMAX",

    "handysize": "HANDYSIZE",
    "kamsarmax": "KAMSARMAX",
    "capesize": "CAPESIZE"

}


# =========================
# MARITIME ABBREVIATIONS
# =========================

MARITIME_ABBREVIATIONS = {

    "lp": "Load Port",
    "dp": "Discharge Port",
    "pol": "Port of Loading",
    "pod": "Port of Discharge",
    "ttl": "Total Commission",
    "adc": "Address Commission",
    "mts": "Metric Tons",
    "dwt": "Deadweight Tonnage",
    "laycan": "Laydays Cancelling",
    "wog": "Without Guarantee",
    "fio": "Free In Out",
    "fiost": "Free In Out Stowed Trimmed",
    "tct": "Time Charter Trip",
    "dely": "Delivery",
    "redely": "Redelivery",
    "dop": "Dropping Outward Pilot"

}

PORT_ALIASES = {
    "sgp": "singapore",
    "jba": "jebel ali",
    "rot": "rotterdam",
    "slo": "san lorenzo",
}

VESSEL_DWT_RULES = {
    "HANDYSIZE": (10000, 40000),
    "HANDYMAX": (20000, 50000),
    "SUPRAMAX": (45000, 65000),
    "ULTRAMAX": (55000, 70000),
    "PANAMAX": (65000, 90000),
    "KAMSARMAX": (75000, 88000),
    "CAPESIZE": (100000, 220000),
}
