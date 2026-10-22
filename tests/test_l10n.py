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
