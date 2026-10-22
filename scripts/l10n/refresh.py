"""Compare a new approved capture or independent Master export without overwriting.

For Master export, --apply atomically replaces catalog.json after validation.
Book updates always produce proposals, never change independent approvals.
"""
import argparse
import json
import os
import tempfile
from pathlib import Path

from core import ROOT, fingerprint, load_catalog


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    current = load_catalog()
    incoming = json.loads(args.input.read_text(encoding="utf-8"))
    old = {x["id"]: x for x in current["records"]}
    if incoming.get("format") == "steel-compendium-approved-book/v1":
        if args.apply:
            raise SystemExit("Book updates are proposals only; review them in the independent Master.")
        proposals = []
        for row in incoming["records"]:
            if row.get("status") != "APPROVED":
                continue
            before = old.get(row["id"])
            if not before or any(before.get(k) != row.get(k) for k in ["source", "target"]):
                proposals.append({"id": row["id"], "change": "added" if not before else "changed",
                                  "oldSourceHash": before.get("sourceHash") if before else None,
                                  "newSourceHash": fingerprint(row["source"])})
        print(json.dumps({"proposals": proposals}, ensure_ascii=False, indent=2))
        return
    if incoming.get("format") != "steel-compendium-catalog/v1":
        raise SystemExit("Unsupported capture format")
    if not incoming.get("master", {}).get("spreadsheetId") or incoming["master"]["spreadsheetId"] != current.get("master", {}).get("spreadsheetId"):
        raise SystemExit("Independent Master ID mismatch")
    # Reject drafts in repository snapshots; pending source inventory is stored separately.
    if any(x.get("status") != "APPROVED" for x in incoming["records"]):
        raise SystemExit("Snapshot must contain APPROVED records only")
    load_catalog(args.input)
    changes = [r["id"] for r in incoming["records"] if r != old.get(r["id"])]
    removed = sorted(set(old) - {r["id"] for r in incoming["records"]})
    print(json.dumps({"changed": changes, "removed": removed, "apply": args.apply}, ensure_ascii=False))
    if args.apply:
        fd, temporary = tempfile.mkstemp(dir=ROOT / "l10n", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as out:
                json.dump(incoming, out, ensure_ascii=False, indent=2)
                out.write("\n")
            os.replace(temporary, ROOT / "l10n/catalog.json")
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


if __name__ == "__main__":
    main()
