import json
from pathlib import Path

from bs4 import BeautifulSoup

from core import ROOT, load_catalog


def main():
    load_catalog()
    report = json.loads((ROOT / "reports/coverage.json").read_text(encoding="utf-8"))
    assert report["summary"]["P1"]["pages"] > 0, "Missing P1 inventory"
    assert report["summary"]["P1"]["translatedBlocks"] > 0, "No approved translation reached the build"
    index = json.loads((ROOT / "site/search/search_index.json").read_text(encoding="utf-8"))
    assert any(d.get("aliases") for d in index["docs"]), "Missing English search aliases"
    for page in report["pages"]:
        if page["scc"].startswith("mcdm.heroes.v1/class/"):
            assert (ROOT / "site" / page["url"] / "index.html").exists(), page["url"]
    for path in ["Browse/ancestry/human/index.html", "Read/heroes/ancestries/index.html",
                 "Browse/career/soldier/index.html", "Browse/class/fury/index.html"]:
        soup = BeautifulSoup((ROOT / "site" / path).read_text(encoding="utf-8"), "lxml")
        assert soup.html.get("lang") == "zh-TW", path
        assert soup.select_one("[data-sc-l10n]"), f"No approved display in {path}"
        assert soup.select_one("#sc-l10n-labels"), path
    for path in ["Bestiary/index.html", "Read/bestiary/index.html", "Read/beastheart/index.html", "Read/summoner/index.html"]:
        assert (ROOT / "site" / path).exists(), f"Upstream page lost: {path}"
    print(json.dumps({"pages": len(report["pages"]), "P1": report["summary"]["P1"], "status": "passed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
