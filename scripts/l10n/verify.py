"""One verification entrypoint: run every step and report actual exit codes."""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    steps = [
        ("python", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_l10n.py"]),
        ("javascript", ["node", "--test", *[str(p.relative_to(ROOT)) for p in sorted((ROOT / "tests").glob("*.test.js"))]]),
        ("build", [sys.executable, "-m", "mkdocs", "build", "-f", "mkdocs.zh-TW.yml"]),
        ("artifacts", [sys.executable, "scripts/l10n/check_build.py"]),
    ]
    results = []
    for name, command in steps:
        start = time.monotonic()
        print(f"\n[{name}]", flush=True)
        try:
            result = subprocess.run(command, cwd=ROOT, check=False)
            code = result.returncode
        except OSError as error:
            print(error)
            code = 1
        results.append({"step": name, "exitCode": code, "seconds": round(time.monotonic() - start, 2)})
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/verification.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return int(any(row["exitCode"] for row in results))


if __name__ == "__main__":
    raise SystemExit(main())
