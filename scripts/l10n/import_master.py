"""Convert the approved projection returned by capture-master.mjs into a candidate snapshot.

Does not approve text or apply it. Run refresh.py first without --apply to inspect the diff.
"""
import argparse
import json
from pathlib import Path

from core import fingerprint, load_catalog


def convert(capture: dict, current: dict) -> dict:
    if capture.get("format") != "steel-compendium-master-approved/v1":
        raise ValueError("Only an approved-only Master capture is accepted")
    if capture.get("master", {}).get("spreadsheetId") != current["master"]["spreadsheetId"]:
        raise ValueError("Independent Master ID mismatch")
    seen = set()
    for row in capture["records"]:
        if row.get("status") != "APPROVED" or not row.get("target") or row.get("sourceHash") != fingerprint(row["source"]):
            raise ValueError("Invalid approval/source hash: " + row.get("id", ""))
        if row["id"] in seen:
            raise ValueError("Duplicate approved ID: " + row["id"])
        seen.add(row["id"])
    previous = {row["id"]: row for row in current["records"]}
    merged = []
    for row in capture["records"]:
        old = previous.get(row["id"], {})
        changed = any(old.get(key) != row.get(key) for key in ["source", "target", "scope"])
        merged.append({**old, **row, "approvalBasis": "Independent Master APPROVED" if changed else old.get("approvalBasis", "Independent Master APPROVED")})
    return {**current, "master": {**current["master"], **capture["master"]}, "records": merged}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    candidate = convert(json.loads(args.capture.read_text(encoding="utf-8")), load_catalog())
    args.output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"approved": len(candidate["records"]), "candidate": str(args.output)}, ensure_ascii=False))
