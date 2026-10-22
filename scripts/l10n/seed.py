"""One-time independent Master seed; subsequent source updates are proposals only."""
import argparse
import json
from pathlib import Path

from core import ROOT, fingerprint, record_scope


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    args = parser.parse_args()
    destination = ROOT / "l10n/catalog.json"
    if destination.exists():
        raise SystemExit("Catalog already exists. Use refresh.py to review changes; never overwrite approvals.")
    capture = json.loads(args.capture.read_text(encoding="utf-8"))
    if capture.get("format") != "steel-compendium-approved-book/v1":
        raise SystemExit("Expected an approved-only Book capture")
    records = []
    for record in capture["records"]:
        if record["status"] != "APPROVED" or not record["source"] or not record["target"]:
            raise ValueError("Capture contains a non-approved or empty record")
        record = dict(record)
        record["sourceHash"] = fingerprint(record["source"])
        record["scope"] = record_scope(record)
        record["approvalBasis"] = "Book Master APPROVED; exact source and scoped rendered-text match required"
        records.append(record)
    data = {"format": "steel-compendium-catalog/v1", "locale": "zh-TW",
            "bookSource": capture["source"], "master": None, "records": records}
    destination.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"importedApproved": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
