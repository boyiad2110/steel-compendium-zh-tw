"""Exercise orchestration and report compatibility without building the website."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("verification_runner", Path(__file__).resolve().parents[1] / "scripts/l10n/verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class VerificationTests(unittest.TestCase):
    def execute(self, outcomes):
        scratch = Path(__file__).resolve().parents[1] / ".work"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            root = Path(directory)
            (root / "tests").mkdir()
            calls = []

            def run(command, **kwargs):
                calls.append(command)
                self.assertEqual(kwargs["cwd"], root)
                self.assertEqual(kwargs["stderr"], subprocess.STDOUT)
                self.assertFalse(kwargs["check"])
                outcome = outcomes[len(calls) - 1]
                if isinstance(outcome, OSError):
                    raise outcome
                kwargs["stdout"].write("fixture diagnostic\n")
                return subprocess.CompletedProcess(command, outcome)

            with patch.object(verify, "ROOT", root), patch.object(verify.subprocess, "run", side_effect=run), contextlib.redirect_stdout(io.StringIO()):
                code = verify.main()
                rows = json.loads((root / "reports/verification.json").read_text())
                # A subsequent failure must overwrite the previous report.
                (root / "reports/verification.json").write_text("stale report")
                calls.clear()
                self.assertEqual(verify.main(), code)
                self.assertEqual(json.loads((root / "reports/verification.json").read_text())[0]["status"], rows[0]["status"])
            for row in rows:
                self.assertTrue({"step", "exitCode", "seconds"}.issubset(row))
                if row["status"] == "skipped":
                    self.assertIsNone(row["exitCode"])
                    self.assertIn("reason", row)
                    self.assertNotIn("log", row)
                else:
                    self.assertTrue((root / row["log"]).is_file())
                    if row["status"] == "failed":
                        self.assertTrue(row["error"])
            return code, rows, calls

    def test_success_runs_all_original_commands_in_order(self):
        code, rows, calls = self.execute([0, 0, 0, 0])
        self.assertEqual(code, 0)
        self.assertEqual([r["step"] for r in rows], ["python", "javascript", "build", "artifacts"])
        self.assertEqual([r["status"] for r in rows], ["passed"] * 4)
        self.assertEqual(calls[0][:4], [sys.executable, "-m", "unittest", "discover"])
        self.assertEqual(calls[1][:2], ["node", "--test"])
        self.assertEqual(calls[2], [sys.executable, "-m", "mkdocs", "build", "-f", "mkdocs.zh-TW.yml"])
        self.assertEqual(calls[3], [sys.executable, "scripts/l10n/check_build.py"])

    def test_either_or_both_suites_fail_but_both_always_run(self):
        for outcomes in ([7, 0], [0, 8], [7, 8]):
            with self.subTest(outcomes=outcomes):
                code, rows, calls = self.execute(outcomes)
                self.assertEqual(code, 1)
                self.assertEqual(len(calls), 2)
                self.assertEqual([r["exitCode"] for r in rows], [*outcomes, None, None])
                self.assertEqual([r["status"] for r in rows[2:]], ["skipped", "skipped"])

    def test_build_failure_skips_artifacts(self):
        code, rows, calls = self.execute([0, 0, 9])
        self.assertEqual((code, len(calls)), (1, 3))
        self.assertEqual(rows[2]["status"], "failed")
        self.assertEqual(rows[2]["exitCode"], 9)
        self.assertIn("fixture diagnostic", rows[2]["error"])
        self.assertEqual(rows[3]["status"], "skipped")

    def test_artifact_failure_is_not_skipped(self):
        code, rows, calls = self.execute([0, 0, 0, 10])
        self.assertEqual((code, len(calls)), (1, 4))
        self.assertEqual(rows[3]["status"], "failed")
        self.assertEqual(rows[3]["exitCode"], 10)

    def test_missing_executable_still_runs_other_suite_and_saves_error(self):
        code, rows, calls = self.execute([FileNotFoundError("missing python"), 0])
        self.assertEqual((code, len(calls)), (1, 2))
        self.assertIn("FileNotFoundError: missing python", rows[0]["error"])
        self.assertEqual(rows[1]["status"], "passed")

    def test_real_child_exit_and_stderr_are_retained_with_bounded_summary(self):
        scratch = Path(__file__).resolve().parents[1] / ".work"
        scratch.mkdir(exist_ok=True)
        real_run = subprocess.run
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            root = Path(directory)
            (root / "tests").mkdir()
            calls = []

            def child(command, **kwargs):
                calls.append(command)
                fixture = "import sys; print('x'*5000, flush=True); print('diagnostic 中文', file=sys.stderr); sys.exit(17)" if len(calls) == 1 else "print('suite passed')"
                return real_run([sys.executable, "-X", "utf8", "-c", fixture], **kwargs)

            with patch.object(verify, "ROOT", root), patch.object(verify.subprocess, "run", side_effect=child), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(verify.main(), 1)
            rows = json.loads((root / "reports/verification.json").read_text())
            self.assertEqual(len(calls), 2)
            self.assertEqual(rows[0]["exitCode"], 17)
            self.assertLessEqual(len(rows[0]["error"].encode("utf-8")), 4000)
            self.assertIn("diagnostic 中文", rows[0]["error"])
            self.assertGreater((root / rows[0]["log"]).stat().st_size, 5000)
            self.assertEqual([r["status"] for r in rows], ["failed", "passed", "skipped", "skipped"])


if __name__ == "__main__":
    unittest.main()
