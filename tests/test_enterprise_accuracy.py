from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["MARITIME_SKIP_DB"] = "1"

from extraction.parser import process_email  # noqa: E402
from extraction.field_filters import extract_phone_strict  # noqa: E402
from extraction.schema_contract import STRUCTURED_RECORD_FIELDS  # noqa: E402


def enterprise(text: str) -> dict:
    rows = process_email(text)
    assert rows
    return rows[0]["structured_record"]


def test_enterprise_schema_and_blacklist():
    row = enterprise("Cargo: ALLOWED\nQty: 30,000 mts\nLP: Santos\nDP: Aqaba")
    assert list(row) == list(STRUCTURED_RECORD_FIELDS)
    assert row["email_type"] == "VC"
    assert row["cargo"] == ""
    assert row["load_port"] == ["Santos"]
    assert row["discharge_port"] == ["Aqaba"]


def test_multi_port_quantity_and_laycan_between():
    row = enterprise(
        "Cargo: soybean meal\n"
        "Quantity: 45.000 mts\n"
        "LP: Paranagua or Santos\n"
        "DP: Iskenderun or Durban\n"
        "Laycan: Between 1 July 2025 and 20 July 2025"
    )
    assert row["cargo"] == "Soybean Meal"
    assert row["quantity"] == 45000
    assert row["load_port"] == ["Paranagua", "Santos"]
    assert row["discharge_port"] == ["Iskenderun", "Durban"]
    assert row["laycan_start"] == "2025-07-01"
    assert row["laycan_end"] == "2025-07-20"


def test_multi_cargo_shared_context_mapping_and_phone_filtering():
    rows = process_email(
        "Mobile +91 9523757703\n"
        "Commodity:\n"
        "Maize\n"
        "Soybean Meal\n"
        "Quantity: 30,000 mts +/-10%\n"
        "LP: Paranagua or Santos\n"
        "DP: Aqaba\n"
        "Laycan: 22-25/JUL\n"
        "L/D rates 10000/12000"
    )
    row = rows[0]
    enterprise_row = row["structured_record"]
    assert extract_phone_strict(
        "Mobile +91 9523757703\nL/D rates 10000/12000\n15-18000 mt ferts"
    ) == ["+91 9523757703"]
    assert enterprise_row["cargo"] == "Maize, Soybean Meal"
    assert enterprise_row["quantity"] == 30000
    assert enterprise_row["load_rate"] == "10000"
    assert enterprise_row["discharge_rate"] == "12000"
    assert enterprise_row["tolerance"] == "+/-10%"
    assert len(row["cargo_legs"]) == 2
    assert {leg["cargo_name"] for leg in row["cargo_legs"]} == {"Maize", "Soybean Meal"}
    assert all(leg["quantity"] == 30000 for leg in row["cargo_legs"])


if __name__ == "__main__":
    test_enterprise_schema_and_blacklist()
    test_multi_port_quantity_and_laycan_between()
    test_multi_cargo_shared_context_mapping_and_phone_filtering()
    print("Enterprise accuracy checks passed.")
