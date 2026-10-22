"""Run both test suites, then build/check artifacts only if prerequisites pass."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    steps = [
        ("python", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]),
        ("javascript", ["node", "--test", *[str(p.relative_to(ROOT)) for p in sorted((ROOT / "tests").glob("*.test.js"))]]),
        ("build", [sys.executable, "-m", "mkdocs", "build", "-f", "mkdocs.zh-TW.yml"]),
        ("artifacts", [sys.executable, "scripts/l10n/check_build.py"]),
    ]
    results = []
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    for name, command in steps:
        blockers = [row["step"] for row in results if row["status"] != "passed"]
        if name in {"build", "artifacts"} and blockers:
            results.append({"step": name, "status": "skipped", "exitCode": None,
                            "seconds": 0, "reason": "Blocked by: " + ", ".join(blockers)})
            continue
        start = time.monotonic()
        log_path = reports / f"verification-{name}.log"
        print(f"\n[{name}] running; log: {log_path.relative_to(ROOT)}", flush=True)
        error_text = None
        with log_path.open("w", encoding="utf-8") as log:
            try:
                result = subprocess.run(command, cwd=ROOT, check=False,
                                        stdout=log, stderr=subprocess.STDOUT,
                                        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
                code = result.returncode
            except OSError as error:
                error_text = f"{type(error).__name__}: {error}"
                log.write(error_text + "\n")
                code = 1
        row = {"step": name, "status": "passed" if code == 0 else "failed",
               "exitCode": code, "seconds": round(time.monotonic() - start, 2),
               "log": log_path.relative_to(ROOT).as_posix()}
        if code != 0:
            # Bound console/JSON output; the complete merged stdout/stderr stays
            # in reports and is uploaded by the existing CI artifact step.
            with log_path.open("rb") as log:
                log.seek(max(0, log_path.stat().st_size - 4000))
                row["error"] = error_text or log.read().decode("utf-8", errors="replace").strip() or f"Command exited with code {code}"
        results.append(row)
        print(f"[{name}] {row['status']} (exit {code})", flush=True)
    (reports / "verification.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return int(any(row["status"] == "failed" for row in results))


if __name__ == "__main__":
    raise SystemExit(main())
