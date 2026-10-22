"""Approved-only, exact-source localization after steel-etl has parsed English.

No source files, URLs, IDs, JSON filter values or game calculations are rewritten.
Matching uses rendered text, never approximate similarity or word substitution.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import unicodedata
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import markdown
from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = Path(__file__).resolve().parents[2]
BLOCKS = "p,li,td,th,h1,h2,h3,h4,h5,h6,.sc-ability__section-body,.sb__feat-body"
LABELS = "a,h1,h2,h3,h4,h5,h6,.tag,.pre,.l,.sc-head__slot,.sc-ability__chip,dt,th"


@lru_cache(maxsize=20000)
def plain(value: str) -> str:
    return BeautifulSoup(markdown.markdown(value, extensions=["tables"]), "lxml").get_text(" ", strip=True)


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFC", html.unescape(value))
    value = value.replace("\u2019", "'").replace("\u2018", "'").replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value).strip()
    # Inline Markdown/HTML boundaries may introduce whitespace before punctuation.
    return re.sub(r"\s+([.,;:!?])", r"\1", value)


def fingerprint(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def load_catalog(path: Path | None = None) -> dict:
    data = json.loads((path or ROOT / "l10n/catalog.json").read_text(encoding="utf-8"))
    if data.get("format") != "steel-compendium-catalog/v1" or data.get("locale") != "zh-TW":
        raise ValueError("Unsupported catalog format or locale")
    seen = set()
    for record in data["records"]:
        if record.get("status") != "APPROVED" or record.get("kind") not in {"glossary", "names", "strings", "ui"}:
            raise ValueError("Public snapshot must contain approved records only")
        if record["id"] in seen:
            raise ValueError(f"Duplicate record: {record['id']}")
        seen.add(record["id"])
        if record["status"] == "APPROVED":
            if not record.get("target") or record.get("sourceHash") != fingerprint(record["source"]):
                raise ValueError(f"Invalid approval/source hash: {record['id']}")
    return data


def record_scope(record: dict) -> str:
    """Book context remains part of the binding, even for identical text."""
    context = record.get("context", "")
    match = re.match(r"Ancestries / (.+)", context)
    if match:
        return "ancestry:" + match[1].lower().replace(" ", "-")
    match = re.match(r"Kits — (.+)", context)
    if match and not match[1].startswith("General Rules"):
        return "kit:" + match[1].lower().replace(" ", "-")
    if context.startswith("Background"):
        return "background"
    if context.startswith("Perks"):
        return "perk"
    if context == "Skills":
        return "skill"
    if context == "Conditions":
        return "condition"
    if context.startswith("Combat"):
        return "combat"
    return "heroes"


def scope_matches(scope: str, uri: str, scc: str = "") -> bool:
    if scope == "ui":
        return True
    if scope.startswith("page:"):
        return scope[5:] == uri
    if scope.startswith("scc:"):
        return scope[4:] == scc
    if uri.startswith("Read/heroes/"):
        chapter = Path(uri).stem
        if scope.startswith("ancestry:"):
            return chapter == "ancestries"
        if scope.startswith("kit:"):
            return chapter == "kits"
        return scope == "heroes" or chapter in {
            "background", "tests", "combat", "perks", "classes", "making-a-hero", "the-basics"
        }
    if scc and not scc.startswith("mcdm.heroes."):
        return False
    if not uri.startswith("Browse/"):
        return scope == "heroes" and uri in {"index.md", "table-reference.md"}
    if scope.startswith("ancestry:"):
        slug = scope.split(":", 1)[1]
        return uri == f"Browse/ancestry/{slug}.md" or f"/{slug}/" in uri
    if scope.startswith("kit:"):
        slug = scope.split(":", 1)[1]
        return uri == f"Browse/kit/{slug}.md" or f"/{slug}/" in uri or f"/Kits/{slug}-" in uri
    if scope == "background":
        return any(uri.startswith(f"Browse/{kind}/") for kind in ["career", "culture", "skill", "rule"])
    if scope in {"perk", "skill", "condition"}:
        return uri.startswith(f"Browse/{scope}/")
    if scope == "combat":
        return uri.startswith(("Browse/rule/", "Browse/feature/common/", "Browse/movement/"))
    return True


def to_markdown(node) -> str:
    """Small serializer for translated approved blocks; never serializes game JSON."""
    if isinstance(node, NavigableString):
        return str(node)
    inner = "".join(to_markdown(child) for child in node.children)
    if node.name == "a":
        return f"[{inner}]({node.get('href', '')})"
    if node.name in {"strong", "b"}:
        return "**" + inner + "**"
    if node.name in {"em", "i"}:
        return "*" + inner + "*"
    if node.name == "br":
        return "<br>"
    if node.name == "li":
        return "- " + inner + "\n"
    if node.name in {"p", "ul", "ol"}:
        return inner + "\n\n"
    return inner


class Catalog:
    def __init__(self, data: dict):
        self.data = data
        self.segments = defaultdict(list)
        self.labels = defaultdict(list)
        for record in data["records"]:
            if record["status"] != "APPROVED" or record.get("sourceHash") != fingerprint(record["source"]):
                continue
            scope = record.get("scope") or record_scope(record)
            source, target = record["source"], record["target"]
            if record["kind"] in {"glossary", "names", "ui"}:
                self.labels[normalized(plain(source)).casefold()].append((target, record["id"], scope))
                continue
            # Parallel paragraphs only: differing paragraph counts need an explicit adaptation.
            src_parts = re.split(r"\n\s*\n", source.strip())
            dst_parts = re.split(r"\n\s*\n", target.strip())
            pairs = [(source, target)]
            if len(src_parts) == len(dst_parts):
                pairs += list(zip(src_parts, dst_parts))
            for src, dst in pairs:
                key = normalized(plain(src))
                if len(key) >= 20:
                    self.segments[key].append((dst, record["id"], scope))
                elif "\n" not in src:
                    self.labels[key.casefold()].append((dst, record["id"], scope))

    def lookup(self, source: str, uri: str, scc: str = "", label: bool = False):
        key = normalized(source)
        choices = (self.labels.get(key.casefold(), []) if label else self.segments.get(key, []))
        allowed = [x for x in choices if scope_matches(x[2], uri, scc)]
        # Conflicting approved translations never resolve by arbitrary row order.
        targets = {x[0] for x in allowed}
        return allowed[0] if len(targets) == 1 else None

    def translate_html(self, content: str, uri: str, scc: str = "") -> tuple[str, list[dict]]:
        soup = BeautifulSoup(content, "lxml")
        hits = []
        # Containers first; descendants are not independently replaced afterwards.
        for el in list(soup.select(BLOCKS)):
            if el.parent is None or el.find_parent(["script", "template", "style", "code", "pre"]):
                continue
            if el.get("data-sc-l10n") or el.find_parent(attrs={"data-sc-l10n": True}):
                continue
            if el.select("table,.sc-ability,.sb-wrap,h1,h2,h3,h4,h5,h6"):
                continue
            if el.get("class") and "chars" in el["class"]:
                continue
            source = normalized(el.get_text(" ", strip=True))
            found = self.lookup(source, uri, scc)
            if not found:
                continue
            target, record_id, _ = found
            rendered = self._linked_target(target, el, uri, scc)
            if rendered is None:
                hits.append({"record": record_id, "state": "link-adaptation-required"})
                continue
            if el.name == "p" and len(rendered.find_all("p", recursive=False)) == 1:
                rendered = rendered.p
            # Numeric/tool readers receive the untouched English source separately.
            el["data-sc-original"] = source
            el["data-sc-l10n"] = record_id
            el.clear()
            for child in list(rendered.contents):
                el.append(child.extract())
            hits.append({"record": record_id, "state": "translated"})
        for el in list(soup.select(LABELS)):
            if el.parent is None or el.find_parent(["script", "template", "style", "code", "pre"]):
                continue
            if el.get("data-sc-l10n") or el.find_parent(attrs={"data-sc-l10n": True}):
                continue
            if el.find(True):  # do not flatten headings with permalinks or composite labels
                children = [n for n in el.contents if isinstance(n, NavigableString) and not isinstance(n, Comment)]
                if len(children) != 1:
                    continue
                source = str(children[0]).strip()
            else:
                children = None
                source = el.get_text(strip=True)
            if el.name == "a":
                prose = el.find_parent(["p", "li", "td"]) or el.find_parent(class_=["sc-ability__section-body", "sb__feat-body"])
                if prose and normalized(prose.get_text(" ", strip=True)) != normalized(source):
                    # A missing/unsafe prose translation falls back as a complete block.
                    # Standalone entity links in indexes can still use approved names.
                    continue
            found = self.lookup(source, uri, scc, label=True)
            if not found:
                continue
            target, record_id, _ = found
            el["data-sc-original"] = source
            el["data-sc-l10n"] = record_id
            if children:
                children[0].replace_with(target)
            else:
                el.string = target
            hits.append({"record": record_id, "state": "translated"})
        body = soup.body
        return (body.decode_contents() if body else str(soup)), hits

    def translate_markdown(self, source: str, uri: str, scc: str = "") -> str:
        """Export content uses the same approved block/link matcher as visible cards.

        Only recognized blocks are serialized. Unmatched Markdown remains byte-for-byte
        unchanged, including numbers, tables, destinations and formatting.
        """
        output = []
        for part in re.split(r"(\n\s*\n)", source):
            if not part.strip():
                output.append(part)
                continue
            quote = all(not line.strip() or line.startswith(">") for line in part.splitlines())
            body = "\n".join(re.sub(r"^> ?", "", line) for line in part.splitlines()) if quote else part
            rendered = markdown.markdown(body, extensions=["tables"])
            translated, hits = self.translate_html(rendered, uri, scc)
            if any(hit["state"] == "translated" for hit in hits):
                result = to_markdown(BeautifulSoup(translated, "html.parser")).strip()
                # Avoid rewriting tables/list syntax with a partial serializer.
                if "<table" in translated or "<ul" in translated or "<ol" in translated:
                    output.append(part)
                    continue
                if quote:
                    result = "\n".join("> " + line if line else ">" for line in result.splitlines())
                output.append(result)
            else:
                output.append(part)
        return "".join(output)

    def _linked_target(self, target: str, source_el, uri: str, scc: str):
        """Retain every authored link, or leave the whole English block intact."""
        fragment = BeautifulSoup(markdown.markdown(target, extensions=["tables"]), "html.parser")
        done = set()
        for anchor in source_el.find_all("a", href=True):
            if "headerlink" in anchor.get("class", []):
                continue
            text = anchor.get_text(" ", strip=True)
            translated = self.lookup(text, uri, scc, label=True)
            label = translated[0] if translated else text
            identity = (anchor["href"], label)
            if identity in done:
                continue
            done.add(identity)
            placed = False
            for node in list(fragment.find_all(string=True)):
                if node.find_parent("a"):
                    continue
                match = re.search(re.escape(label), str(node), flags=re.IGNORECASE)
                if not match:
                    continue
                new_anchor = fragment.new_tag("a", href=anchor["href"])
                new_anchor.string = match[0]
                node.replace_with(NavigableString(str(node)[:match.start()]), new_anchor,
                                  NavigableString(str(node)[match.end():]))
                placed = True
                break
            if not placed:
                return None
        return fragment


def classify(uri: str, meta: dict) -> str:
    scc = meta.get("scc", "")
    if scc and not scc.startswith("mcdm.heroes.") or uri.startswith(("Read/bestiary/", "Read/summoner/", "Read/beastheart/")):
        return "P4"
    if uri.startswith("Read/heroes/"):
        chapter = Path(uri).stem
        if chapter == "for-the-director":
            return "P3"
        if chapter in {"introduction", "tests", "combat", "negotiation", "downtime-projects", "rewards"}:
            return "P2"
        return "P1"
    if re.search(r"(?:level-|level/)([2-9]|10)(?:/|\.)", uri):
        return "P2"
    if uri.startswith("Browse/"):
        kind = uri.split("/")[1]
        if kind in {"monster", "retainer", "dynamic-terrain"}:
            return "P4"
        if kind in {"treasure", "title", "project", "negotiation"}:
            return "P2"
        return "P1"
    return "P0"
