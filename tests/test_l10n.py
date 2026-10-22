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
