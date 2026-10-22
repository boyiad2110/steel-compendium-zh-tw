"""MkDocs hook. Generated upstream sources remain byte-for-byte untouched."""
import json
import sys
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup
from mkdocs.plugins import event_priority

sys.path.insert(0, str(Path(__file__).parent))
from core import Catalog, ROOT, classify, fingerprint, load_catalog, normalized

catalog = None
pages = []
aliases = {}


def on_config(config):
    global catalog, pages, aliases
    catalog = Catalog(load_catalog())
    pages, aliases = [], {}
    for palette in config.theme.get("palette", []):
        toggle = palette.get("toggle", {})
        found = catalog.lookup(toggle.get("name", ""), "index.md", label=True)
        if found:
            toggle["name"] = found[0]
    # Lists replace, rather than append, in inherited config. Append here to retain all upstream assets.
    for css in ["stylesheets/l10n-zh-TW.css"]:
        if css not in config.extra_css:
            config.extra_css.append(css)
    config.extra_javascript = ["javascripts/l10n-core.js", "javascripts/l10n.js"] + list(config.extra_javascript)
    return config


def on_nav(nav, config, files):
    def visit(items):
        for item in items:
            uri = item.file.src_uri if getattr(item, "file", None) else "index.md"
            found = catalog.lookup(item.title or "", uri, label=True)
            if found:
                item.title = found[0]
            if getattr(item, "children", None):
                visit(item.children)
    visit(nav.items)
    return nav


@event_priority(50)
def on_page_content(html, page, config, files):
    uri, scc = page.file.src_uri, str(page.meta.get("scc", ""))
    original_title = page.meta.get("name") or page.title
    priority = classify(uri, page.meta)
    if len(pages) % 250 == 0:
        print(f"zh-TW: localizing page {len(pages) + 1}: {uri}", flush=True)
    # P4 is retained in English until its own scoped mappings are approved.
    translated, hits = catalog.translate_html(html, uri, scc) if priority != "P4" else (html, [])
    soup = BeautifulSoup(translated, "lxml")
    if priority != "P4":
        for template in soup.select("template.sc-src[data-src]"):
            template["data-src"] = catalog.translate_markdown(template["data-src"], uri, scc)
    heading = soup.find("h1")
    if heading:
        title = heading.get_text(" ", strip=True).replace("¶", "").strip()
        if title and title != original_title:
            page.title = title
            aliases[page.url] = original_title
    headings = {el["id"]: el.get_text(" ", strip=True).replace("¶", "").strip()
                for el in soup.select("h1[id],h2[id],h3[id],h4[id],h5[id],h6[id]")}
    def translate_toc(items):
        for item in items:
            if item.id in headings:
                item.title = headings[item.id]
            translate_toc(item.children)
    translate_toc(page.toc.items)
    blocks = []
    for el in soup.select("p,li,td,th,h1,h2,h3,h4,h5,h6"):
        if el.find_parent(["script", "template", "pre", "code"]) or el.select("p,li,table,h1,h2,h3,h4,h5,h6"):
            continue
        source = el.get("data-sc-original") or el.get_text(" ", strip=True)
        source = normalized(source.replace("¶", ""))
        if not source or not any(c.isascii() and c.isalpha() for c in source):
            continue
        owner = el if el.get("data-sc-l10n") else el.find_parent(attrs={"data-sc-l10n": True})
        translated_block = bool(owner)
        if translated_block:
            reason = "approved-exact-match"
        elif priority == "P4":
            reason = "deferred-P4"
        elif catalog.lookup(source, uri, scc):
            reason = "link-adaptation-required"
        elif catalog.lookup(source, uri, scc, label=True):
            reason = "display-binding-required"
        else:
            reason = "no-approved-exact-match"
        blocks.append({"id": f"{scc or uri}#text:{fingerprint(source)[:16]}",
                       "source": source, "sourceHash": fingerprint(source),
                       "state": "translated" if translated_block else "english",
                       "reason": reason,
                       "record": owner.get("data-sc-l10n") if owner else None})
    # Browser helpers receive approved, unambiguous exact labels only. No runtime Sheet access.
    labels = {}
    if priority != "P4":
        for key in catalog.labels:
            found = catalog.lookup(key, uri, scc, label=True)
            if found:
                labels[key] = found[0]
    island = soup.new_tag("template")
    island["id"] = "sc-l10n-labels"
    island["data-labels"] = json.dumps(labels, ensure_ascii=False, separators=(",", ":"))
    (soup.body or soup).append(island)
    # Export templates above receive the same approved-only transformation at build time.
    pages.append({"path": uri, "url": page.url, "scc": scc, "title": original_title,
                  "priority": priority, "blocks": blocks,
                  "translated": sum(x["state"] == "translated" for x in blocks),
                  "english": sum(x["state"] == "english" for x in blocks),
                  "adaptationsRequired": sum(x["state"] == "link-adaptation-required" for x in hits)})
    return soup.body.decode_contents() if soup.body else str(soup)


def on_post_build(config):
    # Retain exact English aliases without displaying a second heading on the page.
    index_path = Path(config.site_dir) / "search/search_index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        for doc in index["docs"]:
            if doc["location"] in aliases:
                doc["aliases"] = [aliases[doc["location"]]]
        index_path.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    summary = {}
    for priority in ["P0", "P1", "P2", "P3", "P4"]:
        group = [p for p in pages if p["priority"] == priority]
        summary[priority] = {"pages": len(group), "translatedBlocks": sum(p["translated"] for p in group),
                             "englishBlocks": sum(p["english"] for p in group),
                             "translationComplete": False, "visualAcceptance": "pending"}
    report = {"upstream": json.loads((ROOT / "l10n/upstream.json").read_text()),
              "summary": summary, "pages": pages}
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    (report_dir / "coverage.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    missing = {}
    for page in pages:
        if page["priority"] != "P1":
            continue
        for block in page["blocks"]:
            if block["state"] == "english":
                unit = missing.setdefault(block["id"], {**block, "paths": [], "scc": page["scc"]})
                if page["path"] not in unit["paths"]:
                    unit["paths"].append(page["path"])
    (report_dir / "p1-missing.json").write_text(json.dumps(list(missing.values()), ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# 中文化覆蓋報告", "", "工程接線與譯文核准分開追蹤；筆數不代表完成率。", "",
             "| 範圍 | 頁數 | 中文區塊 | 英文區塊 | 驗收 |", "|---|---:|---:|---:|---|"]
    for key, values in summary.items():
        lines.append(f"| {key} | {values['pages']} | {values['translatedBlocks']} | {values['englishBlocks']} | 待人工驗收 |")
    lines += ["", "## Heroes 職業", "", "| 職業 | 中文區塊 | 英文區塊 |", "|---|---:|---:|"]
    for page in pages:
        if page["scc"].startswith("mcdm.heroes.v1/class/"):
            lines.append(f"| {page['title']} | {page['translated']} | {page['english']} |")
    (report_dir / "coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("zh-TW coverage:", json.dumps(summary, ensure_ascii=False))
