"""B02 regression cases from the generated Devil source (never rewritten)."""
import sys
import unittest
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/l10n"))
from core import Catalog, load_catalog


class DevilLocalizationTests(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog(load_catalog())

    def render(self, path):
        source = (ROOT / "docs" / path).read_text(encoding="utf-8")
        if source.startswith("---"):
            source = source.split("---", 2)[2]
        return markdown.markdown(source, extensions=["attr_list", "md_in_html"])

    def test_main_introduction_traits_links_and_unapproved_story(self):
        source = self.render("Browse/ancestry/devil.md")
        translated, hits = self.catalog.translate_html(source, "Browse/ancestry/devil.md")
        soup = BeautifulSoup(translated, "lxml")
        for i in range(1, 6):
            self.assertIsNotNone(soup.select_one(f'[data-sc-l10n="heroes.ancestries.devil.description.{i}"]'))
        for node in soup.select(".sc-trait p,.sc-trait h3,.sc-head__right-primary"):
            self.assertTrue(node.get("data-sc-l10n"), node.get_text())
        self.assertFalse([h for h in hits if h["state"] != "translated"])
        # De-duplication of identical repeated links is intentional; no destination lost.
        self.assertEqual({a["href"] for a in soup.select("a[href]")},
                         {a["href"] for a in BeautifulSoup(source, "lxml").select("a[href]")})
        self.assertIn("Adelard scuttled across the floor", soup.get_text())
        self.assertIn("On Devils", soup.get_text())
        self.assertFalse(soup.select("h3 > p"))
        self.assertIn("速選：獸腿、威嚴犄角。", soup.get_text())
        # Actual MkDocs output rewrites self-links to ./, unlike raw Markdown.
        actual, actual_hits = self.catalog.translate_html(source.replace('href="devil.md"', 'href="./"'), "Browse/ancestry/devil.md")
        self.assertIn("你珍愛的雙角", actual)
        self.assertFalse([h for h in actual_hits if h["state"] != "translated"])

    def test_all_independent_pages_and_exports_share_the_mapping(self):
        for path in (ROOT / "docs/Browse/feature/trait/devil").glob("*.md"):
            uri = path.relative_to(ROOT / "docs").as_posix()
            with self.subTest(page=uri):
                original = self.render(uri)
                translated, hits = self.catalog.translate_html(original, uri)
                self.assertFalse([h for h in hits if h["state"] != "translated"])
                soup = BeautifulSoup(translated, "lxml")
                for node in soup.select(".sc-trait p,.sc-trait h3,.sc-head__right-primary"):
                    self.assertTrue(node.get("data-sc-l10n"), node.get_text())
                if path.name == "silver-tongue.md":
                    record = next(r for r in self.catalog.data["records"] if r["id"] == "heroes.ancestries.devil.signature.silver-tongue.effect")
                    self.assertIn("第 9 章", soup.get_text())
                    self.assertIn("第 11 章", soup.get_text())
                    self.assertIn("第 9 章", self.catalog.translate_markdown(record["source"], uri))

    def test_reading_chapter_relative_reference_is_preserved(self):
        source = (ROOT / "docs/Read/heroes/ancestries.md").read_text(encoding="utf-8")
        devil = source.split('\n## Devil {', 1)[1].split('\n## Dragon Knight {', 1)[0]
        translated, hits = self.catalog.translate_html(markdown.markdown(devil), "Read/heroes/ancestries.md")
        soup = BeautifulSoup(translated, "lxml")
        node = soup.select_one('[data-sc-l10n="heroes.ancestries.devil.signature.silver-tongue.effect"]')
        self.assertIsNotNone(node)
        self.assertIsNotNone(node.select_one('a[href="../tests/"]'))
        self.assertEqual(node.select_one('a[href="../tests/"]').get_text(), "考驗")
        self.assertFalse([h for h in hits if h["state"] != "translated"])

    def test_typography_adaptation_does_not_accept_changed_prose(self):
        source = self.render("Browse/ancestry/devil.md")
        changed = source.replace("red or blue skin", "green skin")
        translated, _ = self.catalog.translate_html(changed, "Browse/ancestry/devil.md")
        self.assertIn("green skin", translated)
        outside, _ = self.catalog.translate_html(source, "Browse/ancestry/dwarf.md")
        self.assertIn("hellmark", outside)

    def test_direct_interpersonal_choice_uses_all_approved_table_rows(self):
        for path in (ROOT / "docs/Browse/skill/interpersonal").glob("*.md"):
            uri = path.relative_to(ROOT / "docs").as_posix()
            with self.subTest(page=uri):
                translated, hits = self.catalog.translate_html(self.render(uri), uri)
                soup = BeautifulSoup(translated, "lxml")
                self.assertFalse([h for h in hits if h["state"] != "translated"])
                for node in soup.select("p,.sc-card__blurb"):
                    self.assertTrue(node.get("data-sc-l10n") or node.find_parent(attrs={"data-sc-l10n": True}), node.get_text())


if __name__ == "__main__":
    unittest.main()
