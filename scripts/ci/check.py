"""Dependency-free PR scope classification and governance document checks."""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
DOC_FILES = frozenset({
    "AGENTS.md", "CLAUDE.md", "README.md", "README.zh-TW.md", ".impeccable.md",
    ".github/pull_request_template.md",
})
COMMAND_PATHS = (
    "requirements.lock.txt", "mkdocs.zh-TW.yml", "scripts/l10n/verify.py",
    "scripts/l10n/import_master.py", "scripts/l10n/refresh.py",
    "scripts/l10n/capture-master.mjs", ".github/workflows/zh-tw.yml",
    ".github/workflows/ci.yml",
)


def is_governance(path):
    parts = PurePosixPath(path).parts
    if not parts or path.startswith("/") or "\\" in path or ".." in parts:
        return False
    return path in DOC_FILES or (parts[0] == ".repo-docs" and path.endswith(".md"))


def classify(paths, event="pull_request"):
    paths = sorted(set(paths))
    mode = "docs" if event == "pull_request" and paths and all(map(is_governance, paths)) else "full"
    return {"mode": mode, "reason": "governance-only" if mode == "docs" else "full-required",
            "files": paths}


def github_json(route):
    request = Request(os.environ.get("GITHUB_API_URL", "https://api.github.com") + route,
                      headers={"Accept": "application/vnd.github+json",
                               "Authorization": "Bearer " + os.environ["GH_TOKEN"],
                               "X-GitHub-Api-Version": "2022-11-28"})
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def pr_scope(event, api=github_json):
    """Use the entire PR, paginate, include rename sources, reject incomplete/racy reads."""
    try:
        pr = event["pull_request"]
        route = f'/repos/{event["repository"]["full_name"]}/pulls/{pr["number"]}'
        before = api(route)
        expected = (pr["base"]["sha"], pr["head"]["sha"])
        if (before["base"]["sha"], before["head"]["sha"]) != expected:
            raise ValueError("PR changed since event")
        count = before["changed_files"]
        # GitHub's files endpoint is capped at 3,000 files. Never infer docs-only at the cap.
        if not 0 < count < 3000:
            raise ValueError("PR file count is empty or exceeds reliable API range")
        files = []
        for page in range(1, (count + 99) // 100 + 1):
            files.extend(api(f"{route}/files?per_page=100&page={page}"))
        after = api(route)
        if len(files) != count or after["changed_files"] != count or (
                after["base"]["sha"], after["head"]["sha"]) != expected:
            raise ValueError("PR file list is incomplete or changed")
        if len({item["filename"] for item in files}) != count:
            raise ValueError("Duplicate PR files")
        paths = []
        for item in files:
            paths.append(item["filename"])
            if item.get("status") == "renamed":
                paths.append(item["previous_filename"])
        result = classify(paths)
        result.update({"base": expected[0], "head": expected[1]})
        return result
    except (KeyError, ValueError, TypeError, OSError) as error:
        # No API body/credentials in logs. A failed classification cannot skip the full build.
        return {"mode": "full", "reason": "unreliable-pr-diff:" + type(error).__name__, "files": []}


def markdown_errors(path, root):
    errors = []
    text = path.read_text(encoding="utf-8")
    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f"{path.relative_to(root)}:{number}: trailing whitespace")
    # Code samples are not authored links. Reference-style definitions are checked as well.
    body = re.sub(r"^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", text,
                  flags=re.MULTILINE | re.DOTALL)
    links = re.findall(r"!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", body)
    links += re.findall(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", body, flags=re.MULTILINE)
    checked = 0
    for link in links:
        link = link.removeprefix("<").removesuffix(">")
        url = urlsplit(link)
        if url.scheme or url.netloc or not url.path:
            continue
        checked += 1
        target = unquote(url.path)
        destination = ((root / target.lstrip("/")) if target.startswith("/") else path.parent / target).resolve()
        if not destination.is_relative_to(root.resolve()) or not destination.exists():
            errors.append(f"{path.relative_to(root)}: invalid local link {link}")
    if path.parent == root / ".repo-docs/batches" and path.name not in {"README.md", "_template.md"}:
        for section in ("## 範圍與版本", "## 狀態", "## 驗證", "## 使用者驗收"):
            if section not in text:
                errors.append(f"{path.relative_to(root)}: missing batch section {section}")
    return errors, checked


def check_docs(root=ROOT, base=None):
    files = [root / name for name in sorted(DOC_FILES)]
    files += [p for p in (root / ".repo-docs").rglob("*.md")
              if "upstream" not in p.relative_to(root / ".repo-docs").parts]
    errors, links = [], 0
    for path in files:
        if not path.is_file():
            errors.append("Missing governance file: " + str(path.relative_to(root)))
            continue
        found, count = markdown_errors(path, root)
        errors.extend(found)
        links += count
    for name in COMMAND_PATHS:
        if not (root / name).is_file():
            errors.append("Missing command/config path: " + name)
    if (root / "CLAUDE.md").is_file() and (root / "CLAUDE.md").read_text(encoding="utf-8").strip() != "@AGENTS.md":
        errors.append("CLAUDE.md must reference AGENTS.md")
    command = ["git", "-c", "core.safecrlf=false", "diff", "--check"]
    if base:
        command.append(base)
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        errors.append("git diff --check failed: " + result.stdout + result.stderr)
    return {"documents": len(files), "localLinks": links, "errors": errors}


def save_report(name, result):
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / name).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    scope = sub.add_parser("classify")
    scope.add_argument("--files", nargs="+")
    scope.add_argument("--event", default=os.environ.get("GITHUB_EVENT_NAME", "pull_request"))
    docs = sub.add_parser("docs")
    docs.add_argument("--base", default=os.environ.get("CI_DIFF_BASE") or None)
    args = parser.parse_args()
    if args.command == "docs":
        report = check_docs(base=args.base)
        save_report("ci-docs.json", report)
        return int(bool(report["errors"]))
    if args.files is not None or args.event != "pull_request":
        result = classify(args.files or [], args.event)
    else:
        try:
            event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
            result = pr_scope(event)
        except (KeyError, ValueError, OSError):
            result = {"mode": "full", "reason": "missing-event-context", "files": []}
    save_report("ci-scope.json", result)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f'mode={result["mode"]}\n')
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write(f'## CI validation\n\nMode: **{result["mode"]}**\n\nReason: `{result["reason"]}`\n')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
