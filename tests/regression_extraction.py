"""
Regression checks for maritime email extraction.

Run from repo root:
    python tests/regression_extraction.py

Uses sample_emails/, data/raw_emails/, and tests/fixtures/.
Set MARITIME_SKIP_DB=1 (default in main) to avoid DB writes during tests.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("MARITIME_SKIP_DB", "1")

from extraction.parser import process_email  # noqa: E402
from extraction.schema_contract import validate_enterprise_block  # noqa: E402


def _assert_enterprise_shape(block: dict, label: str) -> None:
    issues = validate_enterprise_block(block)
    assert not issues, f"{label}: schema issues {issues}"


def test_vc_iron_slag() -> None:
    text = (ROOT / "sample_emails" / "vc_email_1.txt").read_text(encoding="utf-8")
    out = process_email(text)
    assert len(out) >= 1, "VC sample: expected >=1 block"
    b = out[0]
    _assert_enterprise_shape(b, "VC")
    assert b.get("cargo"), "VC: cargo expected"
    assert b.get("quantity") is not None, "VC: quantity expected"
    assert b.get("load_port"), "VC: load_port expected"
    assert b.get("discharge_port"), "VC: discharge_port expected"


def test_tc_sample() -> None:
    text = (ROOT / "sample_emails" / "tc_email_1.txt").read_text(encoding="utf-8")
    out = process_email(text)
    assert len(out) >= 1, "TC sample: expected >=1 block"
    b = out[0]
    _assert_enterprise_shape(b, "TC")
    assert b.get("email_type") == "TC", "TC: classifier type"
    assert b.get("dwt"), "TC: DWT expected"
    assert b.get("delivery"), "TC: delivery expected"


def test_tonnage_sample() -> None:
    text = (ROOT / "sample_emails" / "tonnage_email_1.txt").read_text(encoding="utf-8")
    out = process_email(text)
    assert len(out) >= 1, "Tonnage: expected >=1 block"
    b = out[0]
    _assert_enterprise_shape(b, "TONNAGE")
    assert b.get("email_type") == "TONNAGE"
    assert b.get("block_class") in ("VESSEL_OPEN", "VESSEL_HEADER")
    assert b.get("dwt") == "57000" or str(b.get("dwt")) == "57000"
    vn = (b.get("vessel_name") or "").upper()
    assert "SHENG" in vn and "PING" in vn, f"Tonnage: vessel name unexpected: {b.get('vessel_name')}"


def test_multi_cargo_sample() -> None:
    text = (ROOT / "data" / "raw_emails" / "sample_email.txt").read_text(encoding="utf-8")
    out = process_email(text)
    assert len(out) >= 2, "Multi-cargo: expected >=2 fixture blocks"
    cargoes = {str(x.get("cargo") or "").lower() for x in out}
    assert "corn" in cargoes and "coal" in cargoes, f"Multi-cargo: cargoes={cargoes}"
    for i, b in enumerate(out):
        _assert_enterprise_shape(b, f"multi-{i}")


def test_edge_fixture_directory() -> None:
    fix_dir = ROOT / "tests" / "fixtures"
    if not fix_dir.is_dir():
        return
    for path in sorted(fix_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        out = process_email(text)
        if path.name.startswith("edge_technical"):
            assert len(out) == 0, f"{path.name}: technical block must not produce records, got {len(out)}"
            continue
        assert isinstance(out, list) and len(out) >= 1, f"{path.name}: expected >=1 block"
        for i, b in enumerate(out):
            _assert_enterprise_shape(b, f"{path.name}:{i}")


def test_merged_lp_dp_fixture() -> None:
    path = ROOT / "tests" / "fixtures" / "edge_lpdp_merged.txt"
    if not path.exists():
        return
    out = process_email(path.read_text(encoding="utf-8"))
    joined = " ".join(str(b.get("load_port", "")) for b in out).lower()
    assert "paranagua" in joined
    assert any("santos" in str(b.get("discharge_port", "")).lower() for b in out)


def main() -> int:
    test_vc_iron_slag()
    test_tc_sample()
    test_tonnage_sample()
    test_multi_cargo_sample()
    test_edge_fixture_directory()
    test_merged_lp_dp_fixture()
    print("All regression checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
