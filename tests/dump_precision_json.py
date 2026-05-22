"""Dump JSON for precision cases and sample emails."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["MARITIME_SKIP_DB"] = "1"

from extraction.parser import process_email  # noqa: E402

KEYS = (
    "cargo",
    "quantity",
    "load_port",
    "discharge_port",
    "phones",
    "load_rate",
    "discharge_rate",
    "tolerance",
    "cargo_legs",
    "extraction_status",
    "confidence_score",
)


def slim(rec):
    return {k: rec.get(k) for k in KEYS if k in rec}


cases = {
    "failure_1": "15-18'000 mt ferts",
    "failure_2": "LOADING PORT : LUMUT",
    "failure_3": "4400MT STL COILS",
    "failure_4": "20-30,000 mts iron slag",
    "failure_5": "5000/5000",
    "failure_6": "30,000 +-10% metric tons",
    "failure_7": "LP: Paranagua or santos",
    "failure_8": "45.000 mts Soybean meal",
    "failure_9": "Commodity:\nMaize\nSoybean Meal",
}

out = {k: [slim(r) for r in process_email(v)] for k, v in cases.items()}

for p in sorted((ROOT / "sample_emails").glob("*.txt")):
    text = p.read_text(encoding="utf-8", errors="ignore")
    rows = process_email(text)
    out[p.name] = {
        "records": len(rows),
        "samples": [slim(r) for r in rows[:3]],
    }

path = ROOT / "output" / "precision_results.json"
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
print(path)
print(json.dumps(out, indent=2, default=str))
