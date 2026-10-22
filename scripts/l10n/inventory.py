"""Inventory upstream paths/SCCs and P1 dependencies without editing generated files."""
import argparse
import json
import posixpath
import re
from pathlib import Path

import yaml

from core import ROOT, classify


def inventory():
    pages = []
    for path in sorted((ROOT / "docs").rglob("*.md")):
        source = path.read_text(encoding="utf-8")
        meta = {}
        if source.startswith("---\n"):
            meta = yaml.safe_load(source.split("---\n", 2)[1]) or {}
        uri = path.relative_to(ROOT / "docs").as_posix()
        priority = classify(uri, meta)
        links = []
        for match in re.finditer(r"\]\(([^)#]+\.md)(?:#[^)]*)?\)", source):
            target = match[1]
            if "://" not in target:
                links.append(posixpath.normpath(posixpath.join(posixpath.dirname(uri), target)))
        pages.append({"path": uri, "scc": str(meta.get("scc", "")),
                      "title": str(meta.get("name", path.stem)), "priority": priority,
                      "references": sorted(set(links))})
    known = {x["path"]: x for x in pages}
    dependencies = []
    for page in pages:
        if page["priority"] != "P1":
            continue
        for reference in page["references"]:
            target = known.get(reference)
            if target and target["priority"] != "P1":
                dependencies.append({"from": page["path"], "to": reference,
                                     "priority": target["priority"], "state": "review-required"})
    return {"upstream": json.loads((ROOT / "l10n/upstream.json").read_text()),
            "pages": pages, "crossPriorityReferences": dependencies,
            "note": "P1 候選包含綜合職業頁；高等級內容不因同頁就列為首批完成條件。跨優先度引用需人工分類必要依賴。"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    result = inventory()
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    (report_dir / "source-inventory.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.write_manifest:
        classes = [page for page in result["pages"] if page["scc"].startswith("mcdm.heroes.v1/class/")]
        manifest = {"milestone": "Heroes all classes level-1 character creation", "sourceVersion": "Heroes 1.01b",
                    "classes": [{"scc": page["scc"], "path": page["path"], "name": page["title"],
                                 "required": sorted({ref for ref in page["references"] if "/level-" not in ref or "/level-1/" in ref}),
                                 "level1Pages": [p["path"] for p in result["pages"] if "/" + Path(page["path"]).stem + "/level-1/" in p["path"] and p["priority"] == "P1"]}
                                for page in classes],
                    "sharedCategories": ["ancestry", "culture", "career", "skill", "kit", "perk", "complication", "rule", "religion"],
                    "completion": "All required fields approved and all display locations accepted; names alone do not count"}
        (ROOT / "l10n/p1-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pages": len(result["pages"]), "P1": sum(x["priority"] == "P1" for x in result["pages"]),
                      "crossPriorityReferences": len(result["crossPriorityReferences"])}, ensure_ascii=False))
