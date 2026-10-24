import json
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/l10n"))
from core import Catalog, classify, fingerprint, load_catalog
from import_master import convert


def row(source, target, kind="strings", scope="heroes", status="APPROVED", id="test"):
    return {"id": id, "kind": kind, "source": source, "target": target,
            "status": status, "sourceHash": fingerprint(source), "scope": scope}


class LocalizationTests(unittest.TestCase):
    def test_dragon_knight_static_ability_index_uses_approved_card_fields(self):
        import markdown
        root = Path(__file__).resolve().parents[1]
        uri = "Browse/feature/ability/dragon-knight/index.md"
        source = (root / "docs" / uri).read_text(encoding="utf-8")
        cat = Catalog(load_catalog())
        translated, _ = cat.translate_html(markdown.markdown(source), uri)
        cards = BeautifulSoup(translated, "html.parser").select(".sc-prev--ability")
        self.assertEqual(len(cards), 2)
        self.assertEqual([a['href'] for a in cards], ['draconian-pride/', 'dragon-breath/'])
        for card in cards:
            self.assertEqual([c.get_text() for c in card.select('.sc-prev__chip')], ['區域', '魔法'])
            values = card.select('.sc-prev__meta .v')
            self.assertEqual(values[1].get_text(), '區域內每個敵人')
            self.assertFalse(card.select('.sc-prev__meta .v p'))
        self.assertEqual(cards[0].select_one('.v').get_text(), '1 爆發')
        self.assertEqual(cards[1].select_one('.v').get_text(), '1 格內 3 立方')
        self.assertEqual([b.get_text() for b in cards[1].select('.v b')], ['1', '3'])

    def test_dragon_knight_real_browse_and_read_prose_stays_in_sync(self):
        import markdown
        cat = Catalog(load_catalog())
        root = Path(__file__).resolve().parents[1]
        for uri in ("Browse/ancestry/dragon-knight.md", "Read/heroes/ancestries.md"):
            source = (root / "docs" / uri).read_text(encoding="utf-8").split("---", 2)[-1]
            translated, _ = cat.translate_html(markdown.markdown(source, extensions=["tables"]), uri)
            soup = BeautifulSoup(translated, "html.parser")
            self.assertNotIn("Knighthood was a title carried", soup.get_text())
            self.assertNotIn("Then Ajax came.", soup.get_text())
            lead = next(p for p in soup.select(".sc-trait__leadin") if "虹彩鱗片" in p.get_text())
            self.assertIn("你有 3 點族裔點數", lead.get_text())
            self.assertEqual(lead.a.get_text(), "龍息")

    def test_dwarf_approved_prose_and_quick_build_match_real_browse_and_read_sources(self):
        import markdown
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        for uri in ("Browse/ancestry/dwarf.md", "Read/heroes/ancestries.md"):
            source = (root / "docs" / uri).read_text(encoding="utf-8")
            if uri.startswith("Browse/"):
                source = source.split("---", 2)[-1]
            else:
                start = source.index("## Dwarf {")
                end = source.index("## Wode Elf {", start)
                source = source[start:end]
            html = markdown.markdown(source, extensions=["tables", "attr_list"])
            # steel-etl resolves same-page Markdown links to ./ in built pages.
            html = html.replace('href="dwarf.md"', 'href="./"')
            html = html.replace('href="../../Browse/ancestry/dwarf.md"',
                                'href="../../Browse/ancestry/dwarf/"')
            translated, hits = cat.translate_html(html, uri)
            soup = BeautifulSoup(translated, "html.parser")
            description_one = soup.select_one('p[data-sc-l10n="heroes.ancestries.dwarf.description.1"]')
            self.assertIsNotNone(description_one)
            self.assertEqual(sum(a.get_text(strip=True) == "矮人"
                                 for a in description_one.select("a[href]")), 2)
            self.assertIn("矮人雖然體型矮小", description_one.get_text())
            self.assertNotIn("Possessed of a strength", description_one.get_text())
            description = soup.select_one('p[data-sc-l10n="heroes.ancestries.dwarf.description.2"]')
            self.assertIsNotNone(description)
            self.assertEqual(len(description.select("a")), 3)
            self.assertEqual([a["href"] for a in description.select("a")],
                             ["./"] * 3 if uri.startswith("Browse/") else
                             ["../../Browse/ancestry/dwarf/"] * 3)
            self.assertEqual([a.get_text() for a in description.select("a")], ["矮人", "他們", "矮人"])
            expected = next(r["target"] for r in cat.data["records"]
                            if r["id"] == "heroes.ancestries.dwarf.description.2")
            compact = lambda text: "".join(text.split())
            self.assertEqual(compact(description.get_text()),
                             compact(BeautifulSoup(markdown.markdown(expected), "lxml").get_text()))
            self.assertNotIn({"record": "heroes.ancestries.dwarf.description.2",
                              "state": "link-adaptation-required"}, hits)
            story_ids = [p["data-sc-l10n"] for p in soup.select('p[data-sc-l10n^="heroes.ancestries.dwarf.on-dwarves.paragraph."]')]
            self.assertEqual(story_ids, [
                f"heroes.ancestries.dwarf.on-dwarves.paragraph.{number:02d}"
                for number in range(1, 49)
            ])
            self.assertFalse(any("The dwarf's head snapped" in p.get_text()
                                 for p in soup.select("p")))
            lead = next(p for p in soup.select(".sc-trait__leadin")
                        if "你有 3 點族裔點數" in p.get_text()
                        and "腳踏實地" in p.get_text())
            self.assertIn("速選：", lead.get_text())
            self.assertIn("腳踏實地、堅硬石膚", lead.get_text())
            heading = soup.find(["h2", "h3"], string="談矮人")
            self.assertIsNotNone(heading)

    def test_dwarf_runic_options_translate_in_browse_read_and_standalone_sources(self):
        import markdown
        from collections import Counter
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        uris = ("Browse/ancestry/dwarf.md", "Browse/feature/trait/dwarf/runic-carving.md",
                "Read/heroes/ancestries.md")
        labels = {"detection": "偵測", "light": "照明", "voice": "傳聲"}
        for uri in uris:
            source = (root / "docs" / uri).read_text(encoding="utf-8")
            if uri == "Browse/ancestry/dwarf.md":
                source = source.split("---", 2)[-1]
            elif uri == "Read/heroes/ancestries.md":
                start = source.index("## Dwarf {")
                end = source.index("## Wode Elf {", start)
                source = source[start:end]
            else:
                source = source.split("---", 2)[-1]
            rendered = markdown.markdown(source, extensions=["tables", "attr_list"])
            original = BeautifulSoup(rendered, "lxml")
            translated, hits = cat.translate_html(rendered, uri)
            result = BeautifulSoup(translated, "lxml")
            for option, label in labels.items():
                record_id = f"heroes.ancestries.dwarf.signature.runic-carving.{option}.effect"
                prefix = {"detection": "Detection:", "light": "Light:", "voice": "Voice:"}[option]
                source_block = next(p for p in original.select("p")
                                    if p.get_text(" ", strip=True).startswith(prefix))
                match = result.select(f'p[data-sc-l10n="{record_id}"]')
                self.assertEqual(len(match), 1, (uri, record_id))
                target = match[0]
                self.assertEqual(target.find(["b", "strong"]).get_text(strip=True), label + "：")
                self.assertEqual(Counter(a["href"] for a in target.select("a[href]")),
                                 Counter(a["href"] for a in source_block.select("a[href]")))
                expected = next(r["target"] for r in cat.data["records"] if r["id"] == record_id)
                self.assertEqual("".join(target.get_text(" ", strip=True).split()),
                                 "".join((label + "：" + expected).split()))
                self.assertNotIn({"record": record_id, "state": "link-adaptation-required"}, hits)

    def test_dwarf_ancestry_index_card_uses_scoped_name_and_keeps_search_link(self):
        import markdown
        root = Path(__file__).resolve().parents[1]
        uri = "Browse/ancestry/index.md"
        source = (root / "docs" / uri).read_text(encoding="utf-8")
        translated, _ = Catalog(load_catalog()).translate_html(
            markdown.markdown(source, extensions=["tables"]), uri)
        card = next(c for c in BeautifulSoup(translated, "lxml").select(".sc-card")
                    if c.select_one(".sc-card__link") and c.select_one(".sc-card__link")["href"] == "dwarf/")
        self.assertEqual(card.select_one(".sc-card__name").get_text(strip=True), "矮人")
        self.assertEqual(card.select_one(".sc-card__link")["aria-label"], "Dwarf")
        flavor = next(r["target"] for r in Catalog(load_catalog()).data["records"]
                      if r["id"] == "heroes.ancestries.dwarf.description.1")
        self.assertEqual("".join(card.select_one(".sc-card__flavor").get_text(" ", strip=True).split()),
                         "".join(flavor.split()))
        self.assertEqual(card.select_one(".sc-card__type").get_text(strip=True), "族裔")
        self.assertEqual(card.select_one(".sc-card__line b").get_text(strip=True), "招牌特性")
        self.assertEqual(card.select_one(".sc-card__line .hl").get_text(strip=True), "符文銘刻")
        self.assertEqual(card.select_one(".sc-card__link")["href"], "dwarf/")

    def test_dwarf_static_trait_index_cards_translate_fields_and_keep_destinations(self):
        import markdown
        root = Path(__file__).resolve().parents[1]
        uri = "Browse/feature/trait/dwarf/index.md"
        source = (root / "docs" / uri).read_text(encoding="utf-8")
        translated, _ = Catalog(load_catalog()).translate_html(
            markdown.markdown(source, extensions=["tables"]), uri)
        cards = BeautifulSoup(translated, "lxml").select(".sc-prev")
        self.assertEqual(len(cards), 7)
        self.assertEqual([c.select_one(".sc-head__left-eyebrow").get_text(strip=True)
                          for c in cards], ["特性"] * 7)
        self.assertEqual([c["href"] for c in cards], [
            "dwarf-traits/", "great-fortitude/", "grounded/", "runic-carving/",
            "spark-off-your-skin/", "stand-tough/", "stone-singer/"
        ])
        self.assertEqual(cards[0].select_one(".sc-prev__grant").get_text(" ", strip=True), "2 個選項")
        self.assertTrue(all(not c.select_one(".sc-prev__flavor").get_text().startswith(("Your ", "Dwarf heroes"))
                            for c in cards))

    def test_dwarf_names_and_measurements_translate_from_real_read_chapter(self):
        import markdown
        root = Path(__file__).resolve().parents[1]
        uri = "Read/heroes/ancestries.md"
        source = (root / "docs" / uri).read_text(encoding="utf-8")
        translated, _ = Catalog(load_catalog()).translate_html(
            markdown.markdown(source, extensions=["tables", "attr_list"]), uri)
        soup = BeautifulSoup(translated, "lxml")
        names = soup.find(lambda el: el.name in {"h3", "h4", "h5", "h6"}
                          and el.get_text(strip=True) == "矮人姓名")
        self.assertIsNotNone(names)
        name_categories = names.find_next_siblings("p", limit=3)
        self.assertEqual([el.select_one("strong").get_text(" ", strip=True) for el in name_categories],
                         ["女性名：", "中性名：", "男性名："])
        table = next(t for t in soup.select("table") if "4'0''-4'6''" in t.get_text())
        headers = table.select("th")
        self.assertEqual([el.get_text(" ", strip=True) for el in headers],
                         ["族裔", "身高（呎 / 吋）", "體重（磅）", "預期壽命（年）"])
        dwarf_row = next(row for row in table.select("tr")
                         if row.select_one("a") and row.select_one("a").get_text(strip=True) == "矮人")
        self.assertEqual([cell.get_text(" ", strip=True) for cell in dwarf_row.select("td")],
                         ["矮人", "4'0''-4'6''", "500-1,000", "700-1,500"])

    def test_approved_read_overview_summaries_keep_all_links(self):
        import markdown
        from collections import Counter
        root = Path(__file__).resolve().parents[1]
        uri = "Read/heroes/ancestries.md"
        source = (root / "docs" / uri).read_text(encoding="utf-8")
        rendered = markdown.markdown(source, extensions=["tables", "attr_list"])
        original = BeautifulSoup(rendered, "lxml")
        translated, hits = Catalog(load_catalog()).translate_html(rendered, uri)
        soup = BeautifulSoup(translated, "lxml")
        records = {r["id"]: r for r in load_catalog()["records"]}
        for ancestry in ("dwarf", "dragon-knight", "wode-elf"):
            with self.subTest(ancestry=ancestry):
                summary_id = f"heroes.ancestries.{ancestry}.summary"
                name = records[f"heroes.ancestries.{ancestry}.name"]
                record = records[summary_id]
                match = soup.select_one(f'p[data-sc-l10n="{summary_id}"]')
                self.assertIsNotNone(match)
                source_block = next(p for p in original.select("p")
                                    if p.find("strong")
                                    and p.find("strong").get_text(strip=True) == name["source"] + ":")
                self.assertEqual(Counter(a["href"] for a in match.select("a[href]")),
                                 Counter(a["href"] for a in source_block.select("a[href]")))
                self.assertEqual("".join(match.get_text(" ", strip=True).split()),
                                 "".join((name["target"] + "：" + record["target"]).split()))
                self.assertNotIn({"record": summary_id, "state": "link-adaptation-required"}, hits)
        self.assertIsNone(soup.select_one('p[data-sc-l10n="heroes.ancestries.high-elf.summary"]'))

    def test_dwarf_markdown_export_uses_snapshot_and_preserves_authored_links(self):
        import markdown
        import re
        from collections import Counter
        root = Path(__file__).resolve().parents[1]
        uri = "Browse/ancestry/dwarf.md"
        source = (root / "docs" / uri).read_text(encoding="utf-8").split("---", 2)[-1]
        exported = Catalog(load_catalog()).translate_markdown(source, uri)
        original_html = markdown.markdown(source, extensions=["tables", "attr_list"])
        exported_html = markdown.markdown(exported, extensions=["tables", "attr_list"])
        original_links = Counter(a["href"] for a in BeautifulSoup(original_html, "lxml").select("a[href]"))
        exported_links = Counter(a["href"] for a in BeautifulSoup(exported_html, "lxml").select("a[href]"))
        self.assertEqual(exported_links, original_links)
        self.assertIn("\n\n矮人\n\n---", exported)
        self.assertIn("[遊唱家](../class/troubadour.md)", exported)
        self.assertNotIn("Dwarves are the children of the elder god Ord", exported)
        expected = [r["target"] for r in Catalog(load_catalog()).data["records"]
                    if r["id"].startswith("heroes.ancestries.dwarf.on-dwarves.paragraph.")]
        content = markdown.markdown(exported, extensions=["tables", "attr_list"])
        paragraphs = [p.get_text(" ", strip=True) for p in BeautifulSoup(content, "lxml").select("p")]
        compact = lambda text: re.sub(r"\s", "", text)
        for target in expected:
            target_text = BeautifulSoup(markdown.markdown(target), "lxml").get_text(" ", strip=True)
            self.assertIn(compact(target_text), [compact(p) for p in paragraphs])

    def test_dwarf_purchased_trait_links_retain_book_master_wording(self):
        import markdown
        import re
        from collections import Counter
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        cases = {
            "heroes.ancestries.dwarf.trait.grounded.effect": ["穩度", "+1"],
            "heroes.ancestries.dwarf.trait.spark-off-your-skin.effect": ["體力", "+6", "+6"],
        }
        for uri in ("Browse/ancestry/dwarf.md", "Browse/feature/trait/dwarf/grounded.md",
                    "Browse/feature/trait/dwarf/spark-off-your-skin.md", "Read/heroes/ancestries.md"):
            source = (root / "docs" / uri).read_text(encoding="utf-8")
            if uri.startswith("Browse/"):
                source = source.split("---", 2)[-1]
            else:
                start = source.index("## Dwarf {")
                end = source.index("## Wode Elf {", start)
                source = source[start:end]
            rendered = markdown.markdown(source, extensions=["tables"])
            translated, hits = cat.translate_html(rendered, uri)
            original_soup = BeautifulSoup(rendered, "lxml")
            soup = BeautifulSoup(translated, "lxml")
            for record_id, labels in cases.items():
                matches = soup.select(f'[data-sc-l10n="{record_id}"]')
                source_blocks = original_soup.select("p")
                source_prefix = ("Your heavy stone body" if record_id.endswith("grounded.effect")
                                 else "Your stone skin affords you")
                source_block = next((p for p in source_blocks
                                     if p.get_text(" ", strip=True).startswith(source_prefix)), None)
                if source_block is None:
                    self.assertFalse(matches, (uri, record_id))
                    continue
                self.assertEqual(len(matches), 1, (uri, record_id))
                result = matches[0]
                self.assertEqual([a.get_text() for a in result.select("a")], labels)
                self.assertEqual(Counter(a["href"] for a in result.select("a[href]")),
                                 Counter(a["href"] for a in source_block.select("a[href]")))
                self.assertEqual(re.sub(r"\s", "", result.get_text(" ", strip=True)),
                                 re.sub(r"\s", "", next(r["target"] for r in cat.data["records"]
                                                          if r["id"] == record_id)))
                self.assertNotIn({"record": record_id, "state": "link-adaptation-required"}, hits)

    def test_dwarf_dynamic_trait_cards_use_approved_name_type_cost_and_options_labels(self):
        import markdown
        import json
        from types import SimpleNamespace
        import hooks
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        uri = "Browse/feature/index.md"
        source = (root / "docs" / uri).read_text(encoding="utf-8")
        html = markdown.markdown(source, extensions=["tables"])
        page = SimpleNamespace(file=SimpleNamespace(src_uri=uri), meta={}, title="",
                               toc=SimpleNamespace(items=[]), url="Browse/feature/")
        with patch.object(hooks, "catalog", cat), patch.object(hooks, "pages", []):
            translated = hooks.on_page_content(html, page, None, None)
        soup = BeautifulSoup(translated, "html.parser")
        items = json.loads(soup.select_one("script.sc-browse-data").string)
        dwarves = [item for item in items if item.get("href", "").startswith("trait/dwarf/")]
        labels = json.loads(soup.select_one("template#sc-l10n-labels")["data-labels"])
        self.assertEqual(len(dwarves), 7)
        self.assertEqual(labels["dwarf trait"], "矮人特性")
        self.assertEqual(labels["2 options"], "2 個選項")
        self.assertEqual(labels["level"], "等級")
        names = {item["name"]: item.get("tag") for item in dwarves}
        self.assertEqual(names["Signature Trait: Runic Carving"], "Signature Trait")
        self.assertEqual(names["Great Fortitude"], "2 Points")
        self.assertEqual(names["Grounded"], "1 Point")
        self.assertIn("grounded", labels)
        self.assertIn("堅硬石膚", labels["spark off your skin"])

    def test_wode_elf_dynamic_cards_bind_approved_names_and_flavor(self):
        import markdown
        import json
        from types import SimpleNamespace
        import hooks
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        uri = "Browse/feature/index.md"
        source = (root / "docs" / uri).read_text(encoding="utf-8")
        html = markdown.markdown(source, extensions=["tables"])
        page = SimpleNamespace(file=SimpleNamespace(src_uri=uri), meta={}, title="",
                               toc=SimpleNamespace(items=[]), url="Browse/feature/")
        with patch.object(hooks, "catalog", cat), patch.object(hooks, "pages", []):
            translated = hooks.on_page_content(html, page, None, None)
        soup = BeautifulSoup(translated, "html.parser")
        items = json.loads(soup.select_one("script.sc-browse-data").string)
        labels = json.loads(soup.select_one("template#sc-l10n-labels")["data-labels"])
        wode_traits = [item for item in items if item.get("href", "").startswith("trait/wode-elf/")]
        ability = next(item for item in items if item.get("href") == "ability/wode-elf/the-wode-defends/")
        self.assertEqual(len(wode_traits), 8)
        self.assertEqual(labels["wode elf"], "幻林精靈")
        self.assertEqual(labels["the wode defends"], "幻林護衛")
        self.assertIn("尖刺藤蔓", labels["thorny vines erupt from every surface and attempt to bind your foe."])
        self.assertIn("The Wode Defends", ability["name"])
        self.assertEqual(labels["wode elf trait"], "幻林精靈特性")
        self.assertEqual(labels["one creature"], "1 個生物")
        self.assertEqual(labels["you have speed 6."], "你的速度為 6。")
        self.assertEqual(labels["you have the following signature ability. signature abilities can be used at will."],
                         "你獲得以下招牌招式。招牌招式可以隨意使用。")
        self.assertEqual(labels["signature"], "招牌")
        self.assertEqual(labels["ranged **10**"], "遠程 **10**")

    def test_wode_final_story_and_name_copy_match_real_browse_and_read_sources(self):
        import markdown
        from collections import Counter
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        checks = [
            ("Browse/ancestry/wode-elf.md", "談幻林精靈"),
            ("Read/heroes/ancestries.md", "談幻林精靈"),
        ]
        for uri, expected_title in checks:
            source = (root / "docs" / uri).read_text(encoding="utf-8")
            body = source.split("---", 2)[-1] if source.startswith("---") else source
            rendered = markdown.markdown(body, extensions=["tables", "attr_list"])
            if uri == "Browse/ancestry/wode-elf.md":
                # MkDocs rewrites ancestry self-links to ./ before the plugin hook.
                rendered = rendered.replace('href="wode-elf.md"', 'href="./"')
            translated, hits = cat.translate_html(rendered, uri)
            source_soup = BeautifulSoup(rendered, "html.parser")
            soup = BeautifulSoup(translated, "html.parser")
            headings = [h for h in soup.find_all(["h2", "h3"]) if h.get_text(" ", strip=True) == expected_title]
            self.assertTrue(headings, uri)
            paragraphs = []
            for sibling in headings[0].find_next_siblings():
                if sibling.name and sibling.name.startswith("h"):
                    break
                if sibling.name == "p":
                    paragraphs.append(sibling)
            self.assertEqual(len(paragraphs), 38, uri)
            self.assertTrue(all(p.get("data-sc-l10n") for p in paragraphs), uri)
            self.assertFalse(any(hit["state"] == "link-adaptation-required"
                                 and hit["record"].startswith("heroes.ancestries.wode-elf.")
                                 for hit in hits), uri)
            self.assertIn("然後轉身大步離開", paragraphs[30].get_text(" ", strip=True), uri)
            self.assertIn("我們要去哪裡", paragraphs[31].get_text(" ", strip=True), uri)
            self.assertIn("傑瑞米湊近達德", paragraphs[36].get_text(" ", strip=True), uri)
            self.assertIn("幻林就是一場夢", paragraphs[37].get_text(" ", strip=True), uri)
            source_heading = next(h for h in source_soup.find_all(["h2", "h3"])
                                  if h.get_text(" ", strip=True) == "On Wode Elves")
            source_paragraphs = []
            for sibling in source_heading.find_next_siblings():
                if sibling.name and sibling.name.startswith("h"):
                    break
                if sibling.name == "p":
                    source_paragraphs.append(sibling)
            self.assertEqual(Counter(a["href"] for p in paragraphs for a in p.select("a[href]")),
                             Counter(a["href"] for p in source_paragraphs for a in p.select("a[href]")), uri)
            self.assertTrue(any(hit["record"] == "heroes.ancestries.wode-elf.on-wode-elves.paragraph.37"
                                for hit in hits if hit["state"] == "translated"), uri)

        source = (root / "docs/Read/heroes/ancestries.md").read_text(encoding="utf-8")
        rendered = markdown.markdown(source, extensions=["tables", "attr_list"])
        translated, _ = cat.translate_html(rendered, "Read/heroes/ancestries.md")
        source_soup = BeautifulSoup(rendered, "html.parser")
        soup = BeautifulSoup(translated, "html.parser")
        self.assertTrue(any(h.get_text(" ", strip=True) == "幻林精靈姓名" for h in soup.select("h5")))
        self.assertTrue(any("精靈普遍對性別" in p.get_text(" ", strip=True) for p in soup.select("p")))
        self.assertTrue(all(a.get("href") for h in soup.select("h5")
                            if h.get_text(" ", strip=True) == "幻林精靈姓名"
                            for a in h.select("a[href]")))

    def test_wode_read_scope_includes_trait_subheadings_and_embedded_card_labels(self):
        import markdown
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        source = (root / "docs/Read/heroes/ancestries.md").read_text(encoding="utf-8")
        rendered = markdown.markdown(source, extensions=["tables", "attr_list"])
        translated, hits = cat.translate_html(rendered, "Read/heroes/ancestries.md")
        soup = BeautifulSoup(translated, "html.parser")
        wode_section = next(h for h in soup.select("h2")
                            if h.get("data-scc") == "mcdm.heroes.v1/ancestry/wode-elf")
        wode_paragraphs = [p for p in soup.select("p")
                           if cat._read_section_is_wode(soup, p)
                           and not p.find_parent(["template", "script", "style"])]
        wode_cells = [value for value in soup.select(".sc-ability__cell .v")
                      if cat._read_section_is_wode(soup, value)]
        wode_text = " ".join(p.get_text(" ", strip=True) for p in wode_paragraphs)
        compact_wode = "".join(wode_text.split())
        self.assertIn("你的速度為6。", compact_wode)
        self.assertIn("你獲得以下招牌招式。招牌招式可以隨意使用。", compact_wode)
        self.assertIn("1個生物", "".join("".join(v.get_text(" ", strip=True).split()) for v in wode_cells))
        self.assertNotIn("You have speed 6.", wode_text)
        self.assertTrue(any(h["record"] == "heroes.ancestries.wode-elf.trait.swift.effect"
                            and h["state"] == "translated" for h in hits))
        expected_records = {
            "heroes.ancestries.wode-elf.signature.wode-elf-glamor.effect",
            "heroes.ancestries.wode-elf.trait.forest-walk.effect",
            "heroes.ancestries.wode-elf.trait.quick-and-brutal.effect",
            "heroes.ancestries.wode-elf.trait.otherworldly-grace.effect",
            "heroes.ancestries.wode-elf.trait.revisit-memory.effect",
            "heroes.ancestries.wode-elf.trait.swift.effect",
            "heroes.ancestries.wode-elf.trait.the-wode-defends.effect",
        }
        translated_records = {h["record"] for h in hits if h["state"] == "translated"}
        self.assertTrue(expected_records.issubset(translated_records))
        # The same exact short label must not leak into a different ancestry.
        high_elf = next(h for h in wode_section.find_all_next("h2"))
        high_elf_copy = high_elf.find_next("p")
        self.assertFalse(cat._read_section_is_wode(soup, high_elf_copy))

    def test_wode_complete_ability_page_uses_approved_results_and_keeps_links(self):
        import markdown
        from collections import Counter
        root = Path(__file__).resolve().parents[1]
        uri = "Browse/feature/ability/wode-elf/the-wode-defends.md"
        source = (root / "docs" / uri).read_text(encoding="utf-8")
        body = source.split("---", 2)[-1]
        rendered = markdown.markdown(body, extensions=["tables", "attr_list"])
        translated, _ = Catalog(load_catalog()).translate_html(rendered, uri)
        source_soup = BeautifulSoup(rendered, "html.parser")
        soup = BeautifulSoup(translated, "html.parser")
        self.assertEqual(["".join(x.get_text(" ", strip=True).split()) for x in soup.select(".sc-ability__tier .res")], [
            "2+力量或敏捷傷害；敏捷<弱，緩速（豁免解除）",
            "3+力量或敏捷傷害；敏捷<中，緩速（豁免解除）",
            "5+力量或敏捷傷害；敏捷<強，束縛（豁免解除）",
        ])
        values = [cell.select_one(".v") for cell in soup.select(".sc-ability__cell")]
        self.assertEqual("".join(values[0].get_text(" ", strip=True).split()), "遠程10")
        self.assertEqual("".join(values[1].get_text(" ", strip=True).split()), "1個生物")
        chars = soup.select_one(".sc-ability__pr-head .chars")
        self.assertEqual("".join(chars.get_text(" ", strip=True).split()), "力量或敏捷")
        self.assertIsNone(chars.find("p"))
        self.assertEqual([a.get_text(strip=True) for a in chars.select("a")], ["力量", "敏捷"])
        self.assertIn("招牌", soup.select_one(".sc-head__right-primary").get_text(" ", strip=True))
        self.assertEqual(Counter(a["href"] for a in soup.select("a[href]")),
                         Counter(a["href"] for a in source_soup.select("a[href]")))

    def test_wode_signature_ability_card_does_not_drop_untranslated_at_will_rule(self):
        import markdown
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        uri = "Browse/feature/trait/wode-elf/the-wode-defends.md"
        source = (root / "docs" / uri).read_text(encoding="utf-8")
        body = source.split("---", 2)[-1]
        rendered = markdown.markdown(body, extensions=["tables", "attr_list"])
        translated, _ = cat.translate_html(rendered, uri)
        soup = BeautifulSoup(translated, "html.parser")
        text = soup.select_one(".sc-trait__body").get_text(" ", strip=True)
        self.assertNotIn("You have the following signature ability.", text.replace("ability .", "ability."))
        self.assertNotIn("Signature abilities can be used at will.", text)
        self.assertIn("你獲得以下招牌招式。招牌招式可以隨意使用。", "".join(text.split()))
        self.assertEqual(cat.lookup(
            "You have the following signature ability. Signature abilities can be used at will.", uri)[0],
            "你獲得以下招牌招式。招牌招式可以隨意使用。")

    def test_wode_approved_strings_reach_static_ancestry_trait_and_ability_indexes(self):
        import markdown
        from collections import Counter
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        checks = [
            ("Browse/ancestry/index.md", "a.sc-card__link[href$='wode-elf/']", "幻林精靈"),
            ("Browse/feature/trait/wode-elf/index.md", ".sc-prevs", "幻林護衛"),
            ("Browse/feature/ability/wode-elf/index.md", ".sc-prevs", "幻林護衛"),
        ]
        for uri, selector, expected in checks:
            source = (root / "docs" / uri).read_text(encoding="utf-8")
            rendered = markdown.markdown(source, extensions=["tables", "attr_list"])
            translated, _ = cat.translate_html(rendered, uri)
            source_soup = BeautifulSoup(rendered, "html.parser")
            soup = BeautifulSoup(translated, "html.parser")
            cards = soup.select(selector)
            if uri == "Browse/ancestry/index.md":
                cards = [card.find_parent(class_="sc-card") for card in cards]
            self.assertTrue(cards, uri)
            self.assertIn(expected, " ".join(card.get_text(" ", strip=True) for card in cards), uri)
            if uri == "Browse/feature/trait/wode-elf/index.md":
                previews = soup.select(".sc-prev--trait")
                self.assertEqual(len(previews), 8)
                self.assertIn("你的速度為 6。", " ".join(p.get_text(" ", strip=True) for p in previews))
                self.assertNotIn("You have speed 6.", " ".join(p.get_text(" ", strip=True) for p in previews))
            if uri == "Browse/feature/ability/wode-elf/index.md":
                preview = soup.select_one(".sc-prev--ability")
                self.assertIsNotNone(preview)
                self.assertEqual(["".join(value.get_text(" ", strip=True).split())
                                  for value in preview.select(".sc-prev__meta .v")], ["遠程10", "1個生物"])
                self.assertIn("魔法", preview.get_text(" ", strip=True))
                self.assertIn("遠程", preview.get_text(" ", strip=True))
                self.assertIn("打擊", preview.get_text(" ", strip=True))
            self.assertEqual(Counter(a["href"] for a in soup.select("a[href]")),
                             Counter(a["href"] for a in source_soup.select("a[href]")), uri)

    def test_localized_card_fields_keep_inline_markup(self):
        cat = Catalog(load_catalog())
        source = ('<div class="sc-ability__cell"><div class="v">1 burst</div></div>'
                  '<div class="sc-ability__tier"><span class="res">2 damage</span></div>')
        result, _ = cat.translate_html(source, "Browse/ancestry/dragon-knight.md")
        soup = BeautifulSoup(result, "html.parser")
        self.assertFalse(soup.select(".v p, .res p"))
        self.assertEqual(soup.select_one(".res").get_text(), "2 傷害")

    def test_approved_dragon_knight_text_reaches_ancestry_and_feature_indexes(self):
        from types import SimpleNamespace
        from core import normalized, scope_matches
        import hooks

        cat = Catalog(load_catalog())
        summary = "Dragon knights are muscled draconic humanoids who stand between 6 and 7 feet tall. The scales covering their reptilian heads, bodies, and tails can be almost any color. All dragon knights have wings, but on only a few are those wings big enough to let them fly."
        self.assertTrue(scope_matches("ancestry:dragon-knight", "Browse/ancestry/index.md"))
        summary_record = next(r for r in cat.data["records"]
                              if r["id"] == "heroes.ancestries.dragon-knight.summary")
        self.assertEqual(cat.lookup(summary, "Browse/ancestry/index.md"),
                         (summary_record["target"], summary_record["id"], summary_record["scope"]))

        item = {"href": "trait/dragon-knight/draconian-pride/", "name": "Draconian Pride",
                "klass": "Dragon Knight", "level": 0,
                "flavor": "You let loose a mighty roar to shake your foes’ spirits.",
                "grants": "the Draconian Pride main action"}
        choice = {"href": "trait/dragon-knight/dragon-knight-traits/", "name": "Dragon Knight Traits",
                  "klass": "Dragon Knight", "level": 0, "options": 2,
                  "flavor": "Even should the sun stop in the sky."}
        ability = {"kind": "ability", "href": "ability/dragon-knight/dragon-breath/",
                   "name": "Dragon Breath", "klass": "Dragon Knight", "level": 0,
                   "cost": "Signature", "keywords": ["Area", "Magic"],
                   "distance": "**3** cube within **1**", "targets": "Each enemy in the area",
                   "flavor": "A furious exhalation of energy washes over your foes."}
        html = '<script class="sc-browse-data">' + json.dumps([item, choice, ability]) + '</script>'
        page = SimpleNamespace(file=SimpleNamespace(src_uri="Browse/feature/index.md"), meta={}, title="",
                               toc=SimpleNamespace(items=[]), url="Browse/feature/")
        with patch.object(hooks, "catalog", cat), patch.object(hooks, "pages", []):
            translated = hooks.on_page_content(html, page, None, None)
        result = BeautifulSoup(translated, "html.parser")
        data = json.loads(result.select_one("script.sc-browse-data").string)
        labels = json.loads(result.select_one("template#sc-l10n-labels")["data-labels"])
        self.assertEqual(data[0]["tag"], "2 Points")
        self.assertEqual(labels["draconian pride"], "龍人霸氣")
        self.assertEqual(labels["dragon knight trait"], "龍騎士特性")
        self.assertEqual(labels["2 options"], "2 個選項")
        self.assertEqual(labels["grants the draconian pride main action"], "獲得招式：龍人霸氣")
        self.assertEqual(data[2]["distance"], "**3** cube within **1**")
        self.assertEqual(labels["dragon breath"], "龍息")
        self.assertEqual(labels["signature"], "招牌")
        self.assertEqual(labels["area"], "區域")
        self.assertEqual(labels["from"], "來源")
        self.assertEqual(labels["lv"], "等級")
        self.assertEqual(labels["distance"], "射程")
        self.assertEqual(labels["targets"], "目標")
        self.assertEqual(labels["**3** cube within **1**"], "**1** 格內 **3** 立方")
        self.assertEqual(labels["each enemy in the area"], "區域內每個敵人")
        self.assertEqual(labels["level"], "等級")
        self.assertIn("狂怒", labels[normalized(ability["flavor"]).casefold()])
        flavor_key = normalized(item["flavor"]).casefold()
        approved_flavor = cat.lookup(item["flavor"], "Browse/feature/trait/dragon-knight/draconian-pride.md",
                                      "mcdm.heroes.v1/feature.trait.dragon-knight/draconian-pride")
        self.assertEqual(labels[flavor_key], approved_flavor[0])

    def test_dragon_knight_story_links_and_ability_distances_keep_context(self):
        from core import fingerprint

        data = {
            "format": "steel-compendium-catalog/v1",
            "locale": "zh-TW",
            "records": [
                row("human", "人類", id="term.human", scope="heroes"),
                row("dwarf", "矮人", id="term.dwarf", scope="heroes"),
                row("burst", "爆發", id="term.burst", scope="heroes"),
                row("cube", "立方", id="term.cube", scope="heroes"),
                row("push", "推動", id="term.push", scope="heroes"),
                row("1 burst", "1 爆發", id="heroes.ancestries.dragon-knight.ability.draconian-pride.distance",
                    scope="ancestry:dragon-knight"),
                row("3 cube within 1", "1 格內 3 立方",
                    id="heroes.ancestries.dragon-knight.ability.dragon-breath.distance",
                    scope="ancestry:dragon-knight"),
                row("5 damage; push 1", "5 傷害；推動 1",
                    id="heroes.ancestries.dragon-knight.ability.result.pride.12-16",
                    scope="ancestry:dragon-knight"),
                row("Three [human](../../Browse/ancestry/human.md) scouts and one "
                    "[human](../../Browse/ancestry/human.md) guide, plus two "
                    "[dwarf](../../Browse/ancestry/dwarf.md) allies and one "
                    "[dwarf](../../Browse/ancestry/dwarf.md) elder.",
                    "三名人類斥候和一名人類嚮導，另有兩名矮人同伴和一名矮人長者。",
                    id="heroes.ancestries.dragon-knight.on-dragon-knights.paragraph.03",
                    scope="ancestry:dragon-knight"),
            ],
        }
        cat = Catalog(data)
        story = ('<p>Three <a href="../../Browse/ancestry/human.md">human</a> scouts and one '
                 '<a href="../../Browse/ancestry/human.md">human</a> guide, plus two '
                 '<a href="../../Browse/ancestry/dwarf.md">dwarf</a> allies and one '
                 '<a href="../../Browse/ancestry/dwarf.md">dwarf</a> elder.</p>')
        rendered, hits = cat.translate_html(story, "Read/heroes/ancestries.md")
        parsed = BeautifulSoup(rendered, "html.parser")
        self.assertEqual([a.get_text() for a in parsed.select("p a")], ["人類", "人類", "矮人", "矮人"])
        self.assertEqual(len({a["href"] for a in parsed.select("p a")}), 2)
        self.assertIn("heroes.ancestries.dragon-knight.on-dragon-knights.paragraph.03",
                      {item["record"] for item in hits})

        card = ('<div class="sc-ability__cell"><div class="l">Distance</div>'
                '<div class="v">3 <a href="../../../../rule/combat/cube/">cube</a> within 1</div></div>')
        translated, _ = cat.translate_html(card, "Browse/ancestry/dragon-knight.md")
        card_html = BeautifulSoup(translated, "html.parser")
        value = card_html.select_one(".sc-ability__cell .v")
        self.assertEqual(value.get_text(" ", strip=True), "1 格內 3 立方")
        self.assertEqual(value.a["href"], "../../../../rule/combat/cube/")

        outcome = ('<div class="sc-ability__tier"><span class="res">5 damage; '
                   '<a href="../../../../movement/forced-movement/">push</a> 1</span></div>')
        translated_outcome, _ = cat.translate_html(
            outcome, "Browse/feature/ability/dragon-knight/draconian-pride.md")
        result_html = BeautifulSoup(translated_outcome, "html.parser")
        result = result_html.select_one(".sc-ability__tier .res")
        self.assertEqual(result.get_text(" ", strip=True).replace("； ", "；"), "5 傷害；推動 1")
        self.assertEqual(result.a["href"], "../../../../movement/forced-movement/")

        exported = cat.translate_markdown(
            "| **📏 3 [cube](../../../rule/combat/cube.md) within 1** | **🎯 Each enemy in the area** |",
            "Browse/feature/ability/dragon-knight/dragon-breath.md",
        )
        self.assertIn("📏 1 格內 3 [立方](../../../rule/combat/cube.md)", exported)
        exported = cat.translate_markdown(
            "- **12-16:** 5 damage; [push](../../../movement/forced-movement.md) 1",
            "Browse/feature/ability/dragon-knight/draconian-pride.md",
        )
        self.assertIn("5 傷害；[推動](../../../movement/forced-movement.md) 1", exported)

    def test_dragon_knight_story_all_paragraphs_and_authored_links(self):
        import markdown

        cat = Catalog(load_catalog())
        records = [r for r in cat.data["records"]
                   if r["id"].startswith("heroes.ancestries.dragon-knight.on-dragon-knights.paragraph.")]
        self.assertEqual(len(records), 37)
        translated_ids = set()
        link_count = 0
        for record in records:
            source_html = markdown.markdown(record["source"])
            expected_hrefs = [a.get("href") for a in BeautifulSoup(source_html, "html.parser").select("a[href]")]
            for uri in ["Read/heroes/ancestries.md", "Browse/ancestry/dragon-knight.md"]:
                html, hits = cat.translate_html(source_html, uri)
                parsed = BeautifulSoup(html, "html.parser")
                self.assertIn(record["id"], {hit["record"] for hit in hits if hit["state"] == "translated"})
                self.assertEqual([a.get("href") for a in parsed.select("a[href]")], expected_hrefs)
                translated_ids.update(hit["record"] for hit in hits if hit["state"] == "translated")
            link_count += len(expected_hrefs)
        self.assertEqual(len(translated_ids), 37)
        self.assertEqual(link_count, 20)

    def test_dragon_knight_intro_typography_and_reused_signature_sentence(self):
        cat = Catalog(load_catalog())
        intro = ('<p>The ritual of Dracogenesis that grants the power to create a generation of '
                 '<a href="./">dragon knights</a>—also known as draconians or '
                 'wyrmwights—is obscure and supremely difficult for even an experienced sorcerer to '
                 'master. Small populations of draconians in Khemhara, Higara, and Khoursir attest to '
                 'this. Descendants of original generations created millennia ago by powerful wizards, '
                 'they have never been numerous. A typical clutch yields only a single egg. After only '
                 'a few generations, these draconians begin to show new adaptations like feathers or '
                 'frilled ridges.</p>')
        translated, hits = cat.translate_html(intro, "Browse/ancestry/dragon-knight.md")
        parsed = BeautifulSoup(translated, "html.parser")
        self.assertIn("heroes.ancestries.dragon-knight.description.1",
                      {hit["record"] for hit in hits if hit["state"] == "translated"})
        self.assertNotIn("Dracogenesis", parsed.p.get_text())
        self.assertTrue(any(ord(char) > 127 for char in parsed.p.get_text()))
        self.assertEqual(parsed.p.a["href"], "./")

        story = ('<p>Vaantikalisax\'s reptile eyes flashed in anger. "They <em>had it</em>! Thirty years, '
                 'and what did it amount to?! I watched Ajax... I watched him..." The '
                 '<a href="./">dragon knight\'s</a> eyes flinched. His clawed hands tightened on his mace '
                 'and shield. "I watched the oath... fail."</p>')
        translated, hits = cat.translate_html(story, "Browse/ancestry/dragon-knight.md")
        parsed = BeautifulSoup(translated, "html.parser")
        self.assertIn("heroes.ancestries.dragon-knight.on-dragon-knights.paragraph.34",
                      {hit["record"] for hit in hits if hit["state"] == "translated"})
        self.assertNotIn("Vaantikalisax's reptile eyes", parsed.p.get_text())
        self.assertEqual(parsed.p.a["href"], "./")

        leadin = ('<p>You have the following <a href="../../rule/combat/signature-ability/">'
                  'signature ability</a>.</p>')
        translated, hits = cat.translate_html(leadin, "Browse/ancestry/dragon-knight.md")
        parsed = BeautifulSoup(translated, "html.parser")
        self.assertEqual(parsed.p.get_text(), "你獲得以下招牌招式。")
        self.assertEqual(parsed.p.a["href"], "../../rule/combat/signature-ability/")
        self.assertIn("heroes.ancestries.wode-elf.trait.the-wode-defends.effect",
                      {hit["record"] for hit in hits if hit["state"] == "translated"})

    def test_dragon_knight_card_power_roll_and_name_measurement_labels(self):
        cat = Catalog(load_catalog())
        card = ('<div class="sc-ability__pr-head"><span class="pre">Power Roll +</span>'
                '<span class="chars"><a href="../../../../rule/character/might/">Might</a> or '
                '<a href="../../../../rule/character/presence/">Presence</a></span></div>')
        html, _ = cat.translate_html(card, "Browse/feature/ability/dragon-knight/draconian-pride.md")
        parsed = BeautifulSoup(html, "html.parser")
        self.assertEqual(parsed.select_one(".pre").get_text(), "檢定 +")
        self.assertEqual(parsed.select_one(".chars").get_text(" ", strip=True), "力量 / 氣場")
        self.assertEqual([a["href"] for a in parsed.select("a")], [
            "../../../../rule/character/might/", "../../../../rule/character/presence/"
        ])
        labels = ('<h3>Dragon Knight Names</h3><strong>Feminine:</strong>'
                  '<strong>Gender Neutral:</strong><strong>Masculine:</strong>'
                  '<table><tr><th>Ancestry</th><th>Height in Feet/<br>Inches</th>'
                  '<th>Weight in<br>Pounds</th><th>Life Expectancy in<br>Years</th></tr></table>')
        translated, _ = cat.translate_html(labels, "Read/heroes/ancestries.md")
        table = BeautifulSoup(translated, "html.parser")
        self.assertEqual(table.h3.get_text(), "龍騎士姓名")
        self.assertEqual([x.get_text(" ", strip=True) for x in table.select("strong")], ["女性名：", "中性名：", "男性名："])
        self.assertEqual([x.get_text(" ", strip=True) for x in table.select("th")], [
            "族裔", "身高（呎 / 吋）", "體重（磅）", "預期壽命（年）"
        ])

        leadin = ('<p>You have 3 ancestry points to spend on the following traits. '
                  '(<em>Quick Build:</em> <a href="../../feature/ability/dragon-knight/dragon-breath/">'
                  'Dragon Breath</a>, Prismatic Scales.)</p>')
        quick, _ = cat.translate_html(leadin, "Browse/ancestry/dragon-knight.md")
        quick_dom = BeautifulSoup(quick, "html.parser")
        self.assertEqual(quick_dom.p.get_text("", strip=True),
                         "你有 3 點族裔點數，可以用來購買以下特性。（速選：龍息、虹彩鱗片。）")
        self.assertEqual(quick_dom.p.a.get_text(), "龍息")
        self.assertEqual(quick_dom.p.a["href"], "../../feature/ability/dragon-knight/dragon-breath/")

    def test_devil_story_real_sources_keep_approved_prose_breaks_and_links(self):
        import markdown
        import re
        from collections import Counter
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        expected = {r['id']: r for r in cat.data['records'] if '.devil.on-devils.' in r['id']}
        self.assertEqual(len(expected), 47)
        for uri in ['Browse/ancestry/devil.md', 'Read/heroes/ancestries.md']:
            source = (root / 'docs' / uri).read_text(encoding='utf8')
            story = re.split(r'^#{2,3} On Devils[^\n]*\n\n', source, maxsplit=1, flags=re.M)[1]
            story = re.split(r'^#{2,3} Devil Traits[^\n]*\n', story, maxsplit=1, flags=re.M)[0]
            rendered = markdown.markdown('## On Devils\n\n' + story)
            html, hits = cat.translate_html(rendered, uri)
            soup = BeautifulSoup(html, 'lxml')
            self.assertEqual(set(expected), {h['record'] for h in hits if h['state'] == 'translated'})
            self.assertFalse(soup.select('p p,p hr,h2 p'))
            self.assertEqual(Counter(a['href'] for a in soup.select('a[href]')),
                             Counter(a['href'] for a in BeautifulSoup(rendered, 'lxml').select('a[href]')))
            for rid, record in expected.items():
                if rid.endswith('paragraph.45'):
                    continue
                target = record['target']
                if rid.endswith('paragraph.44'):
                    target += expected[rid[:-2] + '45']['target']
                actual = ''.join(n.get_text() for n in soup.select(f'[data-sc-l10n="{rid}"]'))
                compact = lambda text: re.sub(r'\s', '', text)
                self.assertEqual(compact(actual), compact(BeautifulSoup(markdown.markdown(target), 'lxml').get_text()))
            self.assertIsNotNone(soup.select_one('hr[data-sc-l10n$="paragraph.28"]'))
            changed, _ = cat.translate_html(rendered.replace('outrageous sums', 'modest sums'), uri)
            changed_soup = BeautifulSoup(changed, 'lxml')
            self.assertIn('modest sums', changed_soup.get_text())
            self.assertFalse(changed_soup.select('[data-sc-l10n-records$="paragraph.45"]'))
            again, again_hits = cat.translate_html(html, uri)
            self.assertEqual([str(n) for n in BeautifulSoup(again, 'lxml').select('h2,p,hr')],
                             [str(n) for n in soup.select('h2,p,hr')])
            self.assertEqual(again_hits, [])

    def test_dwarf_story_real_browse_and_read_sources_keep_user_final_and_links(self):
        import markdown
        import re
        from collections import Counter
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        expected = {r['id']: r for r in cat.data['records']
                    if r['id'].startswith('heroes.ancestries.dwarf.on-dwarves.')}
        self.assertEqual(len(expected), 49)
        for uri in ['Browse/ancestry/dwarf.md', 'Read/heroes/ancestries.md']:
            source = (root / 'docs' / uri).read_text(encoding='utf8')
            heading_match = re.search(r'^#{2,3} On Dwarves[^\n]*$', source, flags=re.M)
            self.assertIsNotNone(heading_match)
            heading = heading_match.group(0)
            story = re.split(r'^#{2,3} On Dwarves[^\n]*\n\n', source, maxsplit=1, flags=re.M)[1]
            story = re.split(r'^#{2,3} Dwarf Traits[^\n]*\n', story, maxsplit=1, flags=re.M)[0]
            rendered = markdown.markdown(heading + "\n\n" + story, extensions=["attr_list"])
            html, hits = cat.translate_html(rendered, uri)
            soup = BeautifulSoup(html, 'lxml')
            translated_ids = {h['record'] for h in hits if h['state'] == 'translated'}
            self.assertEqual(set(expected), translated_ids)
            self.assertEqual(len(soup.select('p[data-sc-l10n]')), 48)
            title = soup.select_one('h2,h3')
            self.assertEqual(title.get_text(), '談矮人')
            self.assertFalse(any(h['state'] == 'link-adaptation-required' for h in hits))
            self.assertEqual(Counter(a['href'] for a in soup.select('a[href]')),
                             Counter(a['href'] for a in BeautifulSoup(rendered, 'lxml').select('a[href]')))
            self.assertEqual(soup.select_one('a[href$="/class/troubadour.md"]').get_text(), '遊唱家')
            for p in soup.select('p[data-sc-l10n]'):
                target = expected[p['data-sc-l10n']]['target']
                compact = lambda text: re.sub(r'\s', '', text)
                target_text = BeautifulSoup(markdown.markdown(target), 'lxml').get_text()
                self.assertEqual(compact(p.get_text()), compact(target_text))
            again, again_hits = cat.translate_html(html, uri)
            self.assertEqual([str(n) for n in BeautifulSoup(again, 'lxml').select('h2,h3,p')],
                             [str(n) for n in soup.select('h2,h3,p')])
            self.assertEqual(again_hits, [])

    def test_wode_elf_scope_and_quick_build_use_approved_source_records(self):
        from bs4 import BeautifulSoup
        from scripts.l10n.core import scope_matches
        cat = Catalog(load_catalog())
        self.assertTrue(scope_matches("ancestry:wode-elf", "Browse/ancestry/index.md"))
        self.assertTrue(scope_matches("ancestry:wode-elf", "Browse/feature/trait/wode-elf/index.md"))
        self.assertFalse(scope_matches("ancestry:wode-elf", "Browse/ancestry/high-elf.md"))

        intro = "You have 3 ancestry points to spend on the following traits."
        quick = "Quick Build: Swift, Otherworldly Grace."
        source = f"{intro} ({quick})"
        element = BeautifulSoup("<p><em>Quick Build:</em> Swift, Otherworldly Grace.</p>", "html.parser").p
        composed = cat._ancestry_quick_build(element, source, "Browse/ancestry/wode-elf.md", "")
        self.assertIsNotNone(composed)
        self.assertEqual(composed[0], "你有 3 點族裔點數，可以用來購買以下特性。")
        self.assertIn("迅捷步伐", composed[2].get_text())
        self.assertIn("非凡優雅", composed[2].get_text())

    def test_wode_elf_approved_descriptions_match_real_browse_and_read_sources(self):
        import markdown
        import re
        from collections import Counter
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        expected = {
            "heroes.ancestries.wode-elf.description.1",
            "heroes.ancestries.wode-elf.description.2",
        }
        for uri in ["Browse/ancestry/wode-elf.md", "Read/heroes/ancestries.md"]:
            source = (root / "docs" / uri).read_text(encoding="utf-8")
            if uri.startswith("Browse/"):
                section = source.split("---", 2)[-1].split("## On Wode Elves", 1)[0]
            else:
                start = re.search(r"^## Wode Elf \{", source, flags=re.M).start()
                section = source[start:].split("### On Wode Elves", 1)[0]
            rendered = markdown.markdown(section, extensions=["tables", "attr_list"])
            if uri.startswith("Browse/"):
                # Reproduce MkDocs' rewritten root-relative ancestry self-links.
                rendered = rendered.replace('href="wode-elf.md"', 'href="./"')
            html, hits = cat.translate_html(rendered, uri)
            translated = {hit["record"] for hit in hits if hit["state"] == "translated"}
            self.assertTrue(expected.issubset(translated), uri)
            soup = BeautifulSoup(html, "html.parser")
            self.assertEqual(len(soup.select("p[data-sc-l10n]")), 2, uri)
            self.assertEqual(Counter(a["href"] for a in soup.select("a[href]")),
                             Counter(a["href"] for a in BeautifulSoup(rendered, "html.parser").select("a[href]")))
            self.assertFalse(any(hit["state"] == "link-adaptation-required" for hit in hits), uri)
            self.assertTrue(all("Children of the sylvan" not in p.get_text(" ", strip=True)
                                and "natural ability to mask" not in p.get_text(" ", strip=True)
                                for p in soup.select("p[data-sc-original]")), uri)

    def test_approved_on_humans_story_all_paragraphs_and_narrative_links(self):
        import markdown
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        source = (root/'docs/Browse/ancestry/human.md').read_text(encoding='utf8').split('## On Humans\n\n')[1].split('\n\n## Human Traits')[0]
        rendered = markdown.markdown(source).replace('href="human.md"','href="./"')
        html, hits = cat.translate_html(rendered,'Browse/ancestry/human.md')
        soup = BeautifulSoup(html,'lxml')
        expected = {r['id']:r for r in cat.data['records'] if r['id'].startswith('heroes.ancestries.human.on-humans.paragraph.')}
        self.assertEqual(len(soup.select('p[data-sc-l10n]')),17)
        for p in soup.select('p[data-sc-l10n]'):
            self.assertEqual(p.get_text(),expected[p['data-sc-l10n']]['target'])
        self.assertEqual([a.get_text() for a in soup.select('a[href="../class/conduit.md"],a[href="../class/censor.md"],a[href="../class/shadow.md"]')],['使徒','懲戒惡徒者','行於陰影之人'])
        self.assertFalse(any(h['state']=='link-adaptation-required' for h in hits))

    def test_book_human_introduction_preserves_approved_text_and_links(self):
        import markdown
        root = Path(__file__).resolve().parents[1]
        cat = Catalog(load_catalog())
        source = (root / "docs/Browse/ancestry/human.md").read_text(encoding="utf-8")
        paragraphs = source.split("\n\n")
        intro = next(p for p in paragraphs if p.startswith("[Humans]"))
        quote = next(p for p in paragraphs if p.startswith('"No one knows'))
        rendered = markdown.markdown(intro + "\n\n" + quote)
        result, hits = cat.translate_html(rendered, "Browse/ancestry/human.md")
        soup = BeautifulSoup(result, "lxml")
        records = {r["id"]: r for r in cat.data["records"]}
        for i, p in enumerate(soup.select("p"), 1):
            self.assertEqual(p.get_text(), records[f"heroes.ancestries.human.description.{i}"]["target"])
        self.assertEqual([a["href"] for a in soup.select("a")],
                         ["human.md", "../rule/general/supernatural.md", "dwarf.md", "orc.md", "human.md"])
        self.assertEqual(soup.find("a", href="../rule/general/supernatural.md").get_text(), "超自然")
        # MkDocs rewrites main-page self links to ./ before invoking the hook.
        main_html, _ = cat.translate_html(rendered.replace('href="human.md"', 'href="./"'), "Browse/ancestry/human.md")
        main = BeautifulSoup(main_html, "lxml")
        self.assertEqual([p.get_text() for p in main.select("p")], [p.get_text() for p in soup.select("p")])
        self.assertEqual([a.get_text() for a in main.select('a[href="./"]')], ["人類", "人類"])
        changed, _ = cat.translate_html(rendered.replace("oily smell", "pleasant smell"), "Browse/ancestry/human.md")
        self.assertIn("pleasant smell", changed)

    def test_public_catalog_rejects_drafts(self):
        data = json.dumps({"format": "steel-compendium-catalog/v1", "locale": "zh-TW",
                           "records": [row("Home", "首頁", "ui", status="DRAFT")]})
        with patch.object(Path, "read_text", return_value=data):
            with self.assertRaisesRegex(ValueError, "approved records only"):
                load_catalog()

    def test_master_import_rejects_unapproved_stale_and_wrong_identity(self):
        current = {"master": {"spreadsheetId": "master"}, "records": []}
        capture = {"format": "steel-compendium-master-approved/v1", "master": {"spreadsheetId": "master"},
                   "records": [row("Home", "首頁", "ui", status="DRAFT")]}
        with self.assertRaises(ValueError):
            convert(capture, current)
        capture["records"][0] = dict(row("Home", "首頁", "ui"), sourceHash="stale")
        with self.assertRaises(ValueError):
            convert(capture, current)
        capture["master"]["spreadsheetId"] = "another"
        with self.assertRaises(ValueError):
            convert(capture, current)

    def test_approved_exact_source_only(self):
        cat = Catalog({"records": [row("You gain the ability to fly.", "你獲得飛行能力。") ]})
        html, _ = cat.translate_html("<p>You gain the ability to fly.</p>", "Browse/ancestry/human.md")
        self.assertIn("你獲得飛行能力", html)
        for source in ["You gain the ability to fly faster.", "You gain a different ability."]:
            html, _ = cat.translate_html(f"<p>{source}</p>", "Browse/ancestry/human.md")
            self.assertIn(source, html)

    def test_draft_stale_and_conflicting_approval_fall_back(self):
        for records in [[row("Human", "人類", "names", status="DRAFT")],
                        [dict(row("Human", "人類", "names"), sourceHash="stale")],
                        [row("Human", "人類", "names"), row("Human", "另一譯名", "names", id="two")]]:
            html, _ = Catalog({"records": records}).translate_html("<h1>Human</h1>", "Browse/ancestry/human.md")
            self.assertNotIn("人類", html)

    def test_context_ids_links_and_machine_values_survive(self):
        cat = Catalog({"records": [row("Human", "人類", "names", "ancestry:human")]})
        original = '<h1 id="human">Human<a class="headerlink" href="#human">¶</a></h1><script>{"name":"Human"}</script><input value="Human">'
        html, _ = cat.translate_html(original, "Browse/ancestry/human.md")
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(soup.h1["id"], "human")
        self.assertEqual(soup.a["href"], "#human")
        self.assertEqual(soup.script.string, '{"name":"Human"}')
        self.assertEqual(soup.input["value"], "Human")
        other, _ = cat.translate_html("<h1>Human</h1>", "Browse/ancestry/devil.md")
        self.assertNotIn("人類", other)

    def test_prose_keeps_link_or_falls_back_whole_block(self):
        records = [row("You gain the Nature skill.", "你獲得自然技能。"), row("Nature", "自然", "glossary", id="term")]
        html, _ = Catalog({"records": records}).translate_html('<p>You gain the <a href="nature/">Nature</a> skill.</p>', "Browse/skill/nature.md")
        self.assertIn('href="nature/"', html)
        self.assertIn("你獲得", html)
        self.assertIn("自然", html)
        records[1]["target"] = "不同名稱"
        html, hits = Catalog({"records": records}).translate_html('<p>You gain the <a href="nature/">Nature</a> skill.</p>', "Browse/skill/nature.md")
        self.assertIn("You gain", html)
        self.assertIn(">Nature</a>", html)
        self.assertTrue(any(x["state"] == "link-adaptation-required" for x in hits))

    def test_approved_path_labels_adapt_inflected_links_exactly(self):
        source = "If you are force moved, some conditions require tests."
        target = "若你被強制移動，某些狀態需要進行考驗。"
        records = [
            row(source, target, scope="ancestry:human"),
            row("Forced Movement", "強制移動", "glossary", id="forced-movement"),
            row("Condition", "狀態", "glossary", id="condition"),
            row("Test", "考驗", "glossary", id="test"),
        ]
        cat = Catalog({"records": records})
        html, hits = cat.translate_html(
            '<p>If you are <a href="../../movement/forced-movement/">force moved</a>, '
            'some <a href="../../rule/combat/condition/">conditions</a> require '
            '<a href="../../rule/test/test/">tests</a>.</p>',
            "Browse/feature/trait/human/perseverance.md",
        )
        soup = BeautifulSoup(html, "html.parser")
        self.assertEqual([a.get_text() for a in soup.select("a")], ["強制移動", "狀態", "考驗"])
        self.assertEqual([a["href"] for a in soup.select("a")], [
            "../../movement/forced-movement/", "../../rule/combat/condition/", "../../rule/test/test/"
        ])
        self.assertTrue(any(x["state"] == "translated" for x in hits))

    def test_human_forced_movement_distance_link_uses_contextual_distance(self):
        source = "Your connection to the natural world allows you to resist certain supernatural effects. You ignore temporary difficult terrain created by magic and psionic abilities. Additionally, when you are force moved by a magic or psionic ability, you can reduce the forced movement distance by 1."
        target = "你與大自然的連結能讓你抵抗某些超常效果。你可以無視魔法或靈能招式所創造的臨時困難地形。此外，當你被魔法或靈能招式強制移動時，你可以將強制移動的距離 -1。"
        records = [
            row(source, target, scope="ancestry:human", id="heroes.ancestries.human.trait.cant-take-hold.effect"),
            row("Supernatural", "超常", "glossary", id="supernatural"),
            row("Difficult Terrain", "困難地形", "glossary", id="difficult-terrain"),
            row("Forced Movement", "強制移動", "glossary", id="forced-movement"),
            row("Distance", "射程", "glossary", id="distance"),
        ]
        cat = Catalog({"records": records})
        html, hits = cat.translate_html(
            '<p>Your connection to the natural world allows you to resist certain '
            '<a href="../../../../rule/general/supernatural/">supernatural</a> effects. '
            'You ignore temporary <a href="../../../../movement/difficult-terrain/">difficult terrain</a> '
            'created by magic and psionic abilities. Additionally, when you are '
            '<a href="../../../../movement/forced-movement/">force moved</a> by a magic or psionic ability, '
            'you can reduce the <a href="../../../../movement/forced-movement/">forced movement</a> '
            '<a href="../../../../rule/combat/distance/">distance</a> by 1.</p>',
            "Browse/feature/trait/human/cant-take-hold.md",
        )
        soup = BeautifulSoup(html, "html.parser")
        distance = soup.find("a", href="../../../../rule/combat/distance/")
        self.assertIsNotNone(distance)
        self.assertEqual(distance.get_text(), "距離")
        self.assertIn("強制移動的", soup.p.get_text())
        self.assertTrue(any(hit["record"] == "heroes.ancestries.human.trait.cant-take-hold.effect"
                            and hit["state"] == "translated" for hit in hits))
        exported = cat.translate_markdown(
            "Your connection to the natural world allows you to resist certain "
            "[supernatural](../../../rule/general/supernatural.md) effects. You ignore temporary "
            "[difficult terrain](../../../movement/difficult-terrain.md) created by magic and psionic abilities. "
            "Additionally, when you are [force moved](../../../movement/forced-movement.md) by a magic or psionic ability, "
            "you can reduce the [forced movement](../../../movement/forced-movement.md) "
            "[distance](../../../rule/combat/distance.md) by 1.",
            "Browse/feature/trait/human/cant-take-hold.md",
        )
        self.assertIn("[距離](../../../rule/combat/distance.md)", exported)
        self.assertNotIn("[distance]", exported)

    def test_human_composite_header_and_quick_build_use_approved_parts(self):
        records = [
            row("Signature Trait", "招牌特性", "ui", scope="ancestry:human", id="signature"),
            row("Detect the Supernatural", "偵測超常", "strings", scope="ancestry:human", id="detect"),
            row("You have 3 ancestry points to spend on the following traits.",
                "你有 3 點族裔點數，可以用來購買以下特性。", scope="ancestry:human", id="intro"),
            row("Quick Build: Perseverance, Staying Power.", "速選：堅持不懈、續航力",
                scope="ancestry:human", id="quick-build"),
        ]
        html, hits = Catalog({"records": records}).translate_html(
            "<h3>Signature Trait: Detect the Supernatural</h3>"
            "<p>You have 3 ancestry points to spend on the following traits. "
            "(<em>Quick Build:</em> Perseverance, Staying Power.)</p>",
            "Browse/ancestry/human.md",
        )
        soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(soup.h3.get_text(), "招牌特性：偵測超常")
        self.assertEqual(soup.p.get_text(), "你有 3 點族裔點數，可以用來購買以下特性。（速選：堅持不懈、續航力）")
        self.assertEqual(soup.p.em.get_text(), "速選：")
        self.assertTrue(all(x["state"] == "translated" for x in hits))

    def test_segment_headings_remain_headings_after_browser_html_parse(self):
        cat = Catalog({"records": [
            row("Purchased Human Traits", "自購人類特性", scope="ancestry:human", id="purchased"),
            row("Resist the Unnatural", "抵抗異常", scope="ancestry:human", id="resist"),
        ]})
        html, _ = cat.translate_html(
            '<h3 class="sc-trait__title">Purchased Human Traits</h3>'
            '<div><h3 class="sc-trait__title">Resist the Unnatural</h3><span>1 Point</span></div>',
            "Browse/ancestry/human.md",
        )
        # Reparse the serialized output, as the browser does. Paragraph children
        # in headings can otherwise make text-only translation assertions pass.
        parsed = BeautifulSoup(html, "lxml")
        self.assertEqual([h.get_text() for h in parsed.select("h3.sc-trait__title")],
                         ["自購人類特性", "抵抗異常"])
        self.assertFalse(parsed.select("h3 p"))
        self.assertEqual(parsed.select_one("h3 + span").get_text(), "1 Point")

    def test_human_card_flavor_and_scoped_cost_label(self):
        records = [
            row("Giving up is for other people.", "你絕不輕言放棄。", scope="ancestry:human"),
            row("1 Point", "1 費", "ui", scope="ancestry:human", id="human-cost"),
            row("Resist the Unnatural", "抵抗異常", scope="ancestry:human", id="human-trait-name"),
        ]
        html, _ = Catalog({"records": records}).translate_html(
            '<a><div class="sc-prev__tag">1 Point</div>'
            '<div class="sc-prev__flavor">Giving up is for other people.</div></a>',
            "Browse/feature/trait/human/index.md",
        )
        self.assertIn("1 費", html)
        self.assertIn("你絕不輕言放棄。", html)
        self.assertEqual(Catalog({"records": records}).lookup_label(
            "Resist the Unnatural", "Browse/feature/trait/human/resist-the-unnatural.md"
        )[0][0], "抵抗異常")
        other, _ = Catalog({"records": records}).translate_html(
            '<div class="sc-prev__tag">1 Point</div>', "Browse/feature/trait/dwarf/index.md"
        )
        self.assertIn("1 Point", other)

    def test_scope_and_level_priorities(self):
        self.assertEqual(classify("Browse/feature/ability/fury/level-1/back.md", {"scc": "mcdm.heroes.v1/feature/a"}), "P1")
        self.assertEqual(classify("Browse/feature/ability/fury/level-10/a.md", {}), "P2")
        self.assertEqual(classify("Browse/class/beastheart.md", {"scc": "mcdm.beastheart.v1/class/beastheart"}), "P4")
        self.assertEqual(classify("Read/heroes/for-the-director.md", {}), "P3")

    def test_export_uses_same_approved_prose_and_links(self):
        records = [row("You gain the Nature skill.", "你獲得自然技能。"), row("Nature", "自然", "glossary", id="term")]
        source = "> You gain the [Nature](nature/) skill.\n\n> 12 damage"
        result = Catalog({"records": records}).translate_markdown(source, "Browse/skill/nature.md")
        self.assertIn("> 你獲得[自然](nature/)技能。", result)
        self.assertIn("> 12 damage", result)

    def test_export_table_labels_match_visible_card_without_changing_numbers(self):
        records = [row("Melee", "近戰", "glossary")]
        source = "| **[Melee](melee/)** | 12 damage |\n|---|---|"
        result = Catalog({"records": records}).translate_markdown(source, "Browse/feature/ability/fury/level-1/brutal-slam.md")
        self.assertEqual(result, "| **[近戰](melee/)** | 12 damage |\n|---|---|")


if __name__ == "__main__":
    unittest.main()
