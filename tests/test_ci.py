"""CI classification must never mistake runtime changes or incomplete diffs for docs."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/ci"))
from check import classify, markdown_errors, pr_scope


def event():
    return {"repository": {"full_name": "owner/site"},
            "pull_request": {"number": 1, "base": {"sha": "base"}, "head": {"sha": "head"}}}


class FakeAPI:
    def __init__(self, files):
        self.files = files
        self.reads = 0
        self.metadata = {"base": {"sha": "base"}, "head": {"sha": "head"}, "changed_files": len(files)}
        self.after = copy.deepcopy(self.metadata)

    def __call__(self, route):
        if "/files?" not in route:
            self.reads += 1
            return copy.deepcopy(self.metadata if self.reads == 1 else self.after)
        page = int(route.rsplit("=", 1)[1])
        return self.files[(page - 1) * 100:page * 100]


class ScopeTests(unittest.TestCase):
    def test_governance_whitelist(self):
        self.assertEqual(classify(["README.md", "AGENTS.md", ".repo-docs/batches/CI-01.md",
                                   ".github/pull_request_template.md"])["mode"], "docs")

    def test_runtime_unknown_and_mixed_paths_require_full(self):
        for path in ["docs/index.md", "static_content/docs/pins.md", "l10n/catalog.json",
                     "mkdocs.zh-TW.yml", ".github/workflows/zh-tw.yml", "tests/test_ci.py",
                     "scripts/ci/check.py", "requirements.lock.txt", "new-file.txt",
                     ".repo-docs/config.json", ".repo-docs/../docs/index.md", "/README.md"]:
            with self.subTest(path=path):
                self.assertEqual(classify(["README.md", path])["mode"], "full")

    def test_empty_and_manual_execution_require_full(self):
        self.assertEqual(classify([])["mode"], "full")
        self.assertEqual(classify(["README.md"], "workflow_dispatch")["mode"], "full")

    def test_entire_pr_not_last_document_commit(self):
        api = FakeAPI([{"filename": "docs/javascripts/l10n.js"},
                       {"filename": ".repo-docs/batches/B01.md"}])
        self.assertEqual(pr_scope(event(), api)["mode"], "full")

    def test_all_pages_are_read(self):
        api = FakeAPI([{"filename": f".repo-docs/page-{i}.md"} for i in range(100)] +
                      [{"filename": "docs/index.md"}])
        self.assertEqual(pr_scope(event(), api)["mode"], "full")

    def test_doc_only_pr_can_use_fast_path(self):
        result = pr_scope(event(), FakeAPI([{"filename": "README.md", "status": "modified"}]))
        self.assertEqual(result["mode"], "docs")
        self.assertEqual(result["head"], "head")

    def test_renamed_runtime_file_is_not_document_only(self):
        files = [{"filename": ".repo-docs/old.md", "status": "renamed",
                  "previous_filename": "docs/index.md"}]
        self.assertEqual(pr_scope(event(), FakeAPI(files))["mode"], "full")

    def test_deleted_runtime_file_still_requires_full(self):
        files = [{"filename": "docs/index.md", "status": "removed"}]
        self.assertEqual(pr_scope(event(), FakeAPI(files))["mode"], "full")

    def test_incomplete_duplicate_or_oversized_file_lists_require_full(self):
        incomplete = FakeAPI([{"filename": "README.md"}])
        incomplete.metadata["changed_files"] = incomplete.after["changed_files"] = 2
        duplicate = FakeAPI([{"filename": "README.md"}, {"filename": "README.md"}])
        oversized = FakeAPI([])
        oversized.metadata["changed_files"] = 3000
        for api in [incomplete, duplicate, oversized]:
            self.assertEqual(pr_scope(event(), api)["mode"], "full")

    def test_base_head_or_count_changes_during_read_require_full(self):
        for key in ["base", "head", "changed_files"]:
            api = FakeAPI([{"filename": "README.md"}])
            api.after[key] = 2 if key == "changed_files" else {"sha": "new"}
            self.assertEqual(pr_scope(event(), api)["mode"], "full")
        api = FakeAPI([{"filename": "README.md"}])
        api.metadata["head"]["sha"] = "new"
        self.assertEqual(pr_scope(event(), api)["mode"], "full")

    def test_api_failures_and_missing_context_require_full(self):
        def failed_api(route):
            raise OSError("network unavailable")
        self.assertEqual(pr_scope(event(), failed_api)["mode"], "full")
        self.assertEqual(pr_scope({}, failed_api)["mode"], "full")


class DocumentTests(unittest.TestCase):
    def setUp(self):
        # Keep fixtures inside the repo on restricted Windows hosts as well as CI.
        self.folder = Path(__file__).resolve().parents[1] / ".work"
        self.folder.mkdir(exist_ok=True)

    def test_links_images_references_and_code_fences(self):
        with tempfile.TemporaryDirectory(dir=self.folder) as folder:
            root = Path(folder)
            (root / "target file.md").write_text("# Target\n", encoding="utf-8")
            doc = root / "README.md"
            doc.write_text('[local](target%20file.md#target) ![image](<target file.md>)\n'
                           '[ref]: target%20file.md\n[web](https://example.com/)\n'
                           '```md\n[example](missing-example.md)\n```\n', encoding="utf-8")
            errors, count = markdown_errors(doc, root)
            self.assertEqual(errors, [])
            self.assertEqual(count, 3)

    def test_broken_or_outside_links_and_whitespace_fail(self):
        with tempfile.TemporaryDirectory(dir=self.folder) as folder:
            root = Path(folder)
            doc = root / "README.md"
            doc.write_text('[bad](missing.md) [outside](../outside.md) \n', encoding="utf-8")
            self.assertEqual(len(markdown_errors(doc, root)[0]), 3)

    def test_batch_sections_are_required(self):
        with tempfile.TemporaryDirectory(dir=self.folder) as folder:
            root = Path(folder)
            batch = root / ".repo-docs/batches/B99.md"
            batch.parent.mkdir(parents=True)
            batch.write_text("# Empty batch\n", encoding="utf-8")
            self.assertEqual(len(markdown_errors(batch, root)[0]), 4)


if __name__ == "__main__":
    unittest.main()
