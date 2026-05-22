"""
Regression tests for the 11 documented precision failures.
Run: python tests/test_precision_failures.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["MARITIME_SKIP_DB"] = "1"

from extraction.parser import process_email  # noqa: E402
from extraction.field_filters import extract_phone_strict  # noqa: E402


def _one(text: str):
    out = process_email(text)
    return out[0] if out else {}


def test_failure_1_ferts_tonnage_not_phone():
    b = _one("15-18'000 mt ferts")
    assert b.get("phones") in ([], None) or len(b.get("phones") or []) == 0
    assert b.get("quantity") in (18000, "18000")
    assert "fert" in (b.get("cargo") or "").lower()


def test_failure_2_loading_port_lumut():
    b = _one("LOADING PORT : LUMUT")
    lp = b.get("load_port") or ""
    assert "lumut" in lp.lower(), f"got {lp!r}"


def test_failure_3_stl_coils():
    b = _one("4400MT STL COILS")
    assert b.get("quantity") in (4400, "4400")
    assert "steel" in (b.get("cargo") or "").lower()


def test_failure_4_iron_slag_range():
    b = _one("20-30,000 mts iron slag")
    assert b.get("quantity") in (30000, "30000")
    assert "slag" in (b.get("cargo") or "").lower()


def test_failure_5_load_discharge_rates():
    b = _one("5000/5000")
    assert not b.get("phones") or b.get("phones") == []
    assert b.get("load_rate") == 5000
    assert b.get("discharge_rate") == 5000


def test_failure_6_tolerance_not_phone():
    b = _one("30,000 +-10% metric tons")
    assert not b.get("phones") or len(b.get("phones") or []) == 0
    assert b.get("quantity") in (30000, "30000")
    assert b.get("tolerance")


def test_failure_7_lp_or_ports():
    b = _one("LP: Paranagua or santos")
    lp = b.get("load_port") or ""
    assert "paranagua" in lp.lower()
    assert "santos" in lp.lower()


def test_failure_8_european_decimal():
    b = _one("45.000 mts Soybean meal")
    assert b.get("quantity") in (45000, "45000"), f"qty={b.get('quantity')}"


def test_failure_9_multi_commodity():
    text = "Commodity:\nMaize\nSoybean Meal"
    out = process_email(text)
    cargoes = [str(x.get("cargo") or "").lower() for x in out]
    joined = " ".join(cargoes)
    assert "maize" in joined
    assert "soybean" in joined
    assert "corn" not in joined or "maize" in joined


def test_failure_10_phones_strict():
    phones = extract_phone_strict("15-18000 mt ferts")
    assert phones == []


def test_failure_11_no_bullet_qty():
    b = _one("1. First item\n2. Second\n4. Fourth\nno cargo here")
    assert b.get("quantity") not in (1, 2, 4, "1", "2", "4") or b == {}


def test_vessel_spec_not_cargo_fixture():
    text = """MV ADRE
BULK CARRIER
IMO: 9876543
DWT: 56800
GRT: 35,812
NRT: 20,400
LOA: 189.99
BEAM: 32.26
GRAIN CAPACITY: 70,123 CBM
BALE CAPACITY: 68,500 CBM
5 HOLDS / 5 HATCHES
OPEN GUANGZHOU 30TH JUL 2025"""
    b = _one(text)
    assert b.get("template_type") == "TONNAGE"
    assert b.get("email_type") == "TONNAGE"
    assert b.get("cargo") in (None, "")
    assert b.get("quantity") in (None, "")
    assert b.get("dwt") in ("56800", 56800)
    assert b.get("open_date") == "2025-07-30"


def main():
    tests = [
        test_failure_1_ferts_tonnage_not_phone,
        test_failure_2_loading_port_lumut,
        test_failure_3_stl_coils,
        test_failure_4_iron_slag_range,
        test_failure_5_load_discharge_rates,
        test_failure_6_tolerance_not_phone,
        test_failure_7_lp_or_ports,
        test_failure_8_european_decimal,
        test_failure_9_multi_commodity,
        test_failure_10_phones_strict,
        test_failure_11_no_bullet_qty,
        test_vessel_spec_not_cargo_fixture,
    ]
    failed = []
    for t in tests:
        try:
            t()
            print("OK", t.__name__)
        except AssertionError as e:
            failed.append((t.__name__, str(e)))
            print("FAIL", t.__name__, e)
    if failed:
        raise SystemExit(1)
    print("All precision failure tests passed.")


if __name__ == "__main__":
    main()
